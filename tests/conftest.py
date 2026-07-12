"""Fixtures partagées pour les tests pytest du projet GED Intelligente.

Ces fixtures seront enrichies au fil des phases :
- T0.5 (Phase 0) : fixtures minimales pour smoke tests
- T1.10 (Phase 1) : fixtures `db_session` (SQLAlchemy Session)
- T1.11 (Phase 1) : fixtures `client` (TestClient FastAPI)
- T2.8 (Phase 2) : fixture `sample_zip_path`
- T3.6 (Phase 3) : fixture `bulk_zips`
"""

import os
import sys
from pathlib import Path

import pytest

# Permettre l'import de `backend.*` depuis la racine du projet
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


# ---------------------------------------------------------------------------
# Phase 0 — fixtures minimales
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session")
def project_root() -> Path:
    """Retourne la racine du projet."""
    return ROOT


@pytest.fixture(scope="session")
def ged_db_path(project_root: Path) -> Path:
    """Chemin vers la base de données `ged.db` (ou `ged.db.bak` si elle n'existe pas)."""
    primary = project_root / "ged.db"
    if primary.exists():
        return primary
    backup = project_root / "ged.db.bak"
    if backup.exists():
        return backup
    pytest.skip("Aucune base ged.db / ged.db.bak disponible")


# ---------------------------------------------------------------------------
# Phase 1 — fixtures principales (à activer après refactoring)
# ---------------------------------------------------------------------------

@pytest.fixture
def db_session():
    """Session SQLAlchemy vers une base SQLite en mémoire.

    NOTE : sera implémentée en T1.10 après le refactoring de `database.py`.
    Pour l'instant, la fixture lève NotImplementedError pour signaler qu'elle
    n'est pas encore prête.
    """
    pytest.skip("db_session sera disponible après la Phase 1 (T1.10)")


@pytest.fixture
def client():
    """Client HTTP FastAPI pour les tests d'API.

    NOTE : sera implémenté en T1.11.
    """
    pytest.skip("client sera disponible après la Phase 1 (T1.11)")


# ---------------------------------------------------------------------------
# Utilitaires
# ---------------------------------------------------------------------------

def require_env(name: str) -> str:
    """Récupère une variable d'environnement, lève une erreur claire si absente."""
    value = os.environ.get(name)
    if value is None:
        pytest.fail(f"Variable d'environnement {name!r} requise pour ce test")
    return value
