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
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from sqlalchemy.pool import StaticPool
    from backend.database import Base
    import backend.models
    
    engine = create_engine(
        "sqlite:///:memory:", 
        connect_args={"check_same_thread": False},
        poolclass=StaticPool
    )
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture
def client(db_session):
    from fastapi.testclient import TestClient
    from backend.main import app
    from backend.database import get_db

    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


# ---------------------------------------------------------------------------
# Utilitaires
# ---------------------------------------------------------------------------

def require_env(name: str) -> str:
    """Récupère une variable d'environnement, lève une erreur claire si absente."""
    value = os.environ.get(name)
    if value is None:
        pytest.fail(f"Variable d'environnement {name!r} requise pour ce test")
    return value
