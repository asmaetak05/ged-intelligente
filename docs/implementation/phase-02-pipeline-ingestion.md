# Phase 2 — Pipeline d'ingestion bout-en-bout

> **Effort** : 1,5 journée · **Risque** : moyen · **Pré-requis** : Phase 1 terminée

---

## T2.1 — Extraire la logique OCR dans `ocr/`

**Description & objectif** : respecter le plan (logique OCR dans `ocr/`, pas dans `ingestion/`).

**Modifications** :

| Module | Action | Détail |
|---|---|---|
| `ocr` | `MODIFY` | `ocr/extract_native.py` : déplacer `read_pdf()` (PyMuPDF) depuis `ingestion/extractor.py:53-77`. |
| `ocr` | `MODIFY` | `ocr/extract_ocr.py` : déplacer la partie Tesseract (`pdf2image` + `pytesseract`). |
| `ocr` | `MODIFY` | `ocr/preprocess.py` : ajouter fonctions `deskew()`, `denoise()`, `binarize()` (utilise OpenCV si dispo, sinon no-op). |
| `ingestion` | `MODIFY` | `ingestion/extractor.py` : remplacer les imports internes par `from ocr import extract_native, extract_ocr, preprocess`. |

**Plan de vérification** :
- [ ] `python -c "from ocr import extract_native, extract_ocr, preprocess; print('OK')"` ne lève pas d'exception.
- [ ] `python -c "from ingestion.extractor import read_pdf; print('OK')"` fonctionne toujours (réexport).

---

## T2.2 — Créer le module NLP

**Description & objectif** : implémenter réellement l'extraction d'entités (au-delà des 4 regex actuelles) avec spaCy et dateparser.

**Modifications** :

| Module | Action | Détail |
|---|---|---|
| `nlp` | `MODIFY` | `nlp/extract_entities.py` :<br>1. Charger `fr_core_news_sm` au premier import (lazy load).<br>2. Fonction `extract(text: str) -> dict` retournant :<br>   - `objet` (regex)<br>   - `maitre_ouvrage` (regex + spaCy ORG)<br>   - `estimation_mad` (regex MONEY)<br>   - `caution_mad` (regex)<br>   - `delai_execution_mois` (regex nombre + unité)<br>   - `penalite_retard_mille` (regex)<br>   - `date_parution` (regex + `dateparser`)<br>   - `date_limite` (regex "date limite" + `dateparser`)<br>   - `lieu_ouverture_plis` (regex + spaCy LOC)<br>   - `categorie_marche` (classif simple par mots-clés)<br>   - `reference` (regex `Réf[éerence]*\s*:\s*(\S+)`)<br>   - `region` (lookup dans liste villes marocaines)<br>3. Retourne aussi `confidence` (heuristique 0–1 par champ). |
| `nlp` | `MODIFY` | `nlp/normalize.py` :<br>1. `normalize_date(fr_text: str) -> date` (utilise `dateparser`).<br>2. `normalize_money(fr_text: str) -> Decimal` (gère `1 234,56 DHS` / `1.234,56 MAD` / `1 234 DH`).<br>3. `normalize_mois(text: str) -> int` (gère `4 mois`, `18 mois`, `90 jours`). |
| `nlp` | `NEW` | `nlp/villes_maroc.py` : liste de 50+ villes avec leur région. |

**Plan de vérification** :
- [ ] `python -c "from nlp.extract_entities import extract; print(extract('Objet: Construction d\\'une route. Caution provisoire: 5000 DHS'))"` retourne un dict non vide.
- [ ] `python -c "from nlp.normalize import normalize_date; print(normalize_date('27 août 2025'))"` retourne `datetime.date(2025, 8, 27)`.
- [ ] `python -m spacy download fr_core_news_sm` réussit (ou est déjà installé via `requirements.txt`).

---

## T2.3 — Refactor de l'orchestrateur `extractor.py`

**Description & objectif** : `extractor.py` devient un orchestrateur fin qui appelle `ocr/` et `nlp/`, puis poste le résultat.

**Modifications** :

