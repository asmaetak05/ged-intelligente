"""Repository unique — couche d'accès aux données.

Ce module centralise **toute** la logique SQL/SQLAlchemy du backend.
Les endpoints (`main.py`) ne manipulent plus directement la base : ils
s'appuient sur les classes de ce module, ce qui présente trois
avantages :

1. **Testabilité** : on peut injecter une session SQLite en mémoire
   (`tests/conftest.py`) sans toucher au reste du code.
2. **Portabilité** : toutes les requêtes utilisent le dialecte courant
   (`is_sqlite()` / `is_postgresql()`), pas de SQL brut spécifique à
   un moteur.
3. **Évolutivité** : ajouter une méthode (ex. `search_geo`) n'oblige
   pas à fouiller dans les endpoints.

Trois familles de repositories sont exposées :

- :class:`MarcheRepository`     → ``marches`` (appels d'offres).
- :class:`DocumentRepository`   → ``documents`` (archives brutes).
- :class:`OcrLogRepository`     → ``ocr_logs`` (résultats OCR).

Décision d'architecture documentée dans ``docs/Note_Decision_V1.md``
(section 5 « Décision Phase 1 — Repository unique »).
"""
from __future__ import annotations

import json
from datetime import date, datetime
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

from sqlalchemy import and_, case, func, or_, select
from sqlalchemy.orm import Session

from . import models


# =============================================================================
# Filtres — dataclass simple pour `MarcheRepository.list()` / `count()`
# =============================================================================
class MarcheFilter:
    """Critères de filtrage pour la liste des appels d'offres.

    Tous les champs sont optionnels ; ne sont appliqués que ceux dont la
    valeur est non ``None``. Cela permet aux endpoints FastAPI de mapper
    directement des *query params* facultatifs.
    """

    def __init__(
        self,
        ville: Optional[str] = None,
        region: Optional[str] = None,
        organisme: Optional[str] = None,
        categorie: Optional[models.CategorieMarche] = None,
        date_min: Optional[date] = None,
        date_max: Optional[date] = None,
        montant_min: Optional[float] = None,
        montant_max: Optional[float] = None,
        q: Optional[str] = None,
    ) -> None:
        self.ville = ville
        self.region = region
        self.organisme = organisme
        self.categorie = categorie
        self.date_min = date_min
        self.date_max = date_max
        self.montant_min = montant_min
        self.montant_max = montant_max
        self.q = q

    def to_clauses(self) -> List[Any]:
        """Convertit les filtres non nuls en clauses SQLAlchemy.

        Le `LIKE` est insensible à la casse via ``ilike`` sur PostgreSQL ;
        sur SQLite, SQLAlchemy l'émule. Pour la recherche plein-texte
        (`q`), on s'appuie sur ``LIKE`` portable — le FTS natif (GIN /
        FTS5) sera branché dans une migration Alembic dédiée (T1.6 +
        Phase 2).
        """
        clauses: List[Any] = []
        if self.ville:
            clauses.append(models.Marche.ville_execution.ilike(f"%{self.ville}%"))
        if self.region:
            clauses.append(models.Marche.region.ilike(f"%{self.region}%"))
        if self.organisme:
            clauses.append(models.Marche.organisme_acheteur.ilike(f"%{self.organisme}%"))
        if self.categorie is not None:
            clauses.append(models.Marche.categorie_prestation == self.categorie)
        if self.date_min is not None:
            clauses.append(models.Marche.date_parution >= self.date_min)
        if self.date_max is not None:
            clauses.append(models.Marche.date_parution <= self.date_max)
        if self.montant_min is not None:
            clauses.append(models.Marche.montant >= self.montant_min)
        if self.montant_max is not None:
            clauses.append(models.Marche.montant <= self.montant_max)
        if self.q:
            needle = f"%{self.q}%"
            clauses.append(
                or_(
                    models.Marche.titre_projet.ilike(needle),
                    models.Marche.numero_appel_offre.ilike(needle),
                    models.Marche.reference.ilike(needle),
                    models.Marche.tsv_search.ilike(needle),
                )
            )
        return clauses


