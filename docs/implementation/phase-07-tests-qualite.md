# Phase 7 — Tests & qualité

> **Effort** : 1 journée · **Risque** : faible · **Pré-requis** : Phases 1–6 terminées

---

## T7.1 — Tests smoke (déjà créé en T0.5)

**Description & objectif** : maintenir le test smoke au top.

**Modifications** :

| Module | Action | Détail |
|---|---|---|
| `tests` | `MODIFY` | `tests/test_smoke.py` : ajouter `test_openapi_accessible` (`/openapi.json` retourne 200) et `test_docs_accessible` (`/docs` retourne 200). |

**Plan de vérification** :
- [ ] `pytest tests/test_smoke.py -v` → 4 passed.

---

## T7.2 — Test API complet

**Description & objectif** : couvrir tous les endpoints de l'API.

**Modifications** :

| Module | Action | Détail |
|---|---|---|
| `tests` | `MODIFY` | `tests/test_api_endpoints.py` : étendre la couverture à **tous** les endpoints listés dans `main.py` (≥ 25 tests). |
| `tests` | `MODIFY` | `tests/conftest.py` : ajouter fixture `auth_headers` (vide pour l'instant, prêt pour Phase 8). |

**Plan de vérification** :
- [ ] `pytest tests/test_api_endpoints.py -v` → ≥ 25 passed.
- [ ] Aucun endpoint n'est marqué `xfail` (skipped toléré).

---

## T7.3 — Test pipeline (déjà créé en T2.8)

**Description & objectif** : enrichir les cas d'erreur.

**Modifications** :

| Module | Action | Détail |
|---|---|---|
| `tests` | `MODIFY` | `tests/test_pipeline.py` : ajouter :<br>- `test_upload_empty_file_raises_400`<br>- `test_upload_non_zip_file_raises_400`<br>- `test_pipeline_handles_pdf_only`<br>- `test_pipeline_handles_docx_only` |

**Plan de vérification** :
- [ ] `pytest tests/test_pipeline.py -v` → ≥ 8 passed.

---

## T7.4 — Test ML (déjà créé en T6.8)

**Description & objectif** : ajouter les cas limites.

**Modifications** :

| Module | Action | Détail |
|---|---|---|
| `tests` | `MODIFY` | `tests/test_ml.py` : ajouter `test_classifier_handles_unknown_category` et `test_anomaly_score_in_valid_range`. |

**Plan de vérification** :
- [ ] `pytest tests/test_ml.py -v` → ≥ 7 passed.

---

## T7.5 — Test NLP (déjà créé en T2.9)

**Description & objectif** : ajouter un test sur un texte avec des mois en toutes lettres.

**Modifications** :

| Module | Action | Détail |
|---|---|---|
| `tests` | `MODIFY` | `tests/test_nlp.py` : ajouter `test_extract_mois_en_lettres` ("4 mois", "vingt mois") et `test_normalize_money_with_currency_text`. |

**Plan de vérification** :
- [ ] `pytest tests/test_nlp.py -v` → ≥ 6 passed.

---

## T7.6 — Coverage globale

**Description & objectif** : mesurer et atteindre ≥ 60 %.

**Modifications** :

| Module | Action | Détail |
|---|---|---|
| `repo` | `NEW` | `pytest.ini` (ou `pyproject.toml`) : configuration pytest + coverage |
| `repo` | `NEW` | `.coveragerc` (exclure `tests/`, `alembic/`, `data/`) |
| `repo` | `CMD` | `pytest --cov=backend --cov=nlp --cov=ocr --cov=ml --cov=ingestion --cov-report=term-missing --cov-fail-under=60` |

**Plan de vérification** :
- [ ] Coverage global ≥ 60 %.
- [ ] Coverage `backend/repository.py` ≥ 80 %.
- [ ] Coverage `nlp/extract_entities.py` ≥ 70 %.

---

## T7.7 — Script `run_all_tests.sh`

**Description & objectif** : un seul point d'entrée pour CI locale.

**Modifications** :

| Module | Action | Détail |
|---|---|---|
| `scripts` | `NEW` | `scripts/run_all_tests.sh` (Linux/macOS) :<br>```bash<br>#!/usr/bin/env bash<br>set -e<br>echo "=== Lint ==="<br>flake8 backend/ nlp/ ocr/ ml/ ingestion/ tests/ --max-line-length=120 --ignore=E501,W503<br>echo "=== Migrations ==="<br>alembic upgrade head<br>echo "=== Tests Python ==="<br>pytest --cov=... --cov-fail-under=60<br>echo "=== Tests Frontend ==="<br>cd frontend-react && npm test -- --run && npm run build && cd ..<br>echo "=== Smoke ==="<br>uvicorn backend.main:app &<br>PID=$!<br>sleep 3<br>curl -sf http://localhost:8000/api/v1/analytics/kpis > /dev/null<br>kill $PID<br>echo "✅ ALL TESTS PASSED"<br>``` |
| `scripts` | `NEW` | `scripts/run_all_tests.ps1` (Windows) : équivalent PowerShell. |

**Plan de vérification** :
- [ ] `bash scripts/run_all_tests.sh` se termine par `✅ ALL TESTS PASSED`.
- [ ] `powershell scripts/run_all_tests.ps1` fait de même.

---

## T7.8 — Lint & formatage

**Description & objectif** : imposer un style.

**Modifications** :

| Module | Action | Détail |
|---|---|---|
| `repo` | `MODIFY` | `requirements.txt` : ajouter `flake8==7.1.1`, `black==24.8.0`, `isort==5.13.2` |
| `repo` | `NEW` | `.flake8` : `max-line-length=120, exclude=.venv,alembic,frontend-react,data` |
| `repo` | `NEW` | `pyproject.toml` (section `[tool.black]` et `[tool.isort]`) |
| `repo` | `CMD` | `black backend/ nlp/ ocr/ ml/ ingestion/ tests/ scripts/` |
| `repo` | `CMD` | `isort backend/ nlp/ ocr/ ml/ ingestion/ tests/ scripts/` |
| `repo` | `CMD` | `flake8 backend/ nlp/ ocr/ ml/ ingestion/ tests/` |

**Plan de vérification** :
- [ ] `flake8` ne retourne aucune erreur.
- [ ] `black --check .` ne retourne aucune modification à faire.

---

## ✅ Critères de sortie de la Phase 7

- [ ] `pytest --cov-fail-under=60` passe.
- [ ] `bash scripts/run_all_tests.sh` passe.
- [ ] Coverage : `backend/` ≥ 70 %, `nlp/` ≥ 70 %, `ml/` ≥ 60 %.
- [ ] Aucun warning `flake8`.
- [ ] `black --check` propre.

**Effort total** : 1 jour ouvré.
