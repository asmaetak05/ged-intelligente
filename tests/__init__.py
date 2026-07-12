"""Tests pour le projet GED Intelligente.

Ce package contient les tests pytest. L'arborescence prévue est :

tests/
├── __init__.py             # ce fichier
├── conftest.py             # fixtures partagées (client FastAPI, db_session)
├── test_smoke.py           # tests smoke (serveur démarre, endpoints répondent)
├── test_repository.py      # tests du repository (Phase 1)
├── test_api_endpoints.py   # tests des endpoints (Phase 1)
├── test_pipeline.py        # tests du pipeline ingestion (Phase 2)
├── test_nlp.py             # tests du NLP (Phase 2)
├── test_analytics.py       # tests des agrégations BI (Phase 4)
├── test_ml.py              # tests du ML (Phase 6)
├── test_bulk_ingestion.py  # tests de charge (Phase 3)
└── fixtures/               # fichiers de test (ZIP, PDF, DOCX)
"""
