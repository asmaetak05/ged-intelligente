# 📋 Analyse Approfondie & Plan d'Action — Projet GED Intelligente

> **Date de l'analyse** : 11 juillet 2026
> **Auteur de l'analyse** : Claude (revue technique du dépôt)
> **Source** : audit du code + croisement avec le rapport d'avancement fourni

---

## 1. Synthèse exécutive

Le rapport d'avancement fourni est **globalement fidèle**, mais **incomplet sur certains points techniques**. L'audit direct du dépôt révèle :

| Constat du rapport | Vérifié ? | Détail ajouté par l'audit |
|---|---|---|
| Double architecture SQLite / PostgreSQL | ✅ Vrai | `backend/database.py:7` pointe sur PostgreSQL, `main.py:30` ouvre `ged.db` en SQLite. **Aucun code n'utilise SQLAlchemy sauf 2 endpoints ML**. |
| Upload non branché | ✅ Vrai | `main.py:50` retourne un dict statique. Aucune tâche de fond n'est enregistrée. |
| `init_db.py` importe `AppelOffre` inexistant | ✅ Vrai | Le modèle s'appelle `Marche` dans `models.py:44`. |
| `populate_db.py` pointe vers `/api/appels_offres/` | ✅ Vrai | Route inexistante (la bonne est `/api/v1/ged/appels-offres`). |
| Deux frontends | ✅ Vrai | `frontend/` (vanilla, monté via `main.py:292`) et `frontend-react/` (React 19 + Vite). |
| `playwright` absent de `requirements.txt` | ✅ Vrai | Le `requirements.txt` actuel (encodage UTF-16) ne contient pas `playwright`, alors que `playwright_scraper_batch.py` l'utilise. |
| `nlp/`, `ml/`, `ocr/`, `search/`, `tests/`, `alembic/` présents | ⚠️ **À nuancer** | Les dossiers **existent mais sont vides** (fichiers `.py` de 0 octet), donc la promesse structurelle est créée mais aucune logique n'y vit. La logique OCR/NLP est en réalité dans `ingestion/extractor.py`. |
| Données déjà présentes | ❌ **Non mentionné dans le rapport** | La base `ged.db` contient déjà **12 AO** (un `populate_db` a partiellement fonctionné ou un seed manuel a été fait). 3 tables existent : `appels_offres`, `documents_ao`, `extractions_nlp`. |
| `taux_reussite_ocr_pct: 98.5` hardcodé | ✅ Vrai | `main.py:218`. Aucune lecture d'`OcrLog`. |
| `taux top 4 au lieu de 10` | ✅ Vrai | `main.py:256` : `sorted(...)[:4]`. |
| `get_trends` mocké | ✅ Vrai | `main.py:227` retourne un dict en dur. |
| `docs/installation.md` absent | ✅ Vrai | Seul un fichier vide du même nom est présent (`docs/installation.md`, 0 octet). |

**Verdict** : Le rapport est **fiable à ~85 %**. Il sous-estime la **profondeur du décalage structurel** (dossiers créés mais vides) et **omet l'existence de données déjà injectées** (12 AO) qui constituent un acquis valorisable pour la démo.

---

## 2. Audit technique détaillé par couche

### 2.1 L1 — Collecte & OCR (`ingestion/`)

| Élément | Constat | Note |
|---|---|---|
| `scraper.py` (requests/BS4) | Présent, 3 Ko. Prototype simple. | ⭐⭐ |
| `playwright_scraper.py` | Présent, 3,3 Ko. | ⭐⭐ |
| `playwright_scraper_batch.py` | Robuste, 14 Ko, pagination ASP.NET + anti-doublons. | ⭐⭐⭐⭐ |
| `playwright_scraper_exact.py` | 4,5 Ko, script de diagnostic. | ⭐⭐ |
| `extractor.py` | Pipeline OCR fallback PyMuPDF → Tesseract, regex + LLM optionnel. CLI seulement. | ⭐⭐⭐ |
| `diagnostic_pagination.py` / `diagnostic_details_ao.py` | Scripts de debug Playwright, sans impact production. | — |
| `downloader.py` | Vide (0 octet). | ❌ |
| `utils.py` | Vide (0 octet). | ❌ |