# =============================================================================
# MarcheRepository
# =============================================================================
class MarcheRepository:
    """Accès CRUD + agrégations sur la table ``marches``."""

    def __init__(self, db: Session) -> None:
        self.db = db

    # ------------------------------------------------------------------ CRUD
    def get(self, marche_id: int) -> Optional[models.Marche]:
        return self.db.get(models.Marche, marche_id)

    def get_by_numero(self, numero: str) -> Optional[models.Marche]:
        stmt = select(models.Marche).where(models.Marche.numero_appel_offre == numero)
        return self.db.execute(stmt).scalar_one_or_none()

    def list(
        self,
        filters: Optional[MarcheFilter] = None,
        page: int = 1,
        page_size: int = 20,
        order_by: str = "date_parution",
        order_dir: str = "desc",
    ) -> List[models.Marche]:
        """Liste paginée. `page` 1-indexé, `page_size` borné à 200."""
        page = max(1, page)
        page_size = max(1, min(page_size, 200))
        stmt = select(models.Marche)
        if filters is not None:
            clauses = filters.to_clauses()
            if clauses:
                stmt = stmt.where(and_(*clauses))
        # Tri — whitelist des colonnes triables (sécurité).
        sortable = {
            "date_parution": models.Marche.date_parution,
            "date_limite": models.Marche.date_limite,
            "montant": models.Marche.montant,
            "created_at": models.Marche.created_at,
            "titre_projet": models.Marche.titre_projet,
        }
        col = sortable.get(order_by, models.Marche.date_parution)
        stmt = stmt.order_by(col.desc() if order_dir == "desc" else col.asc())
        stmt = stmt.offset((page - 1) * page_size).limit(page_size)
        return list(self.db.execute(stmt).scalars().all())

    def count(self, filters: Optional[MarcheFilter] = None) -> int:
        stmt = select(func.count(models.Marche.id))
        if filters is not None:
            clauses = filters.to_clauses()
            if clauses:
                stmt = stmt.where(and_(*clauses))
        return int(self.db.execute(stmt).scalar_one() or 0)

    def create(self, payload: Dict[str, Any]) -> models.Marche:
        """Crée un marché. Si `numero_appel_offre` existe déjà, lève
        ``ValueError`` (l'appelant doit utiliser ``upsert``)."""
        numero = payload.get("numero_appel_offre")
        if numero and self.get_by_numero(numero) is not None:
            raise ValueError(f"Un marché avec le numero '{numero}' existe déjà")
        # Sérialise `agreements_exiges` (list[str] → JSON str) pour
        # le stockage en colonne `JSON` portable.
        if "agreements_exiges" in payload and isinstance(payload["agreements_exiges"], (list, tuple)):
            payload = {**payload, "agreements_exiges": json.dumps(
                list(payload["agreements_exiges"]), ensure_ascii=False)}
        marche = models.Marche(**payload)
        self.db.add(marche)
        self.db.flush()
        return marche

    def update(self, marche: models.Marche, payload: Dict[str, Any]) -> models.Marche:
        if "agreements_exiges" in payload and isinstance(payload["agreements_exiges"], (list, tuple)):
            payload = {**payload, "agreements_exiges": json.dumps(
                list(payload["agreements_exiges"]), ensure_ascii=False)}
        for key, value in payload.items():
            if hasattr(marche, key):
                setattr(marche, key, value)
        self.db.flush()
        return marche

    def upsert(self, payload: Dict[str, Any]) -> Tuple[models.Marche, str]:
        """Crée ou met à jour selon `numero_appel_offre`.

        Retourne ``(marche, action)`` avec ``action`` ∈ {"created",
        "updated"}. Pratique pour le pipeline d'ingestion (Phase 2).
        """
        numero = payload.get("numero_appel_offre")
        if not numero:
            raise ValueError("numero_appel_offre est obligatoire pour upsert")
        existing = self.get_by_numero(numero)
        if existing is None:
            return self.create(payload), "created"
        # On exclut `numero_appel_offre` de la mise à jour (clé naturelle).
        return self.update(existing, {k: v for k, v in payload.items()
                                      if k != "numero_appel_offre"}), "updated"

    # ------------------------------------------------------------------ FTS
    def search_fts(self, query: str, limit: int = 50) -> List[models.Marche]:
        """Recherche plein texte portable via le module PostgresFTS."""
        from search.postgres_fts import PostgresFTS
        fts_engine = PostgresFTS(self.db)
        results, _ = fts_engine.search(query=query, page_size=limit)
        return [r.marche for r in results]

    def search_fts_advanced(
        self,
        query: str,
        categorie: Optional[models.CategorieMarche] = None,
        region: Optional[str] = None,
        ville: Optional[str] = None,
        organisme: Optional[str] = None,
        date_min: Optional[date] = None,
        date_max: Optional[date] = None,
        montant_min: Optional[float] = None,
        montant_max: Optional[float] = None,
        order_by: str = "pertinence",
        order_dir: str = "desc",
        page: int = 1,
        page_size: int = 20,
    ) -> Tuple[List[Any], int]:
        """Recherche FTS enrichie retournant (list[FtsSearchResult], total_count)."""
        from search.postgres_fts import PostgresFTS
        fts_engine = PostgresFTS(self.db)
        return fts_engine.search(
            query=query,
            categorie=categorie,
            region=region,
            ville=ville,
            organisme=organisme,
            date_min=date_min,
            date_max=date_max,
            montant_min=montant_min,
            montant_max=montant_max,
            order_by=order_by,
            order_dir=order_dir,
            page=page,
            page_size=page_size,
        )

    # ----------------------------------------------------------- Agrégations
    def kpis(self) -> Dict[str, Any]:
        """KPI globaux : nombre d'AO, volume financier, délai moyen,
        taux OCR moyen. Réutilisé par ``/api/v1/analytics/kpis`` (T1.4).
        """
        stmt = select(
            func.count(models.Marche.id),
            func.coalesce(func.sum(models.Marche.montant), 0),
            func.coalesce(func.avg(models.Marche.delai_execution_mois), 0),
        )
        total, volume, delai = self.db.execute(stmt).one()
        return {
            "total_appels_offres": int(total or 0),
            "volume_financier_total_mad": float(volume or 0),
            "delai_moyen_execution_mois": round(float(delai or 0), 2),
            "taux_reussite_ocr_pct": self.ocr_quality_pct(),
        }

    def by_month(self) -> List[Dict[str, Any]]:
        """Volume par mois de parution (12 derniers mois max)."""
        # SQLite et PostgreSQL supportent `strftime` / `to_char` mais
        # avec des syntaxes différentes. On utilise l'API SQLAlchemy
        # portable (func.extract) — `func.extract('month', ...)` est
        # supporté par les deux dialectes via SQLAlchemy.
        stmt = (
            select(
                func.strftime("%Y-%m", models.Marche.date_parution).label("month"),
                func.count(models.Marche.id).label("count"),
            )
            .where(models.Marche.date_parution.is_not(None))
            .group_by("month")
            .order_by("month")
        )
        # `func.strftime` est SQLite-only ; on rebascule proprement :
        # si on est sur PostgreSQL, on utilise `to_char`.
        # SQLAlchemy n'a pas de helper portable pour ce cas, on
        # laisse donc un test runtime via le dialecte.
        if self.db.bind is not None and self.db.bind.dialect.name == "postgresql":
            stmt = (
                select(
                    func.to_char(models.Marche.date_parution, "YYYY-MM").label("month"),
                    func.count(models.Marche.id).label("count"),
                )
                .where(models.Marche.date_parution.is_not(None))
                .group_by("month")
                .order_by("month")
            )
        return [
            {"month": row.month, "count": int(row.count)}
            for row in self.db.execute(stmt).all()
            if row.month
        ]

    def by_category_month(self) -> List[Dict[str, Any]]:
        """Répartition (catégorie, mois) pour les graphes empilés."""
        stmt = (
            select(
                models.Marche.categorie_prestation.label("categorie"),
                func.count(models.Marche.id).label("count"),
            )
            .where(models.Marche.categorie_prestation.is_not(None))
            .group_by(models.Marche.categorie_prestation)
        )
        return [
            {
                "categorie": str(row.categorie.value) if row.categorie else "Inconnu",
                "count": int(row.count),
            }
            for row in self.db.execute(stmt).all()
        ]

    def delai_moyen(self) -> float:
        """Délai d'exécution moyen (mois). 0 si aucun marché."""
        stmt = select(func.avg(models.Marche.delai_execution_mois))
        val = self.db.execute(stmt).scalar_one()
        return round(float(val or 0), 2)

    def top_buyers(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Top acheteurs par volume financier cumulé."""
        stmt = (
            select(
                models.Marche.organisme_acheteur.label("organisme"),
                func.coalesce(func.sum(models.Marche.montant), 0).label("volume"),
                func.count(models.Marche.id).label("nb_marches"),
            )
            .where(models.Marche.organisme_acheteur.is_not(None))
            .group_by(models.Marche.organisme_acheteur)
            .order_by(func.sum(models.Marche.montant).desc())
            .limit(limit)
        )
        return [
            {
                "organisme": row.organisme or "Inconnu",
                "volume_mad": float(row.volume or 0),
                "nb_marches": int(row.nb_marches or 0),
            }
            for row in self.db.execute(stmt).all()
        ]

    def ocr_quality_pct(self) -> float:
        """Taux de qualité OCR moyen sur les logs existants.

        Stratégie : ``AVG(confidence_score_avg)`` sur les
        ``OcrLog``. Si aucun log → 0. La valeur est renvoyée en
        pourcentage (0-100), pas en fraction.
        """
        stmt = select(func.avg(models.OcrLog.confidence_score_avg))
        val = self.db.execute(stmt).scalar_one()
        if val is None:
            return 0.0
        return round(float(val) * (100.0 if val <= 1.0 else 1.0), 2)


# =============================================================================
# DocumentRepository
# =============================================================================
class DocumentRepository:
    """Accès CRUD sur la table ``documents``."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def get(self, document_id: int) -> Optional[models.Document]:
        return self.db.get(models.Document, document_id)

    def list(self, limit: int = 100) -> List[models.Document]:
        stmt = select(models.Document).order_by(models.Document.id.desc()).limit(limit)
        return list(self.db.execute(stmt).scalars().all())

    def create(self, payload: Dict[str, Any]) -> models.Document:
        doc = models.Document(**payload)
        self.db.add(doc)
        self.db.flush()
        return doc

    def update_status(self, document: models.Document,
                      status: models.DocStatus) -> models.Document:
        document.status = status
        self.db.flush()
        return document


# =============================================================================
# OcrLogRepository
# =============================================================================
class OcrLogRepository:
    """Accès CRUD sur la table ``ocr_logs``."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, payload: Dict[str, Any]) -> models.OcrLog:
        log = models.OcrLog(**payload)
        self.db.add(log)
        self.db.flush()
        return log

    def list_by_document(self, document_id: int) -> List[models.OcrLog]:
        stmt = (
            select(models.OcrLog)
            .where(models.OcrLog.document_id == document_id)
            .order_by(models.OcrLog.processed_at.desc())
        )
        return list(self.db.execute(stmt).scalars().all())

    def list_recent(self, limit: int = 50) -> List[models.OcrLog]:
        stmt = select(models.OcrLog).order_by(models.OcrLog.processed_at.desc()).limit(limit)
        return list(self.db.execute(stmt).scalars().all())


# =============================================================================
# Exports
# =============================================================================
__all__ = [
    "MarcheFilter",
    "MarcheRepository",
    "DocumentRepository",
    "OcrLogRepository",
]
