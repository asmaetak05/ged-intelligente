# Changelog — Projet GED Intelligente

> Historique des évolutions par phase. Chaque entrée référence les tickets
> d'implémentation dans `docs/implementation/`.

## Format

| Date | Phase | Ticket | Description |
|---|---|---|---|

---

## Phase 0 — Fondations & alignement (en cours)

**Date** : 2026-07-12
**Branche** : `refactoring/unify-db-and-pipeline`

| Ticket | Description | Statut |
|---|---|---|
| T0.1 | Création de la branche `refactoring/unify-db-and-pipeline` | ✅ |
| T0.2 | Sauvegarde `ged.db` → `ged.db.bak` (12 AO préservés) | ✅ |
| T0.3 | Documentation audit (`docs/ANALYSE_ET_PLAN_ACTION.md`) + ce CHANGELOG | ✅ |
| T0.4 | Note de décision BDD dans `Note_Decision_V1.md` | 🔄 à venir |
| T0.5 | Création `tests/` (`__init__.py`, `conftest.py`, `test_smoke.py`) | 🔄 à venir |
| T0.6 | Compléter `.gitignore` (backups, pytest_cache, alembic, db-journal) | ✅ |
| T0.7 | Conversion `requirements.txt` UTF-16 → UTF-8 + ajout `playwright`, `alembic`, etc. | 🔄 à venir |
| T0.8 | Suppression fichiers 0 octet (`downloader.py`, `utils.py`, `init_db.py` script, `run_ocr_batch.py`, `seed_demo.py`) | 🔄 à venir |

---

## Phase 1 — Unification de la couche données (à venir)

| Ticket | Description | Statut |
|---|---|---|
| T1.1 | Réécrire `models.py` (SQLite + PostgreSQL via SQLAlchemy 2.0) | ⏳ |
| T1.2 | Réécrire `database.py` avec bascule auto SQLite/PostgreSQL | ⏳ |
| T1.3 | Créer `backend/repository.py` (logique SQL unique) | ⏳ |
| T1.4 | Réécrire `main.py` (suppression `sqlite3`, ajout endpoints manquants) | ⏳ |
| T1.5 | Réécrire `init_db.py` (corriger import `AppelOffre` cassé) | ⏳ |
| T1.6 | Configurer Alembic | ⏳ |
| T1.7 | Corriger `populate_db.py` (route + 18 AO supplémentaires) | ⏳ |
| T1.8 | Supprimer doublons (`scripts/init_db.py`, frontend vanilla) | ⏳ |
| T1.9 | Mettre à jour `schemas.py` | ⏳ |
| T1.10 | Tests `test_repository.py` (≥ 5 tests) | ⏳ |
| T1.11 | Tests `test_api_endpoints.py` (≥ 10 tests) | ⏳ |

---

## Phase 2 — Pipeline d'ingestion bout-en-bout (à venir)

| Ticket | Description | Statut |
|---|---|---|
| T2.1 | Extraire la logique OCR dans `ocr/` | ⏳ |
| T2.2 | Créer `nlp/extract_entities.py` (spaCy + dateparser) + `nlp/normalize.py` + `nlp/villes_maroc.py` | ⏳ |
| T2.3 | Refactor `extractor.py` (orchestrateur fin) | ⏳ |
| T2.4 | Brancher `POST /upload` (BackgroundTasks) | ⏳ |
| T2.5 | Sauvegarde `data/processed/text/` et `data/processed/json/` | ⏳ |
| T2.6 | Traçabilité `extractions_nlp` (source, score, snippet) | ⏳ |
| T2.7 | `GET /documents/{id}/status` (progression) | ⏳ |
| T2.8 | `tests/test_pipeline.py` (≥ 5 tests) | ⏳ |
| T2.9 | `tests/test_nlp.py` (≥ 4 tests) | ⏳ |

---

## Phases 3 à 9 — Planifiées (voir `docs/implementation/`)

Phases détaillées dans `docs/implementation/phase-03-dataset-demo.md`
à `phase-09-polish-soutenance.md`. Estimations :

| Phase | Titre | Effort | Cible |
|---|---|---|---|
| 3 | Données réelles & dataset de démo | 1 j | ≥ 30 AO |
| 4 | Dashboard décisionnel | 1,5 j | 6 KPIs réels |
| 5 | Page détail document & recherche | 1 j | UI complète |
| 6 | ML baseline | 1,5 j | TF-IDF + SVM + anomalies |
| 7 | Tests & qualité | 1 j | coverage ≥ 60 % |
| 8 | Documentation & livrables | 1,5 j | rapport + slides |
| 9 | Polish final & soutenance | ½ j | démo 5 min rodée |

**Effort total** : 9 jours ouvrés.