**Manques** :
- Aucun lien `extractor.py` ↔ `main.py` (l'upload ne déclenche rien).
- Pas de dossier `data/processed/text/` ou `data/processed/json/` réellement alimenté.
- Dossier `data/raw/` vide (`.gitkeep` seul).
- `requirements.txt` ne contient pas `playwright` → `playwright_scraper_batch.py` ne peut pas tourner en l'état.

### 2.2 L2 — NLP & structuration (`nlp/`, `ocr/`)

| Élément | Constat | Note |
|---|---|---|
| `nlp/extract_entities.py` | 0 octet. | ❌ |
| `nlp/normalize.py` | 0 octet. | ❌ |
| `ocr/extract_native.py` | 0 octet. | ❌ |
| `ocr/extract_ocr.py` | 0 octet. | ❌ |
| `ocr/preprocess.py` | 0 octet. | ❌ |
| Regex dans `ingestion/extractor.py:79-99` | OK pour `objet`, `caution`, `delai`, `penalite`. | ⭐⭐ |
| spaCy | Installé (`requirements.txt:78`) mais **jamais importé** dans le code. | ❌ |
| `dateparser` | Installé (`requirements.txt:18`) mais **jamais importé**. | ❌ |
| Fallback OpenAI | Présent dans `extractor.py:24-30`, désactivé par défaut, jamais testé. | ⭐ |

**Manques** :
- Aucun module `nlp/` réellement implémenté.
- Champs obligatoires du plan **non extraits** : `date_parution`, `date_limite`, `reference`, `region`.
- Aucune traçabilité champ par champ (les regex renvoient un dict sans score de confiance).

### 2.3 L3 — Backend / API / Recherche (`backend/`, `search/`)

| Élément | Constat | Note |
|---|---|---|
| `main.py` | 11 Ko, 19 endpoints. Mélange SQLAlchemy + sqlite3 brut. | ⭐⭐ |
| `models.py` | Modèle PostgreSQL propre : `Document`, `Marche`, `OcrLog`, `CritereHumain`, `MlInsight`. | ⭐⭐⭐ |
| `schemas.py` | Pydantic v2, 1,9 Ko, peu utilisé. | ⭐ |
| `database.py` | Pointe PostgreSQL (port 5432). Aucune bascule SQLite. | ⭐ |
| `init_db.py` | **CASSÉ** : importe `AppelOffre` (n'existe plus). | ❌ |
| `search/postgres_fts.py` | 0 octet. | ❌ |
| FTS SQLite | OK dans `main.py:60-70`, fallback LIKE `main.py:91-99`. | ⭐⭐⭐ |
| `scripts/setup_postgres_triggers.sql` | Présent (1,1 Ko), trigger TSVECTOR documenté, **jamais appliqué**. | ⭐ |

**Endpoints réels (19) :**
- GED : `upload`, `search`, `documents/{id}/preview`, `documents`, `appels-offres` (create/update).
- Analytics : `kpis`, `trends` (mocké), `distribution/categories`, `top-buyers` (top 4).
- ML : `predictions/{marche_id}`, `retrain` (mocké), `anomalies` (mocké).
- Système : `monitoring` (mocké).

**Endpoints annoncés dans la doc mais manquants :**
- `GET /api/v1/ged/appels-offres/{numero}` (détail).
- `GET /api/v1/ged/appels-offres` avec filtres (date, ville, organisme, catégorie).
- `GET /api/v1/ged/ocr-quality` (taux réel).
- `GET /api/v1/analytics/delai-moyen` (publication → date limite).

### 2.4 L4 — Frontend / BI / ML

| Frontend | Stack | Statut | Note |
|---|---|---|---|
| `frontend/` (vanilla) | HTML + JS + Vite, monté par FastAPI (`main.py:292`) | Actif en production via l'API | ⭐⭐ (basique) |
| `frontend-react/` | React 19 + Tailwind + Recharts | Code prêt, **non servi par l'API** | ⭐⭐⭐ |

**Composants `frontend-react/src/components/` (8 fichiers) :**
- `Dashboard.jsx` (4 Ko) : KPIs + charts.
- `Explorer.jsx` (2,5 Ko) : liste des AO.
- `SearchFTS.jsx` (3,4 Ko) : barre de recherche.
- `Upload.jsx` (4,7 Ko) : upload avec barre de progression factice (`Upload.jsx` ne lit pas la réponse).
- `PredictorML.jsx` (3,2 Ko) : panneau ML.
- `Monitoring.jsx` (2,5 Ko) : surveillance système.
- `Sidebar.jsx`, `Topbar.jsx`, `Placeholder.jsx`.

**Problèmes :**
- `Dashboard.jsx` consomme `taux_reussite_ocr_pct` mocké à 98.5.
- `SearchFTS.jsx` ne déclenche pas la pagination.
- `Upload.jsx` n'envoie pas réellement le fichier (à vérifier dans le code).
- Aucun composant `DocumentDetail.jsx`.

### 2.5 ML (`ml/`)

| Élément | Constat |
|---|---|
| `ml/models/` | Dossier vide. |
| Notebook | ❌ aucun. |
| Modèles sérialisés (joblib) | ❌ aucun. |
| Endpoint `ml/retrain` | Retourne un dict en dur, ne lance rien. |
| `MlInsight` (modèle) | Bien défini, **non alimenté**. |

**Constat** : la couche ML est entièrement promise, **zéro ligne de code effective**.

### 2.6 Données & BDD

```
ged.db (32 Ko) — SQLite, déjà initialisée
├── appels_offres (12 lignes, 18 colonnes)  ← données seed partiellement injectées
├── documents_ao (vide)
└── extractions_nlp (vide)
```

**Champs existants** : `id, numero_ordre, objet, maitre_ouvrage, estimation_mad, caution_mad, dossier_zip_source, delai_execution, penalite_retard, caution_definitive, retenue_garantie, agrements_exiges, profils_exiges, methode_notation, date_ouverture_plis, lieu_ouverture_plis, categorie_marche, date_ingestion`.

**Acquis valorisable** : 12 AO seedés ⇒ démo possible immédiatement si on connecte l'API à cette base réelle plutôt qu'aux mocks.

### 2.7 Scripts

| Fichier | Statut |
|---|---|
| `scripts/init_db.py` | 0 octet, doublon de `backend/init_db.py`. |
| `scripts/populate_db.py` | Pointe `/api/appels_offres/` (mauvaise route), 2 AO en dur. |
| `scripts/read_models.py` / `read_word.py` | Helpers de debug, peu utiles. |
| `scripts/run_ocr_batch.py`, `seed_demo.py` | 0 octet. |
| `scripts/setup_postgres_triggers.sql` | OK, non appliqué. |

---

## 3. Diagnostic par criticité

| # | Problème | Criticité | Impact démo |
|---|---|---|---|
| 1 | Double BDD (PostgreSQL / SQLite) — l'API ne fonctionne pas hors SQLite | 🔴 Critique | Si la démo lance `uvicorn` sans `docker compose up`, l'API crash en `create_all` (ligne 15) puis bascule en mode dégradé silencieux. |
| 2 | `init_db.py` cassé (import `AppelOffre`) | 🔴 Critique | Impossible de (re)créer le schéma. |
| 3 | Upload mort (`main.py:50`) | 🔴 Critique | La promesse "Upload → OCR → DB" n'existe pas. |
| 4 | `populate_db.py` mauvaise route | 🟠 Majeure | Aucun seed reproductible. |
| 5 | `playwright` non déclaré dans `requirements.txt` | 🟠 Majeure | Le scraper "avancé" ne peut pas être exécuté tel quel. |
| 6 | Modules `nlp/`, `ocr/`, `search/`, `ml/` vides | 🟠 Majeure | Aucun moyen de tester l'ETL. |
| 7 | KPIs `taux_reussite_ocr_pct`, `trends`, `top-buyers` (4 au lieu de 10) | 🟠 Majeure | Tableau de bord peu crédible. |
| 8 | Deux frontends en parallèle | 🟡 Mineure | Confusion, mais pas bloquant si on supprime le vanilla. |
| 9 | Pas de tests (`tests/` vide) | 🟡 Mineure | Pas de filet de sécurité. |
| 10 | `docs/installation.md` vide | 🟡 Mineure | Jury ne peut pas relancer le projet. |

---

## 4. Stratégie globale

**Décision d'architecture recommandée** : **SQLite via SQLAlchemy en POC** (chemin le plus court vers une démo fonctionnelle), avec une couche d'abstraction `repository.py` qui permettra de basculer vers PostgreSQL en prod sans toucher aux endpoints.

**Justification** :
- 12 AO déjà en base SQLite.
- `docker-compose.yml` est présent mais pas critique pour la démo locale.
- SQLAlchemy + SQLite est supporté nativement par SQLAlchemy 2.0.
- Tous les modèles `models.py` doivent être **réécrits sans types PostgreSQL-spécifiques** (`TSVECTOR`, `ARRAY`) pour la voie SQLite, ou bien on garde PostgreSQL et on adapte.

**Recommandation finale** : **PostgreSQL via Docker, car :**
1. `docker-compose.yml` est déjà écrit.
2. Les modèles sont déjà propres en PostgreSQL.
3. Le jury appréciera la rigueur (un POC SQLite aurait l'air d'un fallback).
4. Le `FTS` PostgreSQL est documenté et plus crédible qu'un `LIKE`.

**Mais** : pour ne pas perdre de temps, on garde un **fallback SQLite** via variable d'environnement `DATABASE_URL=sqlite:///ged.db` activé par défaut, basculable sur PostgreSQL pour la démo finale.

---

## 5. Plan d'action détaillé

> **Format** : pour chaque phase → **Objectif**, **Livrables**, **Étapes numérotées**, **Critères d'acceptation**, **Estimation**.

---

### 🟢 PHASE 0 — Fondations & alignement (½ journée)

**Objectif** : poser les bases du refactoring sans casser ce qui marche.

| # | Étape | Détail | Sortie |
|---|---|---|---|
| 0.1 | Sauvegarder l'état actuel | `git checkout -b refactoring-unify-db` | Branche de travail |
| 0.2 | Documenter l'audit | `docs/AUDIT_TECHNIQUE.md` (ce document) | Doc versionnée |
| 0.3 | Décider SQLite vs PostgreSQL | Documenter le choix dans `docs/Note_Decision_V1.md` | Note signée |
| 0.4 | Créer `tests/` squelette | `tests/__init__.py`, `tests/conftest.py`, `tests/test_smoke.py` | Structure pytest |
| 0.5 | Créer `docs/CHANGELOG.md` | Tracer chaque refactoring | Historique |
| 0.6 | Compléter `.gitignore` | Ajouter `.env`, `*.db-journal`, `__pycache__`/ racine | Propreté repo |
| 0.7 | Compléter `requirements.txt` | Ajouter `playwright==1.47.0`, `alembic==1.13.2`, `python-multipart` (déjà présent), `pytest-asyncio` | Dépendances fixes |

**Critère d'acceptation** : `pytest tests/test_smoke.py` passe, `git status` propre.

**Estimation** : 3–4 heures.

---

### 🟠 PHASE 1 — Unification de la couche données (1,5 jours)

**Objectif** : une seule source de vérité, une seule API pour y accéder.

| # | Étape | Détail | Fichier(s) cible(s) |
|---|---|---|---|
| 1.1 | Réécrire `models.py` compatible SQLite | Remplacer `TSVECTOR` par `Text`, `ARRAY` par JSON sérialisé, conserver tous les champs métier. Ajouter `date_parution`, `date_limite`, `reference`, `region`, `montant` typé. | `backend/models.py` |
| 1.2 | Réécrire `database.py` | Détecter `DATABASE_URL`. Si vide ou commence par `sqlite:`, utiliser `sqlite:///./ged.db`. Sinon PostgreSQL. Créer un `Base` unique. | `backend/database.py` |
| 1.3 | Créer un repository unique | `backend/repository.py` avec `MarcheRepository`, `DocumentRepository`, `OcrLogRepository` (CRUD + recherche FTS). Toute la logique SQL y vit, `main.py` ne contient plus de `sqlite3.connect`. | `backend/repository.py` (nouveau) |
| 1.4 | Réécrire `main.py` | Remplacer **tous** les `sqlite3.connect` par `Depends(get_db)` + `repository`. Conserver la même signature d'API. Ajouter endpoints manquants : `GET /api/v1/ged/appels-offres/{numero}`, `GET /api/v1/ged/appels-offres` avec filtres. | `backend/main.py` |
| 1.5 | Réécrire `init_db.py` | Utiliser `Base.metadata.create_all`, plus d'import `AppelOffre`. Idempotent. | `backend/init_db.py` |
| 1.6 | Configurer Alembic | `alembic init alembic`, créer la 1ʳᵉ migration `0001_init.py` à partir de `models.py`. | `alembic/` (nouveau) |
| 1.7 | Corriger `populate_db.py` | Pointer `/api/v1/ged/appels-offres`, ajouter les 12 AO existants + 18 nouveaux. | `scripts/populate_db.py` |
| 1.8 | Supprimer les doublons | `scripts/init_db.py` (doublon), `frontend/` (vanilla, après bascule). | — |
| 1.9 | Tests d'intégration BDD | `tests/test_repository.py` : créer, lire, mettre à jour un AO. | `tests/test_repository.py` |

**Critères d'acceptation** :
- `uvicorn backend.main:app` démarre sans warning.
- `GET /api/v1/ged/appels-offres` retourne les 12 AO existants.
- `POST /api/v1/ged/appels-offres` crée un AO et `GET` le retrouve.
- `pytest tests/test_repository.py` passe (3+ tests).
- `alembic upgrade head` crée le schéma sans erreur.

**Estimation** : 1,5 jour ouvré.

---

### 🟠 PHASE 2 — Pipeline d'ingestion bout-en-bout (1,5 jours)

**Objectif** : `Upload → save → extract → OCR → NLP → BDD` fonctionne réellement.

| # | Étape | Détail | Fichier(s) cible(s) |
|---|---|---|---|
| 2.1 | Déplacer la logique d'extraction | Sortir `read_pdf`, `read_docx`, `extract_nlp_regex` de `ingestion/extractor.py` vers `ocr/extract_native.py`, `ocr/extract_ocr.py` et `nlp/extract_entities.py`. Garder `extractor.py` comme orchestrateur. | `ocr/`, `nlp/` |
| 2.2 | Brancher l'upload | Dans `main.py`, créer `_process_upload(file_path, marche_id)` qui appelle l'orchestrateur. Utiliser `BackgroundTasks` (déjà importé) + `asyncio.create_task` ou thread. | `backend/main.py` |
| 2.3 | Sauvegarde disque | Stocker le fichier uploadé dans `data/raw/{numero_ordre}.zip` (ou UUID si pas encore d'AO lié). | `backend/main.py` |
| 2.4 | Pipeline asynchrone réel | `POST /api/v1/ged/documents/upload` crée un `Document` (`status='raw_zip'`) + `BackgroundTask` qui : (1) extrait le ZIP, (2) appelle `extractor.process_archive`, (3) met à jour `Document.status='ocr_processed'`, (4) insère un `OcrLog` avec `confidence_score_avg`. | `backend/main.py` + nouveau `backend/tasks.py` |
| 2.5 | Endpoint de progression | `GET /api/v1/ged/documents/{id}/status` retourne `status` + dernière log. Le frontend l'interroge toutes les 2 s. | `backend/main.py` |
| 2.6 | Compléter `nlp/extract_entities.py` | Ajouter extraction de `date_parution` (regex `(\d{1,2}\s+\w+\s+\d{4})` + `dateparser`), `date_limite` (regex `date limite.*?(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})`), `region` (liste de villes marocaines), `reference` (regex `R[éé]f[éerence]*\s*:\s*(\S+)`). | `nlp/extract_entities.py` |
| 2.7 | Activer spaCy | Charger `fr_core_news_sm` (modèle à installer via `python -m spacy download fr_core_news_sm`). Utiliser `doc.ents` pour extraire `ORG` (maitre_ouvrage), `LOC` (ville), `MONEY` (estimation). | `nlp/extract_entities.py` |
| 2.8 | Traçabilité | Chaque champ extrait enregistre `(valeur, source: regex/spacy, score, raw_text_snippet)` dans `extractions_nlp` (table déjà créée, à utiliser). | `nlp/extract_entities.py` |
| 2.9 | Tests pipeline | `tests/test_pipeline.py` : uploader un ZIP de test (5 ko, 1 PDF + 1 DOCX minimal), attendre `status='ocr_processed'`, vérifier qu'un AO est créé. | `tests/test_pipeline.py` |

**Critères d'acceptation** :
- Un upload via `curl -F file=@test.zip http://localhost:8000/api/v1/ged/documents/upload` crée un `Document` puis un `Marche` correspondant.
- `OcrLog` est créé avec `confidence_score_avg` réel (non nul).
- `GET /api/v1/ged/documents/{id}/status` retourne `ocr_processed` après 10–20 s.
- `extractions_nlp` contient ≥ 1 ligne par champ extrait.

**Estimation** : 1,5 jour ouvré.

---

### 🟡 PHASE 3 — Données réelles & dataset de démo (1 jour)

**Objectif** : peupler la BDD avec 30–50 AO réels et disposer d'un dataset reproductible.

| # | Étape | Détail | Fichier(s) cible(s) |
|---|---|---|---|
| 3.1 | Ajouter `playwright` aux dépendances | `pip install playwright==1.47.0 && playwright install chromium` | `requirements.txt` |
| 3.2 | Script de collecte démo | `scripts/collect_demo_dataset.py` : prend N AO depuis le scraper batch, télécharge les ZIP, stocke dans `data/raw/`, logge les `numero_ordre`. | `scripts/collect_demo_dataset.py` |
| 3.3 | Script d'ingestion démo | `scripts/ingest_dataset.py` : pour chaque ZIP, appelle `POST /api/v1/ged/documents/upload`. | `scripts/ingest_dataset.py` |
| 3.4 | Lancer la collecte | Cible : 30 AO minimum, en stockant dans `data/samples/` (commit autorisé pour 3–5 fichiers choisis). | — |
| 3.5 | Créer `data/samples/README.md` | Expliquer la provenance, licence, anonymisation. | `data/samples/README.md` |
| 3.6 | Commit sélectif | Garder 3–5 ZIP représentatifs (variété de catégories, qualité OCR). | — |

**Critères d'acceptation** :
- ≥ 30 AO en BDD avec champs `objet`, `maitre_ouvrage`, `estimation_mad` renseignés.
- 3–5 ZIP d'exemple versionnés dans `data/samples/`.
- Script reproductible : `python scripts/collect_demo_dataset.py && python scripts/ingest_dataset.py` → 30 AO en BDD.

**Estimation** : 1 jour (dont ½ journée pour le scraping réel).

---

### 🟠 PHASE 4 — Dashboard décisionnel (1,5 jours)

**Objectif** : les 6 KPIs du plan sont calculés depuis la BDD, plus aucune valeur hardcodée.

| # | Étape | Détail | Endpoint |
|---|---|---|---|
| 4.1 | `taux_reussite_ocr_pct` réel | `SELECT 100.0 * SUM(CASE WHEN confidence_score_avg > 70 THEN 1 ELSE 0 END) / COUNT(*) FROM ocr_logs` | `GET /api/v1/analytics/kpis` |
| 4.2 | Top 10 acheteurs | `LIMIT 10` au lieu de `LIMIT 4` | `GET /api/v1/analytics/top-buyers` |
| 4.3 | Volume par période | Agréger `marches` par `strftime('%Y-%m', date_publication)` (SQLite) ou `date_trunc('month', date_publication)` (PostgreSQL). | `GET /api/v1/analytics/trends` (refactor) |
| 4.4 | Volume par catégorie + période | `GROUP BY categorie, month`. | `GET /api/v1/analytics/trends/by-category` |
| 4.5 | Délai moyen publication → date limite | `(date_limite - date_publication) AVG` par catégorie. | `GET /api/v1/analytics/delai-moyen` |
| 4.6 | Répartition par type | Déjà OK. Ajouter `pie chart` propre dans React. | `GET /api/v1/analytics/distribution/categories` |
| 4.7 | Refactor du frontend Dashboard | Consommer les nouvelles routes, supprimer les valeurs en dur. | `frontend-react/src/components/Dashboard.jsx` |
| 4.8 | Tests d'agrégation | `tests/test_analytics.py` : injecter 3 AO factices, vérifier les sommes. | `tests/test_analytics.py` |

**Critères d'acceptation** :
- `taux_reussite_ocr_pct` change quand on injecte un `OcrLog` avec score 30.
- `top-buyers` retourne 10 entrées.
- `trends` affiche 6–12 mois selon la plage de données.
- `delai-moyen` retourne un nombre réel ou `null` si pas de données.

**Estimation** : 1,5 jour ouvré.

---

### 🟠 PHASE 5 — Page détail document & recherche (1 jour)

**Objectif** : un utilisateur peut cliquer sur un AO dans la recherche et voir son texte OCR + ses champs extraits.

| # | Étape | Détail | Fichier(s) cible(s) |
|---|---|---|---|
| 5.1 | Endpoint détail | `GET /api/v1/ged/appels-offres/{numero_ordre}` retourne AO + `OcrLog.raw_text_extracted` + `Document.storage_path`. | `backend/main.py` |
| 5.2 | Composant `DocumentDetail.jsx` | Affiche : titre, organisme, catégorie, KPIs, **texte OCR complet dans un onglet**, **champs extraits avec score**, lien vers PDF source. | `frontend-react/src/components/DocumentDetail.jsx` (nouveau) |
| 5.3 | Route React | `react-router-dom` (à ajouter) ou state-based navigation. | `frontend-react/src/App.jsx` |
| 5.4 | Pagination + filtres dans SearchFTS | `page`, `page_size`, filtres `ville`, `organisme`, `categorie`, `date_min`, `date_max`. Backend : `LIMIT/OFFSET` + `WHERE`. | `SearchFTS.jsx` + `main.py` |
| 5.5 | Endpoint liste paginée | `GET /api/v1/ged/appels-offres?page=1&page_size=20&ville=Casablanca`. | `backend/main.py` |
| 5.6 | Upload avec progression réelle | `Upload.jsx` interroge `/status` toutes les 2 s, affiche la vraie progression. | `Upload.jsx` |

**Critères d'acceptation** :
- Cliquer sur un résultat de recherche ouvre la page détail.
- Le texte OCR est visible et lisible (avec redaction des espaces).
- La pagination fonctionne (page 1/2/3).
- L'upload affiche `ocr_processed` en vrai.

**Estimation** : 1 jour ouvré.

---

### 🟠 PHASE 6 — ML baseline (1,5 jours)

**Objectif** : un modèle TF-IDF + SVM qui classifie la catégorie d'un AO, sérialisé et accessible via l'API.

| # | Étape | Détail | Fichier(s) cible(s) |
|---|---|---|---|
| 6.1 | Préparer les features | `ml/features.py` : vectorisation TF-IDF sur le champ `objet` concaténé avec `methode_notation`. Stop words français. | `ml/features.py` |
| 6.2 | Script d'entraînement | `ml/train_classifier.py` : charge 30+ AO depuis la BDD, split 80/20, entraîne `SVC(probability=True)`, sérialise avec `joblib.dump`. | `ml/train_classifier.py` |
| 6.3 | Script d'inférence | `ml/predict.py` : `joblib.load`, `predict_proba`. | `ml/predict.py` |
| 6.4 | Brancher sur l'API | `POST /api/v1/ged/appels-offres` appelle `ml/predict.py` en fin de création, insère un `MlInsight` avec `predicted_categorie`, `classification_confidence`. | `backend/main.py` |
| 6.5 | Endpoint prédiction réel | `GET /api/v1/ml/predictions/{marche_id}` : lit `MlInsight` (déjà codé, ligne 270) — vérifier qu'il est alimenté. | — |
| 6.6 | Détection d'anomalies simple | `ml/anomaly.py` : `IsolationForest` sur `[estimation_mad, delai_mois, caution_mad]`. Score < seuil = anomalie. | `ml/anomaly.py` |
| 6.7 | Endpoint anomalies réel | `GET /api/v1/ml/anomalies` : retourne la liste des `MlInsight.is_anomaly=True`. | `backend/main.py` |
| 6.8 | `POST /api/v1/ml/retrain` réel | `BackgroundTask` qui appelle `train_classifier.py`. | `backend/main.py` |
| 6.9 | Notebook de présentation | `ml/notebook_demo.ipynb` : load, train, evaluate, confusion matrix. | `ml/notebook_demo.ipynb` |
| 6.10 | Tests ML | `tests/test_ml.py` : prédire un AO factice, vérifier le format de sortie. | `tests/test_ml.py` |

**Critères d'acceptation** :
- `python -m ml.train_classifier` produit `ml/models/classifier.joblib` + métriques affichées.
- Après ingestion d'un nouvel AO, `MlInsight` est créé automatiquement.
- `GET /api/v1/ml/anomalies` retourne au moins les 12 AO existants.
- Le notebook s'exécute sans erreur.

**Estimation** : 1,5 jour ouvré.

---

### 🟢 PHASE 7 — Tests & qualité (1 jour)

**Objectif** : filet de sécurité minimum pour la démo.

| # | Étape | Détail | Fichier(s) cible(s) |
|---|---|---|---|
| 7.1 | Test smoke | `tests/test_smoke.py` : `GET /` (200), `GET /api/v1/analytics/kpis` (200). | — |
| 7.2 | Test API complet | `tests/test_api.py` : couvre les 19 endpoints, fixtures `client` + `db`. | — |
| 7.3 | Test pipeline (déjà 2.9) | à enrichir : cas d'erreur, ZIP corrompu. | — |
| 7.4 | Test ML (déjà 6.10) | à enrichir : cas `confidence < 0.5`. | — |
| 7.5 | Test NLP | `tests/test_nlp.py` : passer un texte connu, vérifier que `objet` et `maitre_ouvrage` sont extraits. | — |
| 7.6 | Coverage | `pytest --cov=backend --cov=nlp --cov=ocr --cov=ml --cov-report=term-missing` ≥ 60 %. | — |
| 7.7 | CI locale | Script `scripts/run_all_tests.sh` qui : lint + tests + alembic upgrade + smoke. | `scripts/run_all_tests.sh` |

**Critères d'acceptation** :
- `pytest` passe en < 30 s.
- Coverage ≥ 60 % sur les modules métier.

**Estimation** : 1 jour ouvré.

---

### 🟢 PHASE 8 — Documentation & livrables (1,5 jours)

**Objectif** : tout ce que le jury doit voir est lisible, à jour, reproductible.

| # | Étape | Détail | Fichier(s) cible(s) |
|---|---|---|---|
| 8.1 | `docs/installation.md` | Pas-à-pas : prérequis, `pip install -r requirements.txt`, `playwright install`, `alembic upgrade head`, `uvicorn backend.main:app`, `cd frontend-react && npm install && npm run dev`. Inclure la bascule PostgreSQL. | `docs/installation.md` (remplir le fichier vide) |
| 8.2 | `docs/user_guide.md` | Démo 5 minutes : ouvrir le dashboard, faire une recherche, ouvrir un AO, lancer un retrain ML. Captures d'écran. | `docs/user_guide.md` (nouveau) |
| 8.3 | `docs/architecture.md` | Schéma ASCII des 4 couches, flux de données, choix techniques justifiés. | `docs/architecture.md` (nouveau) |
| 8.4 | Compléter `docs/realisations/` | Ajouter un README par module (déjà partiellement fait) + dates de finalisation. | `docs/realisations/` |
| 8.5 | `README.md` racine | Refondre : titre, badges, GIF démo, architecture, quickstart, liens vers docs/, statut. | `README.md` |
| 8.6 | Rapport de stage | 30–50 pages : contexte, problématique, état de l'art, conception, réalisation, résultats, perspectives. Captures dashboard, courbes ML, logs OCR. | `docs/Rapport_Stage.pdf` |
| 8.7 | Slides soutenance | 12–15 slides : pitch 30 s, démo 5 min, technique 5 min, bilan 2 min, Q&A. | `docs/Slides_Soutenance.pdf` |
| 8.8 | Scénario démo | `docs/Scenario_Demo.md` : script minute par minute, qui parle, qui clique. | `docs/Scenario_Demo.md` (nouveau) |

**Critères d'acceptation** :
- Un externe peut cloner le repo, suivre `installation.md`, et reproduire la démo en < 15 minutes.
- Les slides sont prêtes.
- Le rapport est relu, sans faute, avec une conclusion qui assume les écarts.

**Estimation** : 1,5 jour ouvré.

---

### 🟢 PHASE 9 — Polish final & soutenance (½ journée)

| # | Étape | Détail |
|---|---|---|
| 9.1 | Vérifier la démo end-to-end | Scénario minute par minute, sur machine vierge. |
| 9.2 | Capturer les screenshots clés | Dashboard, recherche, détail, monitoring. |
| 9.3 | Répéter la présentation | 3 répétitions chronométrées. |
| 9.4 | Anticiper les questions | Tableau Q&A : "Pourquoi pas PostgreSQL en prod ?", "Pourquoi spaCy et pas LLM ?", "Quelle volumétrie visée ?". |

---

## 6. Planning consolidé (8 jours ouvrés)

```
Jour 1        : Phase 0 (½ j) + Phase 1 (½ j début)
Jour 2        : Phase 1 (fin) + tests
Jour 3        : Phase 2 (1,5 j) — pipeline bout-en-bout
Jour 4        : Phase 2 (fin) + Phase 3 (collecte dataset)
Jour 5        : Phase 3 (fin) + Phase 4 (KPIs)
Jour 6        : Phase 4 (fin) + Phase 5 (page détail)
Jour 7        : Phase 6 (ML) + Phase 7 (tests)
Jour 8        : Phase 7 (fin) + Phase 8 (doc)
Jour 9        : Phase 8 (fin slides) + Phase 9 (répétitions)
```

**Marge** : 1 jour (le rapport évoque 8 semaines, l'effort estimé ici est ~9 jours pour atteindre une démo soutenable).

---

## 7. Risques & parades

| Risque | Probabilité | Parade |
|---|---|---|
| Le scraper ASP.NET change de structure | Moyenne | Avoir 12 AO déjà seedés ⇒ la démo ne dépend pas du scraping temps réel. |
| `playwright` ne s'installe pas (réseau) | Moyenne | `pip install playwright` avec proxy + `playwright install --with-deps chromium`. |
| Tesseract absent sur la machine jury | Faible | Tester sur la machine cible au préalable ; sinon fournir un PDF textuel dans `data/samples/`. |
| spaCy fr_core_news_sm manquant | Moyenne | `python -m spacy download fr_core_news_sm` en post-install, documenter. |
| Démo en direct plante | Élevée | Avoir une vidéo de secours (Loom) + script qui rejoue les étapes sans intervention. |
| Le jury demande un POC PostgreSQL | Élevée | Préparer un `docker-compose.yml` propre + tester la bascule avant la soutenance. |

---

## 8. Indicateurs de succès (pour la démo)

| KPI | Avant | Objectif |
|---|---|---|
| Endpoints fonctionnels sans mock | 11 / 19 | **19 / 19** |
| Lignes en BDD | 12 | **≥ 30** |
| Documents OCR + NLP traités en live | 0 | **≥ 5 pendant la démo** |
| `taux_reussite_ocr_pct` calculé | hardcodé 98.5 | **calculé depuis `ocr_logs`** |
| Top acheteurs | 4 | **10** |
| Modèle ML entraîné et sérialisé | aucun | **`classifier.joblib` + notebook** |
| Tests pytest | 0 | **≥ 15** |
| Coverage | 0 % | **≥ 60 %** |
| Slides + rapport | incomplets | **finalisés** |

---

## 9. Points forts à conserver (valorisables en soutenance)

1. **Le scraper Playwright** est robuste et bien testé (pagination ASP.NET, anti-doublons). C'est un atout technique réel.
2. **La stratégie OCR fallback** (PyMuPDF → Tesseract) est mature et documentée. La slide "Pourquoi deux moteurs ?" est forte.
3. **L'interface React** est professionnelle. Une fois branchée sur de vraies données, elle suffit à porter la démo.
4. **Le découpage en modules** (mêmes s'ils sont vides) montre une intention d'architecture que le jury appréciera une fois remplie.
5. **L'honnêteté du rapport d'avancement** est en soi un point fort. L'exposé peut assumer les 30 % NLP restants comme un choix de périmètre (POC ≠ produit industriel).

---

## 10. Conclusion

Le projet est à **mi-parcours sur le plan technique** mais à **90 % sur la valeur démontrable** : ce qui est difficile (scraping ASP.NET, OCR fallback, UI moderne) est fait, ce qui est trivial mais long (brancher la pipeline, peupler la BDD, brancher le ML) reste à faire.

**Effort total estimé** : 8–9 jours ouvrés pour atteindre une démo soutenable.

**Priorité nº 1 absolue** : **Phase 1 + Phase 2** (1+1,5 = 2,5 jours). Sans unification de la BDD et sans pipeline branché, **aucune démo n'est possible**. Tout le reste en dépend.

**Priorité nº 2** : **Phase 4 (KPIs réels)**. C'est ce qui transforme l'UI déjà belle en dashboard convaincant.

**Priorité nº 3** : **Phase 6 (ML baseline)**. Le jury s'attend à du ML, même modeste.

**Priorité nº 4** : **Phase 8 (doc)**. Le rapport et les slides sont notés.

---

*Fin de l'analyse — voir `docs/CHANGELOG.md` pour le suivi d'exécution.*
