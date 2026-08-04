"""Moteur de recherche plein texte unifié (FTS) pour PostgreSQL & SQLite.

Fournit :
1. Détection automatique du dialecte SQL (PostgreSQL FTS natif vs SQLite ILIKE).
2. Requêtes FTS avancées (ranking ts_rank, snippets ts_headline, opérateurs booléens).
3. Génération d'extraits avec surlignage (<mark>) compatible DOMPurify côté frontend.
4. Tri configurable (pertinence, date, montant).
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date
from typing import Any, Dict, List, Optional, Sequence, Tuple

from sqlalchemy import and_, desc, func, or_, select, text
from sqlalchemy.orm import Session

from backend import models


@dataclass
class FtsSearchResult:
    """Résultat enrichi d'une recherche FTS."""
    marche: models.Marche
    score: float
    highlight: str
    matched_fields: List[str]


class PostgresFTS:
    """Moteur FTS unifié supportant PostgreSQL et SQLite en fallback."""

    def __init__(self, db: Session) -> None:
        self.db = db
        self.is_postgres = bool(
            db.bind is not None and db.bind.dialect.name == "postgresql"
        )

    @staticmethod
    def sanitize_query(query: str) -> str:
        """Nettoie et normalise la chaîne de recherche."""
        if not query:
            return ""
        # Supprimer les caractères dangereux pour tsquery
        cleaned = re.sub(r"[^\w\s\-\'\"\./]", " ", query, flags=re.UNICODE)
        return cleaned.strip()

    @staticmethod
    def build_tsquery_string(query: str) -> str:
        """Construit une chaîne de requête tsquery avec support des préfixes (:*)."""
        tokens = [t.strip() for t in re.split(r"\s+", query) if len(t.strip()) > 1]
        if not tokens:
            return query.strip()
        # Concaténation par AND (&) avec wildcard de préfixe pour autocomplétion
        return " & ".join(f"{tok}:*" for tok in tokens)

    @staticmethod
    def extract_highlight_python(text_content: Optional[str], query: str, max_len: int = 180) -> str:
        """Extrait un snippet avec surlignage <mark> pour SQLite ou fallback."""
        if not text_content:
            return ""
        
        words = [re.escape(w) for w in query.split() if len(w) > 1]
        if not words:
            return text_content[:max_len] + ("..." if len(text_content) > max_len else "")
        
        pattern = re.compile(f"({'|'.join(words)})", re.IGNORECASE)
        match = pattern.search(text_content)
        
        if not match:
            return text_content[:max_len] + ("..." if len(text_content) > max_len else "")
        
        start = max(0, match.start() - 60)
        end = min(len(text_content), match.end() + 120)
        snippet = text_content[start:end]
        
        # Envelopper les mots trouvés dans <mark>
        highlighted = pattern.sub(r"<mark>\1</mark>", snippet)
        
        prefix = "..." if start > 0 else ""
        suffix = "..." if end < len(text_content) else ""
        return f"{prefix}{highlighted}{suffix}"

    def search(
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
    ) -> Tuple[List[FtsSearchResult], int]:
        """Effectue une recherche plein texte paginée et scorée."""
        clean_q = self.sanitize_query(query)
        if not clean_q:
            return [], 0

        page = max(1, page)
        page_size = max(1, min(page_size, 200))

        # Base filters
        clauses = []
        if categorie is not None:
            clauses.append(models.Marche.categorie_prestation == categorie)
        if region:
            clauses.append(models.Marche.region.ilike(f"%{region}%"))
        if ville:
            clauses.append(models.Marche.ville_execution.ilike(f"%{ville}%"))
        if organisme:
            clauses.append(models.Marche.organisme_acheteur.ilike(f"%{organisme}%"))
        if date_min is not None:
            clauses.append(models.Marche.date_parution >= date_min)
        if date_max is not None:
            clauses.append(models.Marche.date_parution <= date_max)
        if montant_min is not None:
            clauses.append(models.Marche.montant >= montant_min)
        if montant_max is not None:
            clauses.append(models.Marche.montant <= montant_max)

        if self.is_postgres:
            return self._search_postgres(
                clean_q, clauses, order_by, order_dir, page, page_size
            )
        else:
            return self._search_sqlite(
                clean_q, clauses, order_by, order_dir, page, page_size
            )

    def _search_postgres(
        self,
        query: str,
        clauses: List[Any],
        order_by: str,
        order_dir: str,
        page: int,
        page_size: int,
    ) -> Tuple[List[FtsSearchResult], int]:
        """Recherche plein-texte via to_tsvector, ts_rank_cd et ts_headline sur PostgreSQL."""
        ts_query_str = self.build_tsquery_string(query)
        ts_q = func.to_tsquery("french", ts_query_str)
        tsv = func.to_tsvector(
            "french",
            func.coalesce(models.Marche.titre_projet, "")
            + " "
            + func.coalesce(models.Marche.organisme_acheteur, "")
            + " "
            + func.coalesce(models.Marche.ville_execution, "")
            + " "
            + func.coalesce(models.Marche.tsv_search, "")
        )

        fts_clause = tsv.op("@@")(ts_q)
        all_clauses = [fts_clause] + clauses

        rank_expr = func.ts_rank_cd(tsv, ts_q).label("rank_score")
        headline_expr = func.ts_headline(
            "french",
            func.coalesce(models.Marche.titre_projet, ""),
            ts_q,
            "StartSel=<mark>, StopSel=</mark>, MaxWords=35, MinWords=15"
        ).label("highlight")

        # Total count
        count_stmt = select(func.count(models.Marche.id)).where(and_(*all_clauses))
        total = int(self.db.execute(count_stmt).scalar_one() or 0)

        # Select with ranking
        stmt = (
            select(models.Marche, rank_expr, headline_expr)
            .where(and_(*all_clauses))
        )

        if order_by == "pertinence":
            stmt = stmt.order_by(rank_expr.desc() if order_dir == "desc" else rank_expr.asc())
        elif order_by == "montant":
            stmt = stmt.order_by(models.Marche.montant.desc() if order_dir == "desc" else models.Marche.montant.asc())
        elif order_by == "date_parution":
            stmt = stmt.order_by(models.Marche.date_parution.desc() if order_dir == "desc" else models.Marche.date_parution.asc())
        else:
            stmt = stmt.order_by(rank_expr.desc())

        stmt = stmt.offset((page - 1) * page_size).limit(page_size)
        rows = self.db.execute(stmt).all()

        results = []
        for marche, rank, hl in rows:
            results.append(
                FtsSearchResult(
                    marche=marche,
                    score=float(rank or 1.0),
                    highlight=hl or self.extract_highlight_python(marche.titre_projet, query),
                    matched_fields=["titre_projet", "tsv_search"],
                )
            )
        return results, total

    def _search_sqlite(
        self,
        query: str,
        clauses: List[Any],
        order_by: str,
        order_dir: str,
        page: int,
        page_size: int,
    ) -> Tuple[List[FtsSearchResult], int]:
        """Fallback SQLite avec décomposition par tokens et scoring Python."""
        tokens = [t.strip() for t in query.split() if len(t.strip()) > 0]
        if not tokens:
            return [], 0

        # Chaque token doit correspondre à au moins un champ (AND entre tokens)
        token_clauses = []
        for tok in tokens:
            needle = f"%{tok}%"
            token_clauses.append(
                or_(
                    models.Marche.titre_projet.ilike(needle),
                    models.Marche.numero_appel_offre.ilike(needle),
                    models.Marche.reference.ilike(needle),
                    models.Marche.organisme_acheteur.ilike(needle),
                    models.Marche.ville_execution.ilike(needle),
                    models.Marche.tsv_search.ilike(needle),
                )
            )

        all_clauses = token_clauses + clauses
        count_stmt = select(func.count(models.Marche.id)).where(and_(*all_clauses))
        total = int(self.db.execute(count_stmt).scalar_one() or 0)

        stmt = select(models.Marche).where(and_(*all_clauses))

        # Tri de base SQL
        if order_by == "montant":
            stmt = stmt.order_by(models.Marche.montant.desc() if order_dir == "desc" else models.Marche.montant.asc())
        elif order_by == "date_parution":
            stmt = stmt.order_by(models.Marche.date_parution.desc() if order_dir == "desc" else models.Marche.date_parution.asc())
        elif order_by == "date_limite":
            stmt = stmt.order_by(models.Marche.date_limite.desc() if order_dir == "desc" else models.Marche.date_limite.asc())
        else:
            # Pour pertinence, on trie après en Python
            stmt = stmt.order_by(models.Marche.id.desc())

        # Sur SQLite, on prend une fenêtre plus large si tri par pertinence pour bien scorer
        limit = page_size if order_by != "pertinence" else min(200, total)
        offset = (page - 1) * page_size if order_by != "pertinence" else 0
        
        stmt = stmt.offset(offset).limit(limit)
        marches = list(self.db.execute(stmt).scalars().all())

        results = []
        for m in marches:
            # Score heuristique basé sur la présence des mots-clés
            score = 0.0
            matched = []
            q_lower = query.lower()
            
            titre = (m.titre_projet or "").lower()
            org = (m.organisme_acheteur or "").lower()
            num = (m.numero_appel_offre or "").lower()
            tsv = (m.tsv_search or "").lower()

            if q_lower in titre:
                score += 10.0
                matched.append("titre_projet")
            elif any(tok.lower() in titre for tok in tokens):
                score += 5.0
                matched.append("titre_projet")

            if q_lower in num:
                score += 8.0
                matched.append("numero_appel_offre")

            if q_lower in org:
                score += 4.0
                matched.append("organisme_acheteur")

            if any(tok.lower() in tsv for tok in tokens):
                score += 2.0
                matched.append("tsv_search")

            highlight_source = m.titre_projet or m.organisme_acheteur or ""
            if "tsv_search" in matched and m.tsv_search:
                highlight_source = f"{highlight_source} — {m.tsv_search}"

            hl = self.extract_highlight_python(highlight_source, query)

            results.append(
                FtsSearchResult(
                    marche=m,
                    score=round(score, 2),
                    highlight=hl,
                    matched_fields=matched or ["titre_projet"],
                )
            )

        if order_by == "pertinence":
            results.sort(key=lambda r: r.score, reverse=(order_dir == "desc"))
            results = results[(page - 1) * page_size : page * page_size]

        return results, total
