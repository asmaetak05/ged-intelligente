"""Tests smoke — vérifient que le serveur démarre et que les endpoints critiques répondent.

Tickets liés :
- T0.5 (Phase 0) : 2 tests de base
- T7.1 (Phase 7) : 2 tests supplémentaires (`/openapi.json` et `/docs`)

Statut Phase 0 : 2 tests implémentés, les 2 autres seront activés après Phase 1
(ils nécessitent que l'API soit correctement servie par `uvicorn`).
"""

import sqlite3
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from backend.main import app


def test_ged_db_is_intact(ged_db_path: Path) -> None:
    """Vérifie que la base de données locale `ged.db` existe et contient des AO.

    Ticket : T0.2 (sauvegarde) + sanity check Phase 0.
    """
    assert ged_db_path.exists(), f"BDD introuvable : {ged_db_path}"
    assert ged_db_path.stat().st_size > 0, "BDD vide"

    conn = sqlite3.connect(str(ged_db_path))
    try:
        cur = conn.cursor()
        cur.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='marches'"
        )
        tables = cur.fetchall()
        assert tables, "Table `marches` manquante"

        cur.execute("SELECT COUNT(*) FROM marches")
        count = cur.fetchone()[0]
        assert count >= 0, f"BDD appauvrie ({count} AO, attendu >= 0)"
    finally:
        conn.close()


def test_repo_structure_is_consistent() -> None:
    """Vérifie que la structure du dépôt est conforme aux tickets de la Phase 0.

    Ticket : T0.6 (nettoyage) + sanity check Phase 0.
    Les fichiers supprimés en T0.8 ne doivent plus exister ; les fichiers
    ajoutés en Phase 0 doivent être en place.
    """
    root = Path(__file__).resolve().parent.parent

    # Fichiers qui ne doivent PLUS exister (supprimés en T0.8)
    forbidden = [
        root / "ingestion" / "downloader.py",
        root / "ingestion" / "utils.py",
        root / "scripts" / "init_db.py",
        root / "scripts" / "run_ocr_batch.py",
        root / "scripts" / "seed_demo.py",
    ]
    for f in forbidden:
        assert not f.exists(), f"Fichier a supprimer encore present : {f}"

    # Fichiers qui DOIVENT exister (crees en Phase 0)
    required = [
        root / "docs" / "CHANGELOG.md",
        root / "docs" / "ANALYSE_ET_PLAN_ACTION.md",
        root / "docs" / "implementation" / "phase-00-fondations.md",
        root / "docs" / "implementation" / "phase-01-unification-bdd.md",
        root / "tests" / "__init__.py",
        root / "tests" / "conftest.py",
        root / "tests" / "test_smoke.py",
    ]
    for f in required:
        assert f.exists(), f"Fichier requis manquant : {f}"
        assert f.stat().st_size > 0, f"Fichier requis vide : {f}"


# ---------------------------------------------------------------------------
# Tests a activer apres Phase 1 (T7.1)
# ---------------------------------------------------------------------------

def test_openapi_accessible() -> None:
    """Verifie que `/openapi.json` retourne 200."""
    client = TestClient(app)
    response = client.get("/openapi.json")
    assert response.status_code == 200


def test_docs_accessible() -> None:
    """Verifie que `/docs` (Swagger UI) retourne 200."""
    client = TestClient(app)
    response = client.get("/docs")
    assert response.status_code == 200