| Module | Action | Détail |
|---|---|---|
| `ingestion` | `MODIFY` | `ingestion/extractor.py` :<br>1. Conserver `process_archive(zip_path, api_url) -> bool` mais en plus court (~50 lignes).<br>2. Pour chaque fichier extrait, appelle `ocr.extract_native.read_pdf()` ou `ocr.extract_ocr.read_docx()` (ou nouvelle fonction OCR pour scans).<br>3. Concatène les textes, appelle `nlp.extract_entities.extract(full_text)`.<br>4. POST le résultat à `{api_url}/api/v1/ged/documents/upload` puis `{api_url}/api/v1/ged/appels-offres`.<br>5. Sauvegarde `data/processed/text/{numero}.txt` et `data/processed/json/{numero}.json`. |

**Plan de vérification** :
- [ ] `python -c "from ingestion.extractor import process_archive; print('OK')"` ne lève pas d'exception.
- [ ] `python -m ingestion.extractor` traite tous les ZIP de `data/raw/` (script conservant le mode CLI).

---

## T2.4 — Backend : endpoint upload branché

**Description & objectif** : `POST /api/v1/ged/documents/upload` ne retourne plus un dict statique. Il crée un `Document`, sauvegarde le fichier, lance l'orchestrateur en arrière-plan.

**Modifications** :

| Module | Action | Détail |
|---|---|---|
| `backend` | `NEW` | `backend/tasks.py` :<br>- `process_document_async(document_id: int, file_path: str)` :<br>  1. Marque `Document.status='extracted'`<br>  2. Appelle `ingestion.extractor.process_archive(file_path, ...)`<br>  3. À la fin, marque `Document.status='ocr_processed'`<br>  4. Insère un `OcrLog` avec `confidence_score_avg` réel |
| `backend` | `MODIFY` | `backend/main.py` :<br>1. `upload_document` :<br>   - Sauvegarde le fichier dans `data/raw/{uuid}.zip` (ou `data/raw/{numero_ordre}.zip` si nommage standard)<br>   - Crée `Document` avec `status='raw_zip'`, `archive_name`, `file_name`, `extension`, `storage_path`<br>   - `BackgroundTasks.add_task(process_document_async, doc_id, file_path)`<br>   - Retourne `{"document_id": doc_id, "status": "queued", "filename": file.filename}` |
| `backend` | `MODIFY` | `backend/main.py` : ajouter `GET /api/v1/ged/documents/{id}/status` retournant `{"id", "status", "filename", "updated_at"}`. |

**Plan de vérification** :
- [ ] `curl -F file=@data/samples/test.zip http://localhost:8000/api/v1/ged/documents/upload` retourne un JSON avec `document_id`.
- [ ] 5 secondes après, `GET /api/v1/ged/documents/{id}/status` retourne `ocr_processed` (ou `failed`).
- [ ] Un `OcrLog` est créé : `sqlite3 ged.db "SELECT count(*) FROM ocr_logs"` → ≥ 1.

---

## T2.5 — Sauvegarde des sorties intermédiaires

**Description & objectif** : les textes OCR et JSON structurés doivent persister sur disque (traçabilité, debug, rejeu).

**Modifications** :

| Module | Action | Détail |
|---|---|---|
| `ingestion` | `MODIFY` | `ingestion/extractor.py` : ajouter `save_text(numero, full_text)` et `save_json(numero, payload)` qui écrivent dans `data/processed/text/{numero}.txt` et `data/processed/json/{numero}.json`. |
| `repo` | `CMD` | `mkdir -p data/processed/text data/processed/json data/samples` (déjà présents, vérifier). |

**Plan de vérification** :
- [ ] Après ingestion, `ls data/processed/text/` contient au moins 1 fichier `.txt`.
- [ ] `ls data/processed/json/` contient au moins 1 fichier `.json`.

---

## T2.6 — Traçabilité champ par champ

**Description & objectif** : chaque champ extrait doit être enregistré avec sa source, son score, et un snippet de texte brut. La table `extractions_nlp` existe déjà (cf. audit).

**Modifications** :

