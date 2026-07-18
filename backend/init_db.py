"""Initialisation de la base de données (T1.5).

Crée le schéma complet de l'application en invoquant
``Base.metadata.create_all`` sur l'engine courant. L'opération est
**idempotente** : ré-exécutable sans erreur (les tables existantes sont
ignorées par ``create_all``).

Pré-requis : T1.2 (bascule SQLite / PostgreSQL via ``DATABASE_URL``).
L'import de ``AppelOffre`` (qui n'existe pas dans ``backend.models.py``)
a été supprimé : on importe désormais ``Base`` qui suffit à porter
toutes les tables déclarées par les modèles.
"""
from __future__ import annotations

import os
import sys

from sqlalchemy.exc import SQLAlchemyError

# Permet l'exécution du script depuis n'importe quel cwd.
_BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(_BACKEND_DIR)
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from backend.database import Base, engine, get_database_url, is_postgresql  # noqa: E402
# L'import de `Base` ci-dessus déclenche, par effet de bord, le chargement
# de tous les modèles qui en héritent (Marche, Document, OcrLog, ...).
# On force donc l'import de `backend.models` pour s'assurer que toutes les
# tables sont enregistrées dans `Base.metadata` AVANT `create_all`.
import backend.models  # noqa: F401, E402


def init_db() -> int:
    """Crée les tables manquantes dans la base courante.

    Returns
    -------
    int
        Nombre de tables effectivement créées lors de cet appel (``0``
        si la base était déjà initialisée, ``len(Base.metadata.tables)``
        sinon).

    Notes
    -----
    * ``create_all`` est idempotent : il n'écrase pas les tables existantes.
    * Pour une réinitialisation complète, supprimer le fichier SQLite
      (ou utiliser Alembic en T1.6).
    """
    print("=" * 70)
    print("Initialisation de la base de données")
    print(f"  DATABASE_URL : {get_database_url()}")
    print(f"  Driver       : {'postgresql' if is_postgresql() else engine.url.drivername}")
    print(f"  Tables       : {sorted(Base.metadata.tables.keys())}")
    print("=" * 70)

    pre_existing = set(_list_existing_tables())
    target_tables = set(Base.metadata.tables.keys())
    to_create = target_tables - pre_existing

    try:
        Base.metadata.create_all(bind=engine)
    except SQLAlchemyError as exc:
        print("[ERREUR] Échec de la création des tables :")
        print(f"  {exc.__class__.__name__}: {exc}")
        if is_postgresql():
            print("  → Vérifiez que PostgreSQL est démarré (ex. `docker compose up -d`).")
        else:
            print("  → Vérifiez les droits d'écriture sur le répertoire du fichier SQLite.")
        return 0

    created = len(to_create)
    if created == 0:
        print(f"[OK] Schéma déjà à jour ({len(target_tables)} tables présentes).")
    else:
        print(f"[OK] {created} table(s) créée(s) : {sorted(to_create)}")
        print(f"     Total : {len(target_tables)} tables.")

    return created


def _list_existing_tables() -> list[str]:
    """Liste les tables déjà présentes dans la base (best-effort)."""
    try:
        with engine.connect() as conn:
            return [row[0] for row in conn.exec_driver_sql(
                "SELECT name FROM sqlite_master WHERE type='table'"
                if engine.url.drivername == "sqlite"
                else "SELECT tablename FROM pg_tables WHERE schemaname = current_schema()"
            ).fetchall()]
    except SQLAlchemyError:
        # Si la base n'est pas accessible, on suppose vide : create_all
        # fera le reste et remontera une exception claire si problème réel.
        return []


if __name__ == "__main__":
    init_db()
