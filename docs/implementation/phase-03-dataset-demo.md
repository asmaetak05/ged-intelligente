# Phase 3 — Données réelles & dataset de démo

> **Effort** : 1 journée · **Risque** : moyen (dépend du scraping ASP.NET) · **Pré-requis** : Phase 2 terminée

---

## T3.1 — Installer Playwright et ses dépendances

**Description & objectif** : rendre le scraper batch réellement exécutable.

**Modifications** :

| Module | Action | Détail |
|---|---|---|
| `repo` | `CMD` | `playwright install chromium` |
| `repo` | `CMD` | `playwright install-deps chromium` (sur Linux ; sur Windows : `playwright install --with-deps chromium`) |
| `repo` | `CMD` | `python -c "from playwright.sync_api import sync_playwright; print('OK')"` |

**Plan de vérification** :
- [ ] L'import ci-dessus ne lève pas d'exception.
- [ ] Le binaire `chromium-XXXX` est présent dans `~/.cache/ms-playwright/`.

---

## T3.2 — Documenter le script de collecte démo

**Description & objectif** : avoir une procédure reproductible pour récupérer 30–50 AO réels.

**Modifications** :

| Module | Action | Détail |
|---|---|---|
| `scripts` | `NEW` | `scripts/collect_demo_dataset.py` :<br>1. Importe `ingestion.playwright_scraper_batch.collect(num_ao=50)`<br>2. Boucle avec barre de progression `tqdm`<br>3. Stocke les ZIP dans `data/raw/{numero_ordre}.zip`<br>4. Logge dans `data/raw/_collect.log` : `numero_ordre, source_url, downloaded_at, file_size`<br>5. En cas d'erreur, logge et continue |

**Plan de vérification** :
- [ ] `python scripts/collect_demo_dataset.py --num 5` télécharge 5 ZIP sans crash.
- [ ] `ls data/raw/*.zip | wc -l` → 5.

---

## T3.3 — Documenter le script d'ingestion démo

**Description & objectif** : injecter les ZIP collectés dans l'API, en s'arrêtant si l'API n'est pas dispo.

**Modifications** :

| Module | Action | Détail |
|---|---|---|
| `scripts` | `NEW` | `scripts/ingest_dataset.py` :<br>1. `for zip_path in glob('data/raw/*.zip'):`<br>2.   `requests.post('http://localhost:8000/api/v1/ged/documents/upload', files={'file': open(zip_path, 'rb')})`<br>3.   `time.sleep(1)` (rate limit)<br>4. Vérifie `requests.get('http://localhost:8000/api/v1/ged/appels-offres?page_size=1')` avant de commencer |
| `scripts` | `NEW` | `scripts/ingest_dataset_async.py` (variante) : utilise `httpx.AsyncClient` + `asyncio.gather` pour paralléliser 5 uploads simultanés. |

**Plan de vérification** :
- [ ] `python scripts/ingest_dataset.py` injecte tous les ZIP présents.
- [ ] `sqlite3 ged.db "SELECT count(*) FROM appels_offres"` augmente du nombre de ZIP.

---

## T3.4 — Lancer la collecte effective

**Description & objectif** : atteindre ≥ 30 AO en BDD avec champs métier remplis.

**Modifications** :

| Module | Action | Détail |
|---|---|---|
| `repo` | `CMD` | `python scripts/collect_demo_dataset.py --num 40 --out data/raw` (réseau requis) |
| `repo` | `CMD` | `python scripts/ingest_dataset.py` (l'API doit tourner) |
| `repo` | `CMD` | `sqlite3 ged.db "SELECT count(*) FROM appels_offres WHERE maitre_ouvrage IS NOT NULL"` ≥ 30 |

**Plan de vérification** :
- [ ] `count(*) >= 30`.
- [ ] Au moins 3 catégories différentes représentées.
- [ ] Taux de succès OCR > 50 % (sinon, le pipeline a un bug).

---

## T3.5 — Préparer un échantillon versionné

**Description & objectif** : commiter 3–5 ZIP représentatifs pour que la démo fonctionne sans réseau.

**Modifications** :

| Module | Action | Détail |
|---|---|---|
| `data` | `CMD` | `cp data/raw/AO_001.zip data/samples/AO_001_Travaux_Route.zip`<br>`cp data/raw/AO_002.zip data/samples/AO_002_Fournitures.zip`<br>`cp data/raw/AO_003.zip data/samples/AO_003_Services_Formation.zip`<br>`cp data/raw/AO_004.zip data/samples/AO_004_Etudes.zip`<br>`cp data/raw/AO_005.zip data/samples/AO_005_Travaux_Batiment.zip` |
| `data` | `NEW` | `data/samples/README.md` :<br>- Provenance : portail des marchés publics marocains<br>- Date de collecte : `<date>`<br>- Licence : usage pédagogique uniquement<br>- Anonymisation : `numero_ordre` modifiés, mais structure préservée |

**Plan de vérification** :
- [ ] `ls data/samples/*.zip | wc -l` → 5.
- [ ] `cat data/samples/README.md` est lisible.

---

## T3.6 — Tests d'ingestion de masse

**Description & objectif** : valider que le pipeline tient la charge sur 30 AO en séquence.

**Modifications** :

| Module | Action | Détail |
|---|---|---|
| `tests` | `NEW` | `tests/test_bulk_ingestion.py` (1 test) :<br>- `test_ingest_30_samples_in_sequence` :<br>  1. Crée 30 ZIP minimaux en mémoire<br>  2. Les POST un par un<br>  3. Attend 60 s<br>  4. Vérifie que 30 `Document` sont créés |
| `tests` | `MODIFY` | `tests/conftest.py` : fixture `bulk_zips` qui crée 30 ZIP factices. |

**Plan de vérification** :
- [ ] `pytest tests/test_bulk_ingestion.py -v` → 1 passed.
- [ ] Durée < 90 s.

---

## ✅ Critères de sortie de la Phase 3

- [ ] ≥ 30 AO en BDD avec `maitre_ouvrage`, `objet`, `categorie_marche` non nuls.
- [ ] 3–5 ZIP versionnés dans `data/samples/`.
- [ ] `data/samples/README.md` documenté.
- [ ] `python scripts/collect_demo_dataset.py && python scripts/ingest_dataset.py` est reproductible.

**Effort total** : 1 jour ouvré (dont ½ journée pour le scraping réel).