| Module | Action | Détail |
|---|---|---|
| `nlp` | `MODIFY` | `nlp/extract_entities.py` : `extract()` retourne `{"fields": {nom: {"value": v, "source": "regex|spacy|llm", "score": float, "snippet": str}}}` |
| `backend` | `MODIFY` | `backend/tasks.py` : pour chaque champ, insère une ligne dans `extractions_nlp` (à créer si inexistante). |
| `backend` | `MODIFY` | `backend/models.py` : ajouter modèle `ExtractionNlp` (`id`, `document_id`, `field_name`, `value`, `source`, `score`, `snippet`, `extracted_at`). |
| `backend` | `MODIFY` | `alembic/versions/0002_extraction_nlp.py` (auto-généré). |
| `repo` | `CMD` | `alembic revision --autogenerate -m "add extraction_nlp table"` puis `alembic upgrade head` |

**Plan de vérification** :
- [ ] Après ingestion, `sqlite3 ged.db "SELECT count(*) FROM extractions_nlp"` ≥ 5.
- [ ] `sqlite3 ged.db "SELECT field_name, source, score FROM extractions_nlp LIMIT 5"` montre la traçabilité.

---

## T2.7 — Endpoint de progression

**Description & objectif** : le frontend doit pouvoir interroger l'état d'un upload en temps réel.

**Modifications** :

| Module | Action | Détail |
|---|---|---|
| `backend` | `MODIFY` | `backend/main.py` : `GET /api/v1/ged/documents/{id}/status` retourne :<br>```json<br>{"id": 1, "status": "ocr_processed", "filename": "...", "updated_at": "...", "ocr_confidence": 87.3}<br>``` |
| `backend` | `MODIFY` | `backend/tasks.py` : mettre à jour `Document.updated_at` à chaque transition de statut. |

**Plan de vérification** :
- [ ] Pendant l'ingestion, plusieurs appels successifs à `GET /status` montrent une progression de `raw_zip` → `extracted` → `ocr_processed`.
- [ ] `updated_at` change entre deux statuts.

---

## T2.8 — Tests du pipeline complet

**Description & objectif** : simuler un upload ZIP de bout en bout et vérifier les effets de bord en BDD.

**Modifications** :

| Module | Action | Détail |
|---|---|---|
| `tests` | `NEW` | `tests/fixtures/sample_ao.zip` (ZIP de test, 1 PDF minimal, 1 DOCX minimal, taille < 50 Ko). |
| `tests` | `NEW` | `tests/test_pipeline.py` (≥ 5 tests) :<br>- `test_upload_creates_document`<br>- `test_pipeline_runs_in_background`<br>- `test_pipeline_creates_marche`<br>- `test_pipeline_inserts_ocr_log`<br>- `test_pipeline_handles_corrupted_zip` |
| `tests` | `MODIFY` | `tests/conftest.py` : fixture `sample_zip_path` qui pointe vers `tests/fixtures/sample_ao.zip`. |

**Plan de vérification** :
- [ ] `pytest tests/test_pipeline.py -v` → 5 passed.
- [ ] Le ZIP de test produit au moins 1 ligne dans `appels_offres` et 1 dans `ocr_logs`.

---

## T2.9 — Tests NLP

**Description & objectif** : l'extraction d'entités doit être testée sur des textes connus.

**Modifications** :

| Module | Action | Détail |
|---|---|---|
| `tests` | `NEW` | `tests/test_nlp.py` (≥ 4 tests) :<br>- `test_extract_objet`<br>- `test_extract_dates_french`<br>- `test_extract_money_with_spaces`<br>- `test_extract_region_from_city` |

**Plan de vérification** :
- [ ] `pytest tests/test_nlp.py -v` → 4 passed.
- [ ] `pytest --cov=nlp --cov-report=term-missing` ≥ 60 %.

---

## ✅ Critères de sortie de la Phase 2

- [ ] `curl -F file=@data/samples/sample.zip http://localhost:8000/api/v1/ged/documents/upload` produit un `Document`, un `OcrLog`, et un `Marche`.
- [ ] `data/processed/text/` et `data/processed/json/` contiennent des fichiers.
- [ ] `extractions_nlp` est peuplée avec ≥ 5 lignes par document.
- [ ] `pytest tests/test_pipeline.py tests/test_nlp.py` → 100 % vert.
- [ ] Le frontend React (Phase 5) peut afficher la progression réelle.

**Effort total** : 1,5 jour ouvré.
