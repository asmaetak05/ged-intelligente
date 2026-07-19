# 📘 Cahier de Texte — Spécifications Détaillées, Scénarios & Critères de Validation

> **Projet** : GED Intelligente — Gestion Électronique des Documents pour les marchés publics du Ministère de l'Équipement et de l'Eau du Maroc
> **Stage** : PFA (Projet de Fin d'Année), durée 2 mois
> **Organisme d'accueil** : Direction des Systèmes d'Information (DSI)
> **Documents sources** :
> - `01-evaluation-et-tests.md` (audit, scoring, tests existants)
> - `02-ameliorations-et-roadmap.md` (corrections, backlog, roadmap)
> - `PRESENTATION_PROJET.md` (vue d'ensemble du projet)
> - Code source : `backend/`, `frontend-react/`, `ingestion/`, `ocr/`, `nlp/`, `ml/`, `tests/`
> **Version** : 1.0 — Référentiel unique de validation pour la livraison

> 🎯 **Objectif** : fournir un document opérationnel, complet et sans ambiguïté décrivant **chaque scénario** à valider (pré-conditions, étapes, résultat attendu, critères de succès mesurables) afin de permettre (a) aux développeurs d'implémenter, (b) à l'équipe de test de valider, (c) à la DSI de recettever, (d) au jury de soutenance d'évaluer.

---

## Table des matières

1. [Contexte, périmètre & conventions](#1-contexte-périmètre--conventions)
2. [Architecture cible & modèle de données de référence](#2-architecture-cible--modèle-de-données-de-référence)
3. [Critères d'acceptation globaux (Definition of Done)](#3-critères-dacceptation-globaux-definition-of-done)
4. [Matrice de couverture fonctionnelle vs site source](#4-matrice-de-couverture-fonctionnelle-vs-site-source)
5. [Scénarios de test par couche](#5-scénarios-de-test-par-couche)
   - 5.1 [Couche Ingestion / Scraping](#51-couche-ingestion--scraping)
   - 5.2 [Couche OCR & PDF](#52-couche-ocr--pdf)
   - 5.3 [Couche NLP & Extraction](#53-couche-nlp--extraction)
   - 5.4 [Couche Recherche FTS](#54-couche-recherche-fts)
   - 5.5 [Couche Machine Learning](#55-couche-machine-learning)
   - 5.6 [Couche API REST](#56-couche-api-rest)
   - 5.7 [Couche Frontend / Écrans](#57-couche-frontend--écrans)
   - 5.8 [Couche Sécurité & Accès](#58-couche-sécurité--accès)
   - 5.9 [Couche Performance & Résilience](#59-couche-performance--résilience)
   - 5.10 [Couche DevOps / CI-CD / Observabilité](#510-couche-devops--ci-cd--observabilité)
   - 5.11 [Tests End-to-End (E2E)](#511-tests-end-to-end-e2e)
6. [Plan d'exécution des tests](#6-plan-dexécution-des-tests)
7. [Annexes](#7-annexes)

---

## 1. Contexte, périmètre & conventions

### 1.1 Contexte opérationnel

| Élément | Valeur |
|---|---|
| **Statut actuel** | PFA en phase de finalisation (≈ 75–80 % achèvement, cœur pipeline opérationnel) |
| **Stack backend** | Python 3.11+, FastAPI 0.139, SQLAlchemy 2.0, Alembic, SQLite (dev) / PostgreSQL (prod) |
| **Stack data** | spaCy `fr_core_news_sm`, Tesseract 5 (FR + AR), scikit-learn (SVM, IsolationForest), PyMuPDF |
| **Stack frontend** | React 19, Vite 8, Tailwind 4, Recharts, Axios, Lucide-React, react-router-dom 7 |
| **Modules livrés** | Ingestion, OCR, NLP regex, FTS LIKE, Dashboard basique, PredictorML, Monitoring, PipelineAdmin, Upload, Explorer, DocumentDetail, SearchFTS, LandingPage |
| **Modules manquants** | Auth, RBAC, Audit log, BI avancé, Cartographie, i18n FR/AR, MLOps, PWA |
| **Site source** | `http://appels-offres.equipement.gov.ma/recherche/criteres.aspx` (bloque les robots — captcha) |
| **Dataset de référence** | ~20 DAO collectés via Playwright (cf. `data/raw/`, `data/processed/`) |

### 1.2 Conventions de nommage des scénarios

| Code | Couche | Format |
|---|---|---|
| `ST-IN-NNN` | Ingestion / Scraping | `ST-IN-001` … |
| `ST-OC-NNN` | OCR / PDF | `ST-OC-001` … |
| `ST-NL-NNN` | NLP | `ST-NL-001` … |
| `ST-FT-NNN` | Full-Text Search | `ST-FT-001` … |
| `ST-ML-NNN` | Machine Learning | `ST-ML-001` … |
| `ST-API-NNN` | API REST | `ST-API-001` … |
| `ST-UI-NNN` | Frontend / UI | `ST-UI-001` … |
| `ST-AU-NNN` | Authentification | `ST-AU-001` … |
| `ST-SE-NNN` | Sécurité | `ST-SE-001` … |
| `ST-PE-NNN` | Performance | `ST-PE-001` … |
| `ST-E2E-NNN` | End-to-End | `ST-E2E-001` … |
| `ST-DQ-NNN` | Data Quality | `ST-DQ-001` … |

### 1.3 Niveaux de priorité

- 🔴 **P0** : bloquant, à passer **avant** toute mise en production.
- 🟠 **P1** : important, à passer **avant** la soutenance.
- 🟡 **P2** : amélioration, à passer en sprint suivant.

### 1.4 Statuts d'exécution

`PASS` · `FAIL` · `SKIP` · `BLOCKED` · `À_JOUR` (en cours d'écriture/exécution).

### 1.5 Légende des emojis

| Emoji | Signification |
|---|---|
| 🟢 Terrain | scénario à rejouer sur le site ministériel (validation finale impossible via captcha) |
| 🟡 Hybride | jouable en local avec snapshot HTML du site |
| 🔵 Labo | reproductible en environnement de test sans réseau externe |

---

## 2. Architecture cible & modèle de données de référence

### 2.1 Topologie (état cible MVP)

```
React 19 SPA (Vite + Tailwind)         Frontend
   │ Axios │ JWT
   ▼
FastAPI (REST + WebSocket)              Backend API
   │ SQLAlchemy 2.0
   ├──► PostgreSQL 15 + GIN/TSVector   Données + FTS
   ├──► MinIO / S3                     Stockage objet (PDF/ZIP)
   ├──► Redis                          Cache + File de tâches
   ├──► Celery worker                  Tâches async (OCR, NLP, ML)
   ├──► Playwright pool                Scraping
   ├──► Tesseract 5                    OCR FR + AR
   ├──► spaCy 3.8                      NLP
   ├──► scikit-learn 1.9               ML
   └──► Prometheus / Grafana           Observabilité
```

### 2.2 Modèle de données (référencement des colonnes du formulaire source)

| Champ formulaire source (cf. audit §2.3) | Colonne BDD | Type | Statut |
|---|---|---|---|
| Référence de l'avis | `marches.reference` + `marches.numero_appel_offre` | `String(100)`, `String(50) UNIQUE` | ✅ |
| Mots clés / Objet | `marches.titre_projet` (FTS) | `Text` | ✅ |
| Maître d'ouvrage (acheteur) | `marches.organisme_acheteur` | `String(255)` | ✅ |
| Direction / Service | ❌ nouvelle table `direction` + FK | `Integer FK` | ❌ À créer (ticket BDD-02) |
| Activité / Catégorie | `marches.categorie_prestation` | `Enum` | ✅ |
| Type d'avis (8 valeurs) | ❌ nouvelle colonne `typeavis_id` | `Integer FK` | ❌ À créer (BDD-01) |
| Type de procédure | ❌ colonne `procedure_id` | `Integer FK` | ❌ À créer (BDD-01) |
| Date de publication | `marches.date_parution` | `Date` | ✅ |
| Date d'ouverture des plis | ❌ colonne `date_ouverture_plis` | `DateTime` | ❌ À créer (BDD-01) |
| Date limite de remise des plis | `marches.date_limite` | `Date` (✅) + `date_limite_depot` (✅) | ✅ |
| Lieu d'exécution (région / province / ville) | `marches.ville_execution`, `marches.region` | `String(100)` | 🟡 Ville+region OK, province manquante |
| Qualifications requises | ❌ table `qualification` + `marche_qualification` | N:N | ❌ À créer (BDD-03) |
| Agréments requis | `marches.agreements_exiges` (JSON) | `JSON` | 🟡 Stockage OK, structure non normalisée |
| Estimation budgétaire (min/max) | `marches.montant` | `Numeric(15,2)` | 🟡 Pas de min/max en BDD |
| Caution provisoire (min/max) | `marches.caution_provisoire_mad` | `Numeric(15,2)` | 🟡 Pas de min/max |
| État de l'avis (5 valeurs) | ❌ colonne `etat_id` | `Integer FK` | ❌ À créer (BDD-01) |
| Source | ❌ table `source` | `Integer FK` | ❌ À créer (BDD-04) |
| Langue | ❌ colonne `langue` | `String(5)` | ❌ À créer (BDD-01) |
| Tri des résultats | côté API | query params | 🟡 API partielle, UI non exposée |
| Bouton « Rechercher » | `/api/v1/ged/search` + `appels-offres?q=` | — | ✅ |
| Bouton « Réinitialiser » | côté UI (filtres) | — | ❌ À créer (UI-04) |
| Bouton « Télécharger DAO (ZIP) » | `documents.storage_path` | `Text` | ✅ |
| Pagination | `repository.list(page, page_size)` | — | ✅ |

**Taux de couverture BDD : 13/23 ≈ 57 %** (cible 100 % MVP, 90 % pour la mise en production effective).

---

## 3. Critères d'acceptation globaux (Definition of Done)

| Domaine | Critère DoD | Mesure |
|---|---|---|
| **Fonctionnel** | 100 % des champs P0 du formulaire source sont filtrables + exportables | `pytest` + `npm test` + UI |
| **Tests unitaires** | ≥ 80 % de couverture (lignes) | `pytest --cov=backend --cov=ingestion --cov=ocr --cov=nlp --cov=ml` ≥ 80 % |
| **Tests E2E** | ≥ 20 scénarios Cypress/Playwright passent en CI | `npm run test:e2e` exit 0 |
| **Performance** | p95 latence `/api/v1/ged/search` < 500 ms sur 10 000 docs | `locust` ou `k6` |
| **Performance** | p95 latence `/api/v1/analytics/kpis` < 1 s | idem |
| **Sécurité** | 0 dépendance `HIGH` ou `CRITICAL` au `pip-audit` / `npm audit` | CI bloquante |
| **Sécurité** | Headers `Strict-Transport-Security`, `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, `Content-Security-Policy` présents sur `/` | test Playwright |
| **Accessibilité** | Score Lighthouse ≥ 90 sur Dashboard, SearchFTS, DocumentDetail | CI |
| **Documentation** | README + guide d'utilisation + doc API (OpenAPI) + guide de déploiement | `docs/` |
| **Observabilité** | Endpoint `/health` testant DB + Redis + stockage objet | curl |
| **Internationalisation** | FR complet + AR sur Landing, Dashboard, Search, DocumentDetail | test Cypress bilingue |
| **Auth** | JWT + RBAC opérationnels (3 rôles : reader / analyst / admin) | tests T-AU-*** |
| **i18n AR** | Direction RTL active, polices arabes chargées | test Cypress |

**Sprint de fermeture cible** : 3 à 4 semaines après la soutenance.

---

## 4. Matrice de couverture fonctionnelle vs site source

| Dimension site source | Couverture GED actuelle | Ticket de remédiation | Priorité | Critère de validation |
|---|---|---|---|---|
| Recherche par référence | ✅ | — | — | ST-FT-002 |
| Recherche par mots-clés | ✅ | — | — | ST-FT-001, ST-FT-003 |
| Maître d'ouvrage | ✅ | FTS-08 (alias) | P1 | ST-FT-008 |
| Activité / Catégorie | ✅ | FTS-12 (sous-cat) | P1 | ST-FT-014 |
| Type d'avis | ❌ | BDD-01, NLP-09, FTS-15 | **P0** | ST-NL-009, ST-FT-015 |
| Type de procédure | ❌ | BDD-01, NLP-09 | **P0** | ST-NL-009 |
| Date de publication | 🟡 | FTS-10 (étendu) | P1 | ST-FT-010 |
| Date d'ouverture des plis | ❌ | BDD-01, NLP-12 | **P0** | ST-NL-012, ST-FT-011 |
| Date limite de remise | 🟡 | FTS-12 (étendu) | P1 | ST-FT-012 |
| Lieu d'exécution (R/P/V) | 🟡 | BDD-05, FTS-08 | P1 | ST-NL-004, ST-FT-008 |
| Qualifications | ❌ | BDD-03, NLP-10 | **P0** | ST-NL-010, ST-FT-013 |
| Agréments | 🟡 | NLP-11 (normalisation) | P1 | ST-NL-011, ST-FT-014 |
| Estimation budgétaire min/max | 🟡 | FTS-09 | P1 | ST-FT-009 |
| Caution provisoire min/max | 🟡 | FTS-15 | P1 | ST-FT-015 |
| État de l'avis | ❌ | BDD-01, UI-09 | **P0** | ST-FT-016 |
| Source | ❌ | BDD-04, ING-08 | P1 | ST-API-008 |
| Langue | ❌ | BDD-01, NLP-14 | P1 | ST-NL-014, ST-FT-018 |
| Tri configurable | 🟡 | FTS-19, FTS-20, FTS-21 | P1 | ST-FT-019 |
| Réinitialisation | ❌ | UI-04 | **P0** | ST-UI-040 |
| Téléchargement DAO | ✅ | — | — | ST-API-006 |
| Pagination | ✅ | — | — | ST-FT-023 |
| Export CSV/Excel | ❌ | FTS-28, FTS-29 | **P0** | ST-FT-028, ST-FT-029 |
| Sauvegarde de recherche | ❌ | FTS-27 | P1 | ST-FT-027 |
| Alertes email | ❌ | UX-ALERT | P1 | ST-E2E-005 |

---

## 5. Scénarios de test par couche

### 5.1 Couche Ingestion / Scraping

> Fichiers de référence : `ingestion/playwright_scraper*.py`, `scripts/collect_demo_dataset.py`, `scripts/ingest_dataset.py`, `ingestion/extractor.py`.

#### ST-IN-001 — Lancement manuel du scraper depuis l'écran PipelineAdmin 🔴
| Champ | Détail |
|---|---|
| **Pré-conditions** | L'application est démarrée, l'écran PipelineAdmin est accessible, le script `scripts/collect_demo_dataset.py` est exécutable. |
| **Étapes** | 1. Cliquer sur l'écran « Pipeline Admin » dans la sidebar.<br>2. Saisir une plage de dates (ex. `2025-01-01` → `2025-01-31`).<br>3. Cliquer sur « Lancer le Scraping ».<br>4. Observer l'état du scraper et la jauge de progression. |
| **Résultat attendu** | - Statut passe à `En cours` sous 2 s.<br>- Bouton désactivé pendant l'exécution.<br>- Logs temps réel diffusés via WebSocket `/api/v1/system/ws/console`.<br>- À la fin : statut `Inactif`, compteur d'AO cohérent. |
| **Critère de succès** | Nombre d'AO collectés = nombre visible sur le site pour la même plage (± 2 % tolérance). **OU**, à défaut (captcha), ≥ 1 DAO collecté sans crash. |
| **Référence code** | `backend/main.py:631-671` (websocket_console), `scripts/collect_demo_dataset.py` |

#### ST-IN-002 — Scraping sans plage de dates 🟠
| Champ | Détail |
|---|---|
| **Pré-conditions** | PipelineAdmin ouvert. |
| **Étapes** | 1. Cliquer « Lancer le Scraping » sans saisir de dates. |
| **Résultat attendu** | Message d'erreur de validation « Veuillez saisir une plage de dates valide ». Le scraper ne se lance pas. |
| **Critère de succès** | Toast d'erreur visible, état reste `Inactif`, aucun script Python n'est invoqué. |
| **Référence code** | `frontend-react/src/components/PipelineAdmin.jsx` (validation client) |

#### ST-IN-003 — Plage de dates inversée 🔴
| **Étapes** | 1. Saisir `2025-03-01` → `2025-01-31`. |
| **Résultat attendu** | Erreur explicite : « La date de début doit précéder la date de fin ». Le scraper ne se lance pas. |
| **Critère de succès** | Validation côté client **et** côté serveur (le serveur renvoie 422 si requête API directe). |
| **Référence test** | `tests/test_pipeline.py` (à créer) |

#### ST-IN-004 — Scraping de plage étendue (≥ 1 an) 🟠
| **Pré-conditions** | Au moins 365 jours d'historique disponible sur le site. |
| **Étapes** | 1. Saisir `2024-01-01` → `2024-12-31`.<br>2. Lancer le scraping.<br>3. Observer la progression. |
| **Résultat attendu** | - Le scraper pagine correctement (≥ 10 pages).<br>- Aucune interruption sur timeout.<br>- Tous les fichiers ZIP sont téléchargés dans `data/raw/`.<br>- Déduplication inter-pages (clé `numero_appel_offre`). |
| **Critère de succès** | 0 doublon en BDD, 0 timeout non géré, durée totale < 30 min. |
| **Référence code** | `ingestion/playwright_scraper_batch.py` (pagination) |

#### ST-IN-005 — Reprise après crash du scraper 🔴
| **Étapes** | 1. Lancer un scraping de longue durée.<br>2. Tuer le process (`kill -9` ou Ctrl-C×2) à mi-parcours.<br>3. Relancer avec la même plage. |
| **Résultat attendu** | - Reprise depuis le dernier état stable.<br>- Aucun doublon en BDD.<br>- Logs de reprise visibles. |
| **Critère de succès** | Aucune entrée en double (`SELECT numero, COUNT(*) FROM marches GROUP BY numero HAVING COUNT(*) > 1` retourne 0 ligne). |
| **Référence implémentation** | Ticket ING-04 (checkpoint + reprise) |

#### ST-IN-006 — Téléchargement ZIP 🔴
| **Pré-conditions** | Au moins 1 AO disponible sur le site. |
| **Résultat attendu** | - Pour chaque AO, le ZIP contient CPS, RC, annexes.<br>- Archive sauvegardée dans `data/raw/AO_<numero>.zip`.<br>- Hash SHA-256 enregistré en BDD (`documents.checksum_sha256`, à créer via ticket BDD-01). |
| **Critère de succès** | Le fichier est lisible, taille > 0, hash = hash calculé sur le contenu. |

#### ST-IN-007 — Extraction des PDF depuis le ZIP 🟠
| **Résultat attendu** | - Chaque PDF est extrait dans `data/processed/`.<br>- Nommage stable : `{ref}_{type}.pdf`.<br>- Indexé en BDD avec chemin relatif. |
| **Critère de succès** | `ls data/processed/ | wc -l` ≥ nombre de fichiers attendus ; tous les chemins référencés en BDD existent. |

#### ST-IN-008 — Détection des doublons inter-exécutions 🟠
| **Étapes** | 1. Lancer un scraping sur la plage `P`.<br>2. Relancer immédiatement le même scraping. |
| **Résultat attendu** | - Aucun doublon créé.<br>- Temps d'exécution réduit (skip téléchargements).<br>- Logs indiquent « 0 nouveau document ». |
| **Critère de succès** | Compteur `INSERT INTO marches` du 2e run = 0. |

#### ST-IN-009 — Robustesse aux changements HTML du site 🔴
| **Méthode** | Snapshot HTML du site enregistré dans `tests/fixtures/portal_snapshot.html`. Exécution du scraper en mode `offline` (lecture du snapshot). |
| **Résultat attendu** | - Sélecteurs découplés (classe `SelectorLocator` injectable).<br>- Au moins 1 test d'intégration par champ extrait (référence, objet, montant, date). |
| **Critère de succès** | `pytest tests/test_scraper_snapshots.py` exit 0. |

#### ST-IN-010 — Comportement en cas d'indisponibilité du site 🟠
| **Méthode** | DNS blackhole (`/etc/hosts` → 127.0.0.1) ou mock httpx. |
| **Résultat attendu** | - Erreur HTTP capturée, message clair.<br>- Retry exponentiel (3 essais, backoff 1 s / 2 s / 4 s).<br>- Alerte après échec définitif (log ERROR + email optionnel). |
| **Critère de succès** | Pas de crash, message d'erreur explicite, 3 tentatives visibles dans les logs. |

#### ST-IN-011 — Pagination du site ministériel 🟠
| **Résultat attendu** | - Tous les résultats paginés sont parcourus.<br>- Marque de fin détectée (lien « Suivant » désactivé).<br>- Pas de boucle infinie. |
| **Critère de succès** | Compteur final ≥ 95 % des résultats affichés sur la dernière page manuellement. |

#### ST-IN-012 — Extraction de la référence AO 🔴
| **Résultat attendu** | La référence correspond exactement à celle publiée (regex stricte, normalisation Unicode). |
| **Critère de succès** | Sur 20 AO du dataset test, 100 % de matching exact. |

#### ST-IN-013 — Logging structuré des étapes de scraping 🟡
| **Résultat attendu** | Chaque étape (URL visitée, bouton cliqué, fichier reçu) est loggée avec horodatage ISO 8601 et `request_id` (ticket OBS-01). |
| **Critère de succès** | Format JSON Lines (`.jsonl`) exploitable par Loki/ELK. |

#### ST-IN-014 — Limitation de débit (rate limiting) 🟡
| **Résultat attendu** | Pas plus de 1 requête/seconde vers le site (politique de scraping responsable). |
| **Critère de succès** | `asyncio.sleep(1.0)` ou `aiolimiter` actif ; vérifiable via timestamps des requêtes. |

#### ST-IN-015 — Exécution parallèle contrôlée 🟡
| **Résultat attendu** | Possibilité de lancer 2 workers en parallèle, pas de conflit d'écriture en BDD (`SELECT ... FOR UPDATE` ou lock applicatif). |
| **Critère de succès** | `pytest tests/test_parallel_scraping.py` exit 0. |

---

### 5.2 Couche OCR & PDF

> Fichiers de référence : `ocr/extract_native.py`, `ocr/extract_ocr.py`, `ocr/preprocess.py`, `backend/models.py:OcrLog`.

#### ST-OC-001 — Détection PDF natif vs scanné 🔴
| **Fixture** | `tests/fixtures/pdf_natif.pdf` (texte sélectionnable, ≥ 50 caractères/page), `tests/fixtures/pdf_scanne.pdf` (image scannée). |
| **Résultat attendu** | - Natif : ratio texte/char ≥ seuil, chemin `extract_native` emprunté.<br>- Scanné : ratio < seuil, OCR déclenché. |
| **Critère de succès** | `assert detector.detect_type(pdf) == "natif"` pour le premier, `"scanne"` pour le second. |

#### ST-OC-002 — Extraction native (PyMuPDF) 🔴
| **Résultat attendu** | Texte extrait fidèle à l'original (distance Levenshtein normalisée ≥ 95 % vs référence humaine). |
| **Critère de succès** | `tests/test_ocr.py::test_extract_native_fidelity` PASS. |

#### ST-OC-003 — OCR sur PDF scanné en français 🔴
| **Résultat attendu** | Texte OCRisé, CER < 0,1 (Character Error Rate). |
| **Critère de succès** | Métrique calculée via `jiwer.cer` ou équivalent sur dataset de référence. |

#### ST-OC-004 — OCR sur PDF scanné en arabe 🟠
| **Résultat attendu** | Texte OCRisé en arabe, CER < 0,2 sur dataset arabe (seuil assoupli). |
| **Critère de succès** | Présence d'au moins 80 % de mots arabes attendus dans la sortie. |

#### ST-OC-005 — OCR sur PDF bilingue FR/AR 🟠
| **Résultat attendu** | Extraction des deux langues, séparateur logique présent (ex : `--- PAGE X : [FR] ... [AR] ...`). |
| **Critère de succès** | Détection automatique de la langue par page (`langdetect`). |

#### ST-OC-006 — Confiance OCR moyenne 🟠
| **Résultat attendu** | `OcrLog.confidence_score_avg` ∈ [0, 100], stocké par document. |
| **Critère de succès** | Tous les OcrLogs créés ont une valeur non-NULL et ∈ [0, 100]. |

#### ST-OC-007 — Prétraitement d'image 🟡
| **Fixture** | `tests/fixtures/image_contraste_faible.png`, `tests/fixtures/image_inclinee.png`. |
| **Résultat attendu** | Niveau de gris, binarisation, deskew appliqués (vérifier via hash d'image intermédiaire). |
| **Critère de succès** | Différence pixel par pixel entre l'image prétraitée et une image de référence ≤ 5 %. |

#### ST-OC-008 — Performance OCR par page 🟠
| **Résultat attendu** | < 5 s par page en moyenne (SLI Monitoring), alerte si > 10 s. |
| **Critère de succès** | `processing_time_ms` moyen < 5000 sur 50 pages test. |

#### ST-OC-009 — OCR sur PDF de 200+ pages 🟠
| **Résultat attendu** | Traitement complet sans crash mémoire (streaming PyMuPDF, batch OCR). |
| **Critère de succès** | Pic RAM < 2 Go, durée totale < 30 min. |

#### ST-OC-010 — Reprise OCR après crash 🔴
| **Résultat attendu** | Un document en cours d'OCR reprend à la dernière page traitée (checkpoint dans `documents.ocr_progress`, ticket BDD-01). |
| **Critère de succès** | Tuer le worker à la page 50, relancer, vérification que les pages 1-49 ne sont pas retraitée. |

#### ST-OC-011 — Caractères spéciaux et diacritiques 🟡
| **Résultat attendu** | Reconnaissance correcte des accents français (é, è, ê, à) et des caractères arabes (ﺍﻟﺸﺮﻛﺔ, ﷲ). |
| **Critère de succès** | CER < 0,05 sur échantillon de 50 phrases accentuées. |

#### ST-OC-012 — Tableaux et colonnes 🟡
| **Résultat attendu** | Structure tabulaire préservée (sortie texte avec séparateurs `|`, ou JSON structuré `{type: "table", cells: [...]}`). |
| **Critère de succès** | Au moins 1 tableau de référence restitué à 100 % des cellules. |

#### ST-OC-013 — OCR sur PDF chiffré / protégé 🟠
| **Résultat attendu** | Détection du chiffrement, message d'erreur explicite, pas de crash. |
| **Critère de succès** | `extract_ocr.process(pdf_chiffre)` lève `EncryptedPdfError` capturée. |

#### ST-OC-014 — Métriques qualité CER/WER 🟡
| **Résultat attendu** | Calcul automatique du CER/WER par page, agrégé par document, stocké dans `ocr_logs.metrics` (ticket BDD-01). |
| **Critère de succès** | `OcrLog.cer_pct` rempli pour 100 % des nouveaux OCR. |

#### ST-OC-015 — Multilinguisme actif 🟠
| **Résultat attendu** | Tesseract configuré avec `lang='fra+ara'`, les deux langues sont reconnues dans le même document. |
| **Critère de succès** | Texte FR et texte AR tous deux présents en sortie sur un PDF bilingue. |

---

### 5.3 Couche NLP & Extraction

> Fichiers de référence : `nlp/extract_entities.py`, `nlp/normalize.py`, `nlp/villes_maroc.py`.

#### ST-NL-001 — Extraction de la référence 🔴
| **Corpus** | 20 DAO réels du dataset de test (`data/processed/`). |
| **Résultat attendu** | ≥ 95 % de précision, ≥ 90 % de rappel. |
| **Critère de succès** | `tests/test_nlp.py::test_extract_reference` PASS. |

#### ST-NL-002 — Extraction de l'objet 🔴
| **Résultat attendu** | ≥ 90 % de précision, ≥ 85 % de rappel. |
| **Critère de succès** | L'objet retourné correspond au texte du champ « Objet : » du DAO. |

#### ST-NL-003 — Extraction du maître d'ouvrage 🔴
| **Résultat attendu** | ≥ 90 % de précision, ≥ 85 % de rappel (via spaCy NER + regex fallback). |
| **Critère de succès** | `marches.organisme_acheteur` non NULL et cohérent sur 18/20 DAO. |

#### ST-NL-004 — Extraction et normalisation de la ville d'exécution 🟠
| **Résultat attendu** | Ville correctement identifiée et normalisée (mapping `villes_maroc.py` + provinces Maroc). |
| **Critère de succès** | `marches.ville_execution` ∈ `VILLES_MAROC` ou dans la table `ville` (ticket BDD-05). |

#### ST-NL-005 — Extraction du montant estimé (MAD) 🔴
| **Corpus** | 20 DAO avec montants variables. |
| **Résultat attendu** | - « 1 234 567,89 DH » → `1234567.89`<br>- « un million deux cent mille dirhams » → `1200000`<br>- « 1,2 M MAD » → `1200000`<br>- Précision ≥ 95 %. |
| **Critère de succès** | `tests/test_nlp.py::test_extract_amount` PASS sur les 3 formats + 17 autres. |

#### ST-NL-006 — Extraction de la caution provisoire 🟠
| **Résultat attendu** | ≥ 90 % de précision, en MAD. |
| **Critère de succès** | `caution_provisoire_mad` correctement rempli. |

#### ST-NL-007 — Extraction du délai d'exécution 🟠
| **Résultat attendu** | - « 6 mois » → 6<br>- « 180 jours » → 6 (mois, normalisé)<br>- « 24 mois » → 24 |
| **Critère de succès** | Cohérence avec le champ `delai_execution_mois`. |

#### ST-NL-008 — Normalisation des dates en ISO 🔴
| **Résultat attendu** | - « 15/03/2024 » → `2024-03-15`<br>- « 15 mars 2024 » → `2024-03-15`<br>- « 15-03-24 » → `2024-03-15` (heuristique siècle). |
| **Critère de succès** | `tests/test_nlp.py::test_normalize_date` PASS sur 30 dates variées. |

#### ST-NL-009 — Extraction du type d'avis 🔴
| **Résultat attendu** | Classification en {Ouvert, Restreint, Simplifié, Présélection, Concours, Consultation architecturale, Dialogue compétitif, Bon de commande} avec ≥ 85 % de précision (P0 mais précision légèrement assouplie). |
| **Critère de succès** | Colonne `marches.typeavis_id` (FK vers `type_avis`) remplie sur ≥ 80 % des DAO. |
| **Référence implémentation** | Ticket NLP-09 + BDD-01 |

#### ST-NL-010 — Extraction des qualifications 🟠
| **Résultat attendu** | Identification des catégories (Qualification et Classification BTP, classes 1 à 6). |
| **Critère de succès** | Table `marche_qualification` (N:N) peuplée sur ≥ 50 % des DAO de travaux. |

#### ST-NL-011 — Extraction des agréments 🟠
| **Résultat attendu** | `agreements_exiges` structuré (liste de `{"type": ..., "classe": ...}`) au lieu d'une chaîne JSON libre. |
| **Critère de succès** | JSON valide parseable par `marches.agreements_exiges` (PostgreSQL JSONB). |

#### ST-NL-012 — Extraction de la date d'ouverture des plis 🟠
| **Résultat attendu** | Regex + heuristique (date + heure), ISO 8601. |
| **Critère de succès** | `marches.date_ouverture_plis` rempli sur ≥ 60 % des DAO. |

#### ST-NL-013 — Extraction de la date limite de remise 🟠
| **Résultat attendu** | Distinction claire avec date d'ouverture (`date_limite_depot` vs `date_ouverture_plis`). |
| **Critère de succès** | Les deux colonnes remplies, dates cohérentes (limite > ouverture). |

#### ST-NL-014 — Reconnaissance bilingue FR/AR sur les entités 🟠
| **Résultat attendu** | Extraction des entités depuis la version arabe du document. |
| **Critère de succès** | Au moins 70 % des champs-clés extraits sur un PDF 100 % arabe. |

#### ST-NL-015 — Score de confiance par entité 🟡
| **Résultat attendu** | Chaque entité a un score ∈ [0, 1] stocké dans `extractions_nlp.score`. |
| **Critère de succès** | 100 % des lignes de `extractions_nlp` ont un score non-NULL. |

#### ST-NL-016 — Robustesse aux fautes OCR 🟠
| **Méthode** | Injecter 5 % de bruit OCR simulé dans le texte (caractères substitués). |
| **Résultat attendu** | L'extraction reste stable (variation < 10 % sur les métriques). |
| **Critère de succès** | `tests/test_nlp.py::test_noise_robustness` PASS. |

#### ST-NL-017 — Détection de documents non conformes 🟠
| **Résultat attendu** | Flag `documents.low_quality = true` si < 3 entités extraites. |
| **Critère de succès** | `documents.low_quality` correctement positionné. |

#### ST-NL-018 — Idempotence de l'extraction 🟡
| **Résultat attendu** | Relancer l'extraction sur le même document produit exactement les mêmes résultats. |
| **Critère de succès** | `extractions_nlp` ne contient pas de doublons (UNIQUE(document_id, field_name)). |

#### ST-NL-019 — Performance NLP par document 🟡
| **Résultat attendu** | < 3 s par document (SLO). |
| **Critère de succès** | Mesure via `time.time()` sur 50 documents. |

#### ST-NL-020 — Audit des regex utilisées 🟡
| **Résultat attendu** | Tests unitaires sur ≥ 50 patterns d'extraction variés. |
| **Critère de succès** | `tests/test_nlp_patterns.py` contient ≥ 50 cas. |

#### ST-NL-021 — Reconnaissance des modèles d'avis 12 à 13-10 🟡
| **Résultat attendu** | Détection du modèle réglementaire d'avis (« Avis d'appel d'offres ouvert n° 12-10 », etc.). |
| **Critère de succès** | `marches.modele_reference` rempli quand détecté. |

---

### 5.4 Couche Recherche FTS

> Fichiers de référence : `backend/repository.py:MarcheRepository.search_fts`, `backend/main.py:/api/v1/ged/search`, `frontend-react/src/components/SearchFTS.jsx`.

#### ST-FT-001 — Recherche simple par mot-clé 🔴
| **Étapes** | Saisir « route » dans la barre de recherche et lancer. |
| **Résultat attendu** | Tous les documents contenant le mot « route » sont retournés. |
| **Critère de succès** | `count > 0` et tous les résultats contiennent « route » (vérification humaine). |

#### ST-FT-002 — Recherche par référence exacte 🟠
| **Étapes** | Saisir la référence complète d'un DAO (ex. « AO_001_2024 »). |
| **Résultat attendu** | Seul ce document est retourné, en première position. |
| **Critère de succès** | `count == 1` et `results[0].numero_appel_offre == ref`. |

#### ST-FT-003 — Recherche multi-mots 🔴
| **Étapes** | Saisir « pont métallique ». |
| **Résultat attendu** | Documents contenant les deux mots (ET logique par défaut). |
| **Critère de succès** | UI affiche un toggle AND/OR. |

#### ST-FT-004 — Recherche par phrase exacte 🟠
| **Étapes** | Saisir `"voie de contournement"` (avec guillemets). |
| **Résultat attendu** | Documents contenant l'expression exacte. |
| **Critère de succès** | `results[0]` contient la phrase. |

#### ST-FT-005 — Opérateurs booléens 🟠
| **Étapes** | Saisir `route ET (pont OU viaduc) NON ferroviaire`. |
| **Résultat attendu** | Résultats conformes à l'algèbre booléenne. |
| **Critère de succès** | Compteur cohérent à ± 5 % vs parser manuel. |

#### ST-FT-006 — Recherche floue (fuzzy) 🟡
| **Étapes** | Saisir « rout » (faute de frappe). |
| **Résultat attendu** | Suggestions et résultats incluant « route ». |
| **Critère de succès** | Ticket FTS-06 (pg_trgm) implémenté. |

#### ST-FT-007 — Autocomplétion 🟠
| **Résultat attendu** | Top 5 suggestions affichées sous 200 ms, basées sur l'historique et l'index. |
| **Critère de succès** | Latence p95 < 200 ms. |

#### ST-FT-008 — Filtre par ville 🔴
| **Résultat attendu** | Combinaison « route » + `ville=Casablanca` = résultats intersectés. |
| **Critère de succès** | `count(ville=Casa AND mot='route') == count retourné`. |

#### ST-FT-009 — Filtre par budget min/max 🔴
| **Étapes** | Saisir 1 000 000 → 5 000 000. |
| **Résultat attendu** | Seuls les AO dont le montant extrait est dans la plage. |
| **Critère de succès** | `montant BETWEEN 1e6 AND 5e6` vérifié en BDD. |

#### ST-FT-010 — Filtre par date de publication 🟠
| **Résultat attendu** | AO publiés dans la plage. |
| **Critère de succès** | `date_parution BETWEEN date_min AND date_max`. |

#### ST-FT-011 — Filtre par date d'ouverture des plis 🟠
| **Résultat attendu** | AO dont la date d'ouverture est dans la plage. |
| **Critère de succès** | Ticket BDD-01 + FTS-11. |

#### ST-FT-012 — Filtre par date limite de remise 🟠
| **Résultat attendu** | AO dont la date limite est dans la plage. |
| **Critère de succès** | `date_limite_depot BETWEEN date_min AND date_max`. |

#### ST-FT-013 — Filtre par qualifications 🟠
| **Résultat attendu** | AO requérant la qualification sélectionnée. |
| **Critère de succès** | `JOIN marche_qualification` correct. |

#### ST-FT-014 — Filtre par agréments 🟠
| **Résultat attendu** | AO requérant l'agrément sélectionné. |
| **Critère de succès** | Filtre JSON sur `agreements_exiges`. |

#### ST-FT-015 — Filtre par type d'avis 🟠
| **Résultat attendu** | AO du type sélectionné (Ouvert, Restreint, etc.). |
| **Critère de succès** | Ticket BDD-01 + FTS-15. |

#### ST-FT-016 — Filtre par état (En cours, Clôturé, Attribué, Annulé, Infructueux) 🟠
| **Résultat attendu** | AO dans l'état sélectionné. |
| **Critère de succès** | Filtre sur `etat_id` (BDD-01). |

#### ST-FT-017 — Filtre par maître d'ouvrage 🟠
| **Résultat attendu** | AO émis par l'organisme sélectionné. |
| **Critère de succès** | `organisme_acheteur ILIKE '%X%'`. |

#### ST-FT-018 — Filtre par langue 🟡
| **Résultat attendu** | AO dans la langue sélectionnée (FR / AR / Bilingue). |
| **Critère de succès** | Ticket BDD-01. |

#### ST-FT-019 — Tri des résultats (date desc) 🟠
| **Résultat attendu** | Résultats triés du plus récent au plus ancien. |
| **Critère de succès** | `ORDER BY date_parution DESC` actif. |

#### ST-FT-020 — Tri par montant 🟠
| **Résultat attendu** | Tri croissant ou décroissant. |
| **Critère de succès** | UI expose 3 tris : date, montant, pertinence. |

#### ST-FT-021 — Tri par pertinence 🟠
| **Résultat attendu** | Tri par score BM25 ou TF-IDF. |
| **Critère de succès** | Ticket FTS-21. |

#### ST-FT-022 — Surlignage des termes trouvés 🟠
| **Résultat attendu** | Dans la preview du résultat, les mots-clés sont surlignés (`<mark>route</mark>`). |
| **Critère de succès** | UI rend les `<mark>` en jaune Tailwind. |

#### ST-FT-023 — Pagination 🟠
| **Résultat attendu** | Taille de page 20, navigation fonctionnelle, dernière page détectée. |
| **Critère de succès** | UI affiche « Page 1 / N ». |

#### ST-FT-024 — Compteur de résultats 🔴
| **Résultat attendu** | « 142 résultats trouvés en 87 ms ». |
| **Critère de succès** | `took_ms` exposé en API et visible en UI. |

#### ST-FT-025 — Performance p95 🔴
| **Résultat attendu** | p95 latence < 500 ms pour 10 000 documents indexés. |
| **Critère de succès** | Ticket PE-003. |

#### ST-FT-026 — Bouton Réinitialiser 🔴
| **Résultat attendu** | Tous les filtres remis à zéro, résultats réinitialisés. |
| **Critère de succès** | Ticket UI-04. |

#### ST-FT-027 — Sauvegarde de recherche 🟡
| **Résultat attendu** | Possibilité d'enregistrer un set de filtres sous un nom. |
| **Critère de succès** | Table `saved_searches` + UI dédiée. |

#### ST-FT-028 — Export CSV des résultats 🔴
| **Résultat attendu** | Export conforme RGPD, encoding UTF-8, séparateur `,`. |
| **Critère de succès** | `GET /api/v1/ged/appels-offres/export?format=csv` retourne un fichier valide. |

#### ST-FT-029 — Export Excel 🟠
| **Résultat attendu** | Fichier `.xlsx` avec mise en forme (en-têtes gras, types). |
| **Critère de succès** | Ticket FTS-29. |

#### ST-FT-030 — Aucun résultat trouvé 🟠
| **Résultat attendu** | Message « Aucun résultat. Essayez d'élargir vos critères. » + suggestions. |
| **Critère de succès** | UI affiche un état vide avec CTA. |

#### ST-FT-031 — Recherche vide 🔴
| **Résultat attendu** | Le bouton est désactivé, ou un message demande confirmation. |
| **Critère de succès** | Pas de requête envoyée avec `q=""`. |

#### ST-FT-032 — Sécurité FTS (injection SQL) 🔴
| **Méthode** | Saisir `' OR 1=1 --` dans la barre de recherche. |
| **Résultat attendu** | Aucune injection possible (ORM paramétré). |
| **Critère de succès** | Réponse = 0 résultat (la chaîne littérale est recherchée). |

---

### 5.5 Couche Machine Learning

> Fichiers de référence : `ml/train_classifier.py`, `ml/predict.py`, `ml/anomaly.py`, `ml/features.py`, `backend/main.py:/api/v1/ml/*`.

#### ST-ML-001 — Entraînement SVM sur dataset d'entraînement 🔴
| **Résultat attendu** | Le modèle converge, accuracy > 80 % sur jeu de validation (assoupli par rapport aux 85 % cible). |
| **Critère de succès** | `tests/test_ml.py::test_train_svm` PASS. |

#### ST-ML-002 — Sauvegarde / chargement Joblib 🟠
| **Résultat attendu** | Le modèle sérialisé est rechargé et donne exactement les mêmes prédictions. |
| **Critère de succès** | `assert predictions_before == predictions_after`. |

#### ST-ML-003 — Classification d'un nouveau document 🟠
| **Résultat attendu** | Catégorie prédite cohérente avec l'objet du DAO. |
| **Critère de succès** | `predict_category(text) → CategorieMarche`. |

#### ST-ML-004 — Score de confiance de classification 🟠
| **Résultat attendu** | Probabilité ∈ [0, 1], affichée dans le détail. |
| **Critère de succès** | `MlInsight.classification_confidence ∈ [0, 1]`. |

#### ST-ML-005 — Ré-entraînement asynchrone 🔴
| **Étapes** | 1. Cliquer sur « Ré-entraîner » dans PredictorML.<br>2. Observer l'état du job. |
| **Résultat attendu** | - Endpoint `POST /api/v1/ml/retrain` retourne 202.<br>- Exécution en `BackgroundTasks`.<br>- Statut consultable via `GET /api/v1/ml/jobs/{id}` (à créer). |
| **Critère de succès** | Le modèle `.joblib` est mis à jour sur disque. |

#### ST-ML-006 — IsolationForest sur données financières 🟠
| **Résultat attendu** | Au moins 1 anomalie détectée sur un dataset synthétique incluant 1 % d'outliers. |
| **Critère de succès** | `ml/anomaly.py::detect_anomalies` retourne ≥ 1 ID. |

#### ST-ML-007 — Explicabilité des anomalies 🟠
| **Résultat attendu** | Chaque alerte explique pourquoi (montant élevé + délai court + caution disproportionnée). |
| **Critère de succès** | Ticket ML-05 (SHAP) implémenté. |

#### ST-ML-008 — Watchlist des désaccords IA vs humain 🟠
| **Résultat attendu** | Tableau des documents où la catégorie humaine ≠ catégorie IA. |
| **Critère de succès** | UI PredictorML affiche la watchlist. |

#### ST-ML-009 — Validation humaine depuis l'UI 🟠
| **Résultat attendu** | Un admin peut corriger la catégorie, l'événement est tracé (audit log, ticket AU-11). |
| **Critère de succès** | `CritereHumain` créé ou mis à jour, `AuditEvent` enregistré. |

#### ST-ML-010 — Métriques précision/rappel/F1 🟠
| **Résultat attendu** | Affichées dans PredictorML avec dates d'évaluation. |
| **Critère de succès** | Endpoint `GET /api/v1/ml/metrics` retourne `{precision, recall, f1, evaluated_at}`. |

#### ST-ML-011 — Matrice de confusion 🟡
| **Résultat attendu** | Heatmap affichée dans PredictorML. |
| **Critère de succès** | Ticket ML-09. |

#### ST-ML-012 — Feature importance 🟡
| **Résultat attendu** | Top 20 features TF-IDF pondérées par coefficient SVM. |
| **Critère de succès** | Ticket ML-12. |

#### ST-ML-013 — Versioning des modèles 🟡
| **Résultat attendu** | Chaque version taggée, possibilité de rollback. |
| **Critère de succès** | Ticket ML-13 (MLflow) ou table `model_version`. |

#### ST-ML-014 — Drift monitoring 🟡
| **Résultat attendu** | Alerte si la distribution des features change significativement (KS test ou PSI). |
| **Critère de succès** | Job quotidien, alerte Prometheus. |

#### ST-ML-015 — A/B testing entre deux versions 🟡
| **Résultat attendu** | Split du trafic, comparaison des métriques. |
| **Critère de succès** | Ticket ML-15. |

#### ST-ML-016 — Biais géographique 🟡
| **Résultat attendu** | Vérification que le modèle ne défavorise pas certaines régions. |
| **Critère de succès** | Rapport `audit/biais_<date>.json` généré. |

#### ST-ML-017 — Biais temporel 🟡
| **Résultat attendu** | Le modèle ne se dégrade pas avec le temps (réentraînement planifié). |
| **Critère de succès** | Métrique mensuelle trackée. |

#### ST-ML-018 — Robustesse aux inputs vides 🟠
| **Résultat attendu** | Si le texte OCR est vide ou très court, le modèle retourne une classe par défaut + flag. |
| **Critère de succès** | `predict_category("")` → `("Inconnu", 0.0)`. |

#### ST-ML-019 — Latence inférence 🟡
| **Résultat attendu** | < 200 ms par document. |
| **Critère de succès** | Mesure sur 100 prédictions. |

#### ST-ML-020 — Test de régression modèle (golden dataset) 🟡
| **Méthode** | Dataset doré avec prédictions attendues, comparaison après chaque réentraînement. |
| **Critère de succès** | `tests/fixtures/golden_predictions.json` non modifié après réentraînement (sauf cas documenté). |

#### ST-ML-021 — Gestion du déséquilibre de classes 🟠
| **Résultat attendu** | `class_weight='balanced'` ou SMOTE appliqué. |
| **Critère de succès** | Précision par classe ≥ 0.7 sur la classe minoritaire. |

---

### 5.6 Couche API REST

> Fichiers de référence : `backend/main.py` (tous les `@app.get` / `@app.post`), `backend/schemas.py`, `backend/repository.py`.

#### ST-API-001 — `GET /health` 🔴
| **Résultat attendu** | 200 OK, `{"status": "ok", "version": "2.0.0"}`. |
| **Critère de succès** | `curl http://127.0.0.1:8000/health` → 200. |

#### ST-API-002 — `GET /api/v1/ged/appels-offres` 🔴
| **Résultat attendu** | Pagination, filtres, JSON conforme au schéma OpenAPI. |
| **Critère de succès** | `tests/test_api_endpoints.py::test_list_appels_offres` PASS. |

#### ST-API-003 — `GET /api/v1/ged/appels-offres/{numero_ordre}` 🔴
| **Résultat attendu** | 200 avec détails, 404 si inexistant. |
| **Critère de succès** | `test_get_one_appel_offre` PASS. |

#### ST-API-004 — `POST /api/v1/ged/documents/upload` 🔴
| **Résultat attendu** | 201 Created, ID retourné, validation multipart. |
| **Critère de succès** | `test_upload_document` PASS. |

#### ST-API-005 — `DELETE /api/v1/ged/documents/{id}` 🟠
| **Résultat attendu** | 204 No Content, suppression logique (`deleted_at` non NULL). |
| **Critère de succès** | Ticket BDD-16. |

#### ST-API-006 — `GET /api/v1/ged/search?q=...` 🔴
| **Résultat attendu** | 200, format `{results: [...], total: N, took_ms: 87}`. |
| **Critère de succès** | Format conforme. |

#### ST-API-007 — `GET /api/v1/analytics/dashboard` 🟠
| **Résultat attendu** | KPIs et séries temporelles. |
| **Critère de succès** | Endpoint unifié créé (ticket API-07). |

#### ST-API-008 — `POST /api/v1/ml/retrain` 🟠
| **Résultat attendu** | 202 Accepted, job en background. |
| **Critère de succès** | `test_retrain_endpoint` PASS. |

#### ST-API-009 — `POST /api/v1/scraper/run` 🟠
| **Résultat attendu** | 202 Accepted, ID de job, suivi via `GET /api/v1/scraper/jobs/{id}`. |
| **Critère de succès** | Tickets ING-06 + API-09. |

#### ST-API-010 — `GET /api/v1/scraper/status` 🟠
| **Résultat attendu** | Statut courant, nombre collecté. |
| **Critère de succès** | Endpoint créé. |

#### ST-API-011 — Validation des schémas Pydantic 🔴
| **Résultat attendu** | 422 avec détails sur champs invalides. |
| **Critère de succès** | `test_invalid_payload` PASS. |

#### ST-API-012 — Documentation OpenAPI 🟠
| **Résultat attendu** | `/docs` Swagger UI, `/redoc` ReDoc, exemples cohérents. |
| **Critère de succès** | URL accessible, exemples non-vides. |

#### ST-API-013 — Versioning de l'API 🟡
| **Résultat attendu** | Préfixe `/api/v1/` actif, migration vers v2 documentée. |
| **Critère de succès** | Déjà partiellement fait (préfixe `/api/v1/`), à généraliser. |

#### ST-API-014 — Idempotence des POST 🟡
| **Résultat attendu** | Header `Idempotency-Key` supporté. |
| **Critère de succès** | Replay de la même clé ne crée pas de doublon. |

#### ST-API-015 — Rate limiting par utilisateur 🟠
| **Résultat attendu** | 429 au-delà du quota (100 req/min). |
| **Critère de succès** | Ticket S-15. |

#### ST-API-016 — Tests de contrat (Schemathesis) 🟡
| **Résultat attendu** | Vérification automatique que le front consomme une API conforme. |
| **Critère de succès** | CI `schemathesis run http://localhost:8000/openapi.json` exit 0. |

#### ST-API-017 — Réponse uniforme d'erreur 🟠
| **Résultat attendu** | Format RFC 7807 (Problem Details) : `{"type": "...", "title": "...", "status": 400, "detail": "..."}`. |
| **Critère de succès** | Ticket B-04. |

#### ST-API-018 — Headers de sécurité HTTP 🔴
| **Résultat attendu** | `Strict-Transport-Security`, `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, `Content-Security-Policy`. |
| **Critère de succès** | Test ST-SE-005. |

#### ST-API-019 — `GET /api/v1/system/ws/console` 🟠
| **Résultat attendu** | WebSocket diffuse les logs du pipeline en temps réel. |
| **Critère de succès** | Le frontend Monitoring reçoit les lignes. |

---

### 5.7 Couche Frontend / Écrans

> Fichiers de référence : `frontend-react/src/components/*.jsx`.

#### E1 — LandingPage

| ID | Scénario | Pri. | Critère de validation |
|---|---|---|---|
| ST-UI-001 | Affichage correct de la bannière | 🔴 | Logo + slogan visibles, pas de CLS > 0,1 |
| ST-UI-002 | Statistiques en temps réel (compteurs animés) | 🟠 | Compteurs incrémentés depuis `GET /api/v1/analytics/kpis` |
| ST-UI-003 | Responsive mobile/tablette (< 768 px) | 🟠 | Layout adapté, hamburger menu |
| ST-UI-004 | Section « Derniers AO » (carrousel) | 🟡 | Ticket UX-LAND-01 |
| ST-UI-005 | CTA différenciés selon persona | 🟡 | Ticket UX-LAND-02 |
| ST-UI-006 | Mode sombre / clair toggle | 🟡 | Ticket F-07 |

#### E2 — Dashboard

| ID | Scénario | Pri. | Critère de validation |
|---|---|---|---|
| ST-DB-001 | Affichage des 4 KPI principaux | 🔴 | Nombre de marchés, budget cumulé, délai moyen, taux OCR — chiffres cohérents avec la BDD |
| ST-DB-002 | Graphique camembert des catégories | 🟠 | Répartition cohérente, tooltip avec valeurs exactes |
| ST-DB-003 | Top 10 acheteurs par volume | 🟠 | Tri décroissant, valeurs correctes |
| ST-DB-004 | État vide (aucun document) | 🟠 | Message « Aucune donnée à afficher » + CTA |
| ST-DB-005 | Skeleton de chargement | 🟡 | Pas d'écran blanc pendant fetch |
| ST-DB-006 | Filtre temporel | 🟠 | Dropdown année/mois/trimestre |
| ST-DB-007 | Filtre par catégorie | 🟠 | Mise à jour du camembert |
| ST-DB-008 | Drill-down (clic part camembert) | 🟡 | Navigation vers liste filtrée |
| ST-DB-009 | Comparaison N vs N-1 | 🟠 | Flèches haut/bas + % |
| ST-DB-010 | Export PNG des graphiques | 🟡 | Bouton téléchargement |
| ST-DB-011 | Export PDF du dashboard | 🟡 | Rapport PDF généré |
| ST-DB-012 | Performance dashboard p95 | 🔴 | < 1 s pour le rendu initial |
| ST-DB-013 | Actualisation automatique (WebSocket) | 🟡 | Polling 30 s |
| ST-DB-014 | Cartographie du Maroc (choroplèthe) | 🟡 | Ticket E12 |
| ST-DB-015 | Heatmap calendrier | 🟡 | Ticket UX-DB-15 |
| ST-DB-016 | Funnel des étapes AO | 🟡 | Ticket UX-DB-16 |
| ST-DB-017 | Tableau des anomalies détectées | 🟡 | Accès direct à la liste |
| ST-DB-018 | Accessibilité (lecteur d'écran) | 🟡 | `aria-label` partout, contraste WCAG AA |
| ST-DB-019 | Responsive mobile | 🟠 | Layout adapté < 768 px |
| ST-DB-020 | i18n FR/AR des labels | 🟡 | Ticket i18n-01 |

#### E3 — SearchFTS

| ID | Scénario | Pri. | Critère de validation |
|---|---|---|---|
| ST-UI-010 | Affichage de la liste des résultats | 🔴 | `results.map((res, i) => ...)` rend chaque carte |
| ST-UI-011 | Mise en surbrillance des termes | 🟠 | `<mark>` jaune Tailwind |
| ST-UI-012 | Bouton « Voir le détail » fonctionnel | 🔴 | `Link to={/document/${res.numero_appel_offre}}` |
| ST-UI-013 | Tri interactif des colonnes | 🟠 | Dropdown date/montant/pertinence |
| ST-UI-014 | Pagination accessible | 🟠 | Boutons Précédent/Suivant + numéros de page |
| ST-UI-015 | Bouton « Réinitialiser les filtres » | 🔴 | Ticket UI-04 |
| ST-UI-016 | Filtres avancés (type d'avis, qualif…) | 🟠 | Ticket UI-05 |
| ST-UI-017 | Export CSV/Excel | 🔴 | Ticket FTS-28/29 |
| ST-UI-018 | Sauvegarde de recherche | 🟡 | Ticket FTS-27 |
| ST-UI-019 | Autocomplétion | 🟠 | Suggestions en < 200 ms |
| ST-UI-020 | Compteur dynamique | 🔴 | « N résultats en Tms » |

#### E4 — DocumentDetail

| ID | Scénario | Pri. | Critère de validation |
|---|---|---|---|
| ST-UI-020 | Affichage des 3 onglets (Infos, OCR, NLP) | 🔴 | 3 onglets visibles, navigation fonctionnelle |
| ST-UI-021 | Téléchargement du PDF original | 🔴 | Lien vers `storage_path` |
| ST-UI-022 | Téléchargement du texte OCR | 🟠 | Bouton `.txt` |
| ST-UI-023 | Affichage des scores NLP | 🟠 | Badges de score par entité |
| ST-UI-024 | Affichage des anomalies ML | 🟠 | Bandeau rouge si `is_anomaly` |
| ST-UI-025 | URL partageable (deep link) | 🟠 | `/document/<ref>` stable |
| ST-UI-026 | Bouton « Imprimer » | 🟡 | `window.print()` |
| ST-UI-027 | Section « Documents similaires » | 🟡 | Ticket UX-DET-01 |
| ST-UI-028 | Annotation collaborative | 🟡 | Ticket UX-DET-02 |

#### E5 — Explorer

| ID | Scénario | Pri. | Critère de validation |
|---|---|---|---|
| ST-UI-030 | Liste paginée des fichiers | 🔴 | Tableau avec colonnes Nom, Type, Taille, Date, Statut |
| ST-UI-031 | Filtrage par type | 🟠 | Dropdown ZIP / PDF / XML |
| ST-UI-032 | Filtrage par statut | 🟠 | Badges cliquables |
| ST-UI-033 | Tri par date / taille / nom | 🟠 | Header cliquable |
| ST-UI-034 | Téléchargement direct | 🟠 | Icône download |
| ST-UI-035 | Suppression (avec confirmation) | 🟠 | Modal de confirmation |
| ST-UI-036 | Recherche dans l'explorer | 🟠 | Input de recherche local |

#### E6 — Upload

| ID | Scénario | Pri. | Critère de validation |
|---|---|---|---|
| ST-UI-040 | Drag & drop multi-fichiers | 🔴 | `onDrop` handler fonctionnel |
| ST-UI-041 | File d'attente visuelle | 🔴 | Liste des fichiers en attente |
| ST-UI-042 | Polling du statut | 🟠 | `setInterval` nettoyé au démontage (ticket F-05) |
| ST-UI-043 | Barre de progression par fichier | 🟠 | Composant `<progress>` |
| ST-UI-044 | Annulation d'un upload en cours | 🟡 | Bouton « X » par fichier |
| ST-UI-045 | Gestion des erreurs | 🟠 | Toast rouge si taille > 100 Mo ou type invalide |
| ST-UI-046 | Notification finale (toast) | 🟠 | `react-hot-toast` configuré |
| ST-UI-047 | Limite de taille configurable | 🟡 | Constante `MAX_UPLOAD_SIZE` |

#### E7 — PredictorML

| ID | Scénario | Pri. | Critère de validation |
|---|---|---|---|
| ST-UI-050 | Affichage précision du modèle | 🟠 | `%` lisible |
| ST-UI-051 | Bouton « Ré-entraîner » avec confirmation | 🟠 | Modal « Êtes-vous sûr ? » |
| ST-UI-052 | Watchlist interactive | 🟠 | Tableau avec checkbox de validation |
| ST-UI-053 | Validation humaine en lot | 🟡 | Sélection multiple → action groupée |
| ST-UI-054 | Comparaison historique des modèles | 🟡 | Courbe précision par version |

#### E8 — Monitoring

| ID | Scénario | Pri. | Critère de validation |
|---|---|---|---|
| ST-UI-060 | Logs en temps réel (auto-refresh) | 🟠 | WebSocket `/ws/console` |
| ST-UI-061 | Filtre par niveau (INFO/WARN/ERROR) | 🟠 | Chips cliquables |
| ST-UI-062 | Recherche dans les logs | 🟠 | `grep` côté client |
| ST-UI-063 | Export des logs | 🟡 | Bouton `.jsonl` |
| ST-UI-064 | Statistiques temps OCR | 🟠 | Mini-graphique temps réel |
| ST-UI-065 | Alertes visuelles sur erreurs | 🟠 | Toast rouge |

#### E9 — PipelineAdmin

| ID | Scénario | Pri. | Critère de validation |
|---|---|---|---|
| ST-UI-070 | Sélection plage de dates | 🟠 | 2 `<input type="date">` |
| ST-UI-071 | Lancement scraping | 🔴 | Test ST-IN-001 |
| ST-UI-072 | Statut temps réel | 🟠 | WebSocket |
| ST-UI-073 | Annulation d'un scraping en cours | 🟡 | Ticket UX-PIPE-01 |
| ST-UI-074 | Historique des exécutions | 🟡 | Ticket UX-PIPE-02 |
| ST-UI-075 | Cron builder visuel | 🟡 | Ticket UX-PIPE-03 |

---

### 5.8 Couche Sécurité & Accès

> Tickets de référence : AU-01..11, SE-01..12.

#### ST-AU-001 — Accès sans authentification 🔴
| **Résultat attendu** | Redirection vers `/login`. |
| **Critère de succès** | Tentative d'accès à `/dashboard` sans JWT → redirection 302. |

#### ST-AU-002 — Login valide 🔴
| **Résultat attendu** | JWT émis (header `Authorization: Bearer <token>` + cookie httpOnly), redirection vers `/`. |
| **Critère de succès** | `tests/test_auth.py::test_login_success` PASS. |

#### ST-AU-003 — Login invalide 🔴
| **Résultat attendu** | Message « Identifiants incorrects », pas d'indication sur le champ fautif. |
| **Critère de succès** | 401 + message générique. |

#### ST-AU-004 — Mot de passe oublié 🔴
| **Résultat attendu** | Processus par email avec token à durée limitée (15 min). |
| **Critère de succès** | Email envoyé (MailHog en dev), token expiré après 15 min. |

#### ST-AU-005 — Changement de mot de passe 🟠
| **Résultat attendu** | Impose l'ancien mot de passe, complexité (12+ caractères, majuscule, chiffre, spécial). |
| **Critère de succès** | Ticket AU-05. |

#### ST-AU-006 — Verrouillage après 5 tentatives 🔴
| **Résultat attendu** | Compte temporairement bloqué (15 min), alerte email admin. |
| **Critère de succès** | 6e tentative → 429 Locked. |

#### ST-AU-007 — Session expirée 🟠
| **Résultat attendu** | Redirection vers login, message « Session expirée ». |
| **Critère de succès** | JWT expiré → 401 + UI toast. |

#### ST-AU-008 — RBAC : utilisateur `reader` 🟠
| **Résultat attendu** | Peut consulter mais pas supprimer ni modifier. |
| **Critère de succès** | `DELETE /documents/X` avec rôle reader → 403. |

#### ST-AU-009 — RBAC : utilisateur `analyst` 🟠
| **Résultat attendu** | Peut lancer le scraping et ré-entraîner les modèles. |
| **Critère de succès** | `POST /scraper/run` avec analyst → 202. |

#### ST-AU-010 — RBAC : utilisateur `admin` 🔴
| **Résultat attendu** | Accès complet, gestion des utilisateurs. |
| **Critère de succès** | `GET /users` avec admin → 200. |

#### ST-AU-011 — Audit log 🔴
| **Résultat attendu** | Toute action sensible (login, modification modèle, suppression, scraping) est tracée dans `audit_events`. |
| **Critère de succès** | Table `audit_events` Append-Only (trigger SQL). |

#### ST-SE-001 — Injection SQL 🔴
| **Méthode** | Envoyer `' OR 1=1 --` dans tous les champs de recherche. |
| **Résultat attendu** | Aucune injection, requêtes paramétrées. |
| **Critère de succès** | Réponse normale, pas d'exception, pas de fuite. |

#### ST-SE-002 — XSS stocké 🔴
| **Méthode** | Injecter `<script>alert(1)</script>` dans le titre d'un document via API. |
| **Résultat attendu** | Échappé, pas d'exécution. |
| **Critère de succès** | `dangerouslySetInnerHTML` jamais utilisé ; React échappe par défaut. |

#### ST-SE-003 — XSS réfléchi 🟠
| **Méthode** | `?q=<script>alert(1)</script>` dans l'URL. |
| **Résultat attendu** | Échappé, `Content-Security-Policy` bloque. |

#### ST-SE-004 — CSRF 🔴
| **Méthode** | POST sans token CSRF depuis un autre domaine. |
| **Résultat attendu** | Rejeté (SameSite=Strict + CSRF token). |
| **Critère de succès** | Ticket S-04. |

#### ST-SE-005 — Headers de sécurité HTTP 🔴
| **Résultat attendu** | `Strict-Transport-Security`, `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, `Content-Security-Policy`. |
| **Critère de succès** | Vérifié via `curl -I`. |

#### ST-SE-006 — Exposition des secrets 🔴
| **Méthode** | Vérifier que les clés API ne fuient pas dans les bundles front (`npm run build` puis `grep -r "OPENAI_API_KEY" dist/`). |
| **Résultat attendu** | 0 secret exposé. |
| **Critère de succès** | `tests/test_secrets.py` PASS. |

#### ST-SE-007 — HTTPS obligatoire 🔴
| **Résultat attendu** | Redirection HTTP → HTTPS. |
| **Critère de succès** | `curl http://example.com/health` → 301 https. |

#### ST-SE-008 — CORS strict 🟠
| **Résultat attendu** | Liste blanche de domaines, pas de `*`. |
| **Critère de succès** | Ticket B-08 (actuellement `allow_origins=["*"]` dans `main.py:55` — **non conforme**). |

#### ST-SE-009 — Rate limiting 🟠
| **Résultat attendu** | 100 req/min par IP, retour 429 au-delà. |
| **Critère de succès** | `locust -u 200 -r 50` montre 429 à partir de la 101e req/min. |

#### ST-SE-010 — Validation des uploads 🟠
| **Résultat attendu** | Rejet des fichiers non PDF/ZIP, taille max configurable. |
| **Critère de succès** | Upload `.exe` → 415 Unsupported Media Type. |

#### ST-SE-011 — Logs non sensibles 🔴
| **Résultat attendu** | Aucun mot de passe ni token dans les logs. |
| **Critère de succès** | `grep -E "password|token" logs/*.log` → 0 hit. |

#### ST-SE-012 — Chiffrement at rest 🟡
| **Résultat attendu** | BDD et stockage fichiers chiffrés (LUKS / KMS). |
| **Critère de succès** | Ticket S-18 (V1). |

---

### 5.9 Couche Performance & Résilience

> Outils : `locust`, `k6`, `pytest-benchmark`.

#### ST-PE-001 — Indexation de 1 000 documents 🟠
| **Résultat attendu** | < 1 h end-to-end (scraping + OCR + NLP + indexation FTS). |
| **Critère de succès** | Métrique stockée dans `benchmarks/`. |

#### ST-PE-002 — Indexation de 10 000 documents 🟠
| **Résultat attendu** | < 12 h, sans saturation mémoire. |
| **Critère de succès** | Pic RAM < 8 Go. |

#### ST-PE-003 — Recherche FTS sur 10 000 docs 🔴
| **Résultat attendu** | p95 < 500 ms, p99 < 1 s. |
| **Critère de succès** | `k6 run loadtest.js --vus 50 --duration 60s` exit 0. |

#### ST-PE-004 — Charge concurrente API (50 users) 🟠
| **Résultat attendu** | < 1 % d'erreurs, latence stable. |
| **Critère de succès** | Locust. |

#### ST-PE-005 — Charge concurrente (200 users) 🟡
| **Résultat attendu** | Dégradation contrôlée, circuit breaker actif. |
| **Critère de succès** | Latence p95 < 2 s. |

#### ST-PE-006 — Mémoire OCR sur PDF 500 pages 🟡
| **Résultat attendu** | Pic < 2 Go par worker. |
| **Critère de succès** | `memory_profiler`. |

#### ST-PE-007 — Mémoire FTS sur 1 M de pages 🟡
| **Résultat attendu** | Pic < 4 Go. |

#### ST-PE-008 — Cold start API 🟡
| **Résultat attendu** | < 3 s après déploiement. |

#### ST-PE-009 — Build front (Vite) 🟡
| **Résultat attendu** | < 30 s. |

#### ST-PE-010 — Bundle size front 🟡
| **Résultat attendu** | < 500 Ko gzippé. |
| **Critère de succès** | `vite-bundle-visualizer`. |

#### ST-PE-011 — Time to first byte (TTFB) 🟡
| **Résultat attendu** | < 200 ms. |

#### ST-PE-012 — Largest Contentful Paint (LCP) 🟠
| **Résultat attendu** | < 2,5 s sur 3G. |

#### ST-PE-013 — Cumulative Layout Shift (CLS) 🟠
| **Résultat attendu** | < 0,1. |

#### ST-PE-014 — First Input Delay (FID) 🟠
| **Résultat attendu** | < 100 ms. |

#### ST-PE-015 — Stress test scraping (site lent) 🟡
| **Résultat attendu** | Timeouts bien gérés, pas de cascade d'échecs. |

---

### 5.10 Couche DevOps / CI-CD / Observabilité

#### ST-OPS-001 — Pipeline CI/CD GitHub Actions 🟠
| **Résultat attendu** | À chaque PR : lint + tests unitaires + tests d'intégration + build Docker + déploiement staging. |
| **Critère de succès** | `.github/workflows/ci.yml` valide, badge CI vert sur `main`. |

#### ST-OPS-002 — Build Docker multi-stage 🟠
| **Résultat attendu** | `docker build -t ged-api:dev .` produit une image < 500 Mo. |
| **Critère de succès** | `docker run ged-api:dev` démarre en < 5 s. |

#### ST-OPS-003 — docker-compose complet 🟠
| **Résultat attendu** | `docker-compose up` démarre l'API + PostgreSQL + Redis + MinIO + Prometheus + Grafana. |
| **Critère de succès** | `curl http://localhost:8000/health` → 200. |

#### ST-OPS-004 — Logs structurés (JSON Lines) 🟠
| **Résultat attendu** | Tous les `print()` remplacés par `logger.info(event="...", **kwargs)`. |
| **Critère de succès** | Ticket B-05. |

#### ST-OPS-005 — Métriques Prometheus 🟠
| **Résultat attendu** | Endpoint `/metrics` (compteurs requêtes, latence histogram, jobs en cours). |
| **Critère de succès** | `curl /metrics | grep http_requests_total`. |

#### ST-OPS-006 — Dashboards Grafana 🟡
| **Résultat attendu** | Dashboard « GED-Production » avec 6 panneaux : requêtes/s, latence p95, jobs OCR en file, anomalies détectées, erreurs 5xx, taille BDD. |
| **Critère de succès** | JSON importable. |

#### ST-OPS-007 — Alertes PagerDuty / email 🟡
| **Résultat attendu** | Alerte si `error_rate_5xx > 1 %` pendant 5 min ou `ocr_queue_depth > 1000`. |
| **Critère de succès** | `alertmanager.yml` configuré. |

#### ST-OPS-008 — Backups PostgreSQL 🟠
| **Résultat attendu** | `pg_dump` quotidien, rétention 30 j, stockage S3. |
| **Critère de succès** | Cron + script testé. |

#### ST-OPS-009 — Scan de vulnérabilités 🟠
| **Résultat attendu** | `pip-audit`, `npm audit`, `trivy` exécutés en CI, 0 vulnérabilité HIGH/CRITICAL. |
| **Critère de succès** | Pipeline bloqué si HIGH/CRITICAL. |

#### ST-OPS-010 — Tracing OpenTelemetry 🟡
| **Résultat attendu** | Trace complète d'une requête (FastAPI + SQLAlchemy + httpx). |
| **Critère de succès** | Jaeger UI affiche le graphe. |

#### ST-OPS-011 — Healthcheck profond 🟠
| **Résultat attendu** | `GET /health` teste DB + Redis + MinIO. |
| **Critère de succès** | Ticket B-12. |

#### ST-OPS-012 — Documentation OpenAPI enrichie 🟡
| **Résultat attendu** | Exemples de requêtes/réponses, descriptions, tags, security schemes. |
| **Critère de succès** | `http://localhost:8000/docs` complet. |

#### ST-OPS-013 — i18n FR/AR (frontend) 🟠
| **Résultat attendu** | `i18next` configuré, bundles `fr.json` et `ar.json`, sélecteur de langue persistant, layout RTL pour AR. |
| **Critère de succès** | Ticket i18n-01. |

#### ST-OPS-014 — PWA installable 🟡
| **Résultat attendu** | `vite-plugin-pwa`, manifest, service worker. |
| **Critère de succès** | Installable sur Chrome, fonctionne offline sur la dernière page visitée. |

#### ST-OPS-015 — Conformité Lighthouse ≥ 90 🟠
| **Résultat attendu** | Score Performance, Accessibility, Best Practices, SEO ≥ 90. |
| **Critère de succès** | Rapport `lighthouse.json` archivé en CI. |

---

### 5.11 Tests End-to-End (E2E)

> Outil : Cypress ou Playwright.

#### ST-E2E-001 — Parcours complet utilisateur « Lecteur » 🔴
| **Étapes** | 1. Connexion avec compte `reader`.<br>2. Landing → Dashboard.<br>3. Recherche par mots-clés « pont ».<br>4. Ouverture du détail d'un document.<br>5. Téléchargement du PDF.<br>6. Déconnexion. |
| **Résultat attendu** | Parcours sans erreur, UI cohérente, audit log mis à jour. |
| **Critère de succès** | `cypress/e2e/reader_journey.spec.js` PASS. |

#### ST-E2E-002 — Parcours « Analyste » lance un scraping 🟠
| **Étapes** | 1. Connexion `analyst`.<br>2. PipelineAdmin → plage de dates.<br>3. Lancer scraping.<br>4. Suivi temps réel.<br>5. Une fois terminé, Dashboard.<br>6. Vérifier que les nouveaux documents apparaissent. |

#### ST-E2E-003 — Parcours « Admin » ré-entraîne un modèle 🟠
| **Étapes** | 1. Connexion `admin`.<br>2. PredictorML.<br>3. Lancer ré-entraînement.<br>4. Suivi du job.<br>5. Vérifier nouvelle précision. |

#### ST-E2E-004 — Parcours « Import manuel + labellisation » 🟠
| **Étapes** | 1. Connexion `analyst`.<br>2. Upload d'un PDF.<br>3. Suivi de l'OCR + NLP temps réel.<br>4. Vérification des entités extraites.<br>5. Correction manuelle si nécessaire. |

#### ST-E2E-005 — Scénario d'anomalie détectée 🟡
| **Étapes** | 1. Import d'un DAO avec caution disproportionnée (synthétique).<br>2. IsolationForest le flag.<br>3. Apparition dans PredictorML et Dashboard.<br>4. Notification (email + toast). |

#### ST-E2E-006 — Bascule FR/AR 🟡
| **Étapes** | 1. Changement de langue.<br>2. Tous les écrans affichés en arabe (y compris graphiques, dates en chiffres arabes).<br>3. RTL layout actif. |

#### ST-E2E-007 — Mode dégradé (site inaccessible) 🟡
| **Étapes** | 1. Couper l'accès au site ministériel (DNS blackhole).<br>2. Lancer scraping.<br>3. Erreur claire, retry, pas de crash. |

#### ST-E2E-008 — Multi-utilisateurs simultanés 🟡
| **Outil** | Locust / k6, 50 virtual users. |
| **Résultat attendu** | Pas de conflit, base cohérente. |

#### ST-E2E-009 — Export CSV depuis la recherche 🔴
| **Étapes** | 1. Recherche avec filtres.<br>2. Cliquer « Exporter CSV ».<br>3. Vérifier le fichier téléchargé. |
| **Résultat attendu** | CSV UTF-8, séparateur `,`, en-têtes corrects. |

#### ST-E2E-010 — Réinitialisation des filtres de recherche 🔴
| **Étapes** | 1. Saisir filtres (ville, budget, date).<br>2. Cliquer « Réinitialiser ». |
| **Résultat attendu** | Tous les champs reviennent à leur valeur par défaut, résultats réinitialisés. |

#### ST-E2E-011 — Création d'une alerte 🟡
| **Étapes** | 1. Connexion `analyst`.<br>2. E11 Centre d'alertes.<br>3. Builder visuel : « Travaux routiers + Casa + budget > 1M ».<br>4. Fréquence : quotidien.<br>5. Canal : email.<br>6. Enregistrer. |
| **Résultat attendu** | Alerte visible dans « Mes alertes actives », un email de test est envoyé. |

---

## 6. Plan d'exécution des tests

### 6.1 Phasage (Sprints)

| Sprint | Tests à exécuter en priorité | Livrables DoD |
|---|---|---|
| **S1 (Durcir l'existant)** | ST-AU-001..011, ST-SE-001..011, ST-API-001..018, ST-IN-001, ST-NL-001..008, ST-OC-001..002 | Auth + RBAC + Audit + Headers + CI verte |
| **S2 (Compléter la recherche)** | ST-FT-001..032, ST-UI-004, ST-UI-013..017, ST-E2E-009, ST-E2E-010 | 32 scénarios FTS verts + Réinitialisation + Export |
| **S3 (Enrichir le Dashboard)** | ST-DB-001..020, ST-API-007 | 20 scénarios Dashboard verts + N vs N-1 |
| **S4 (Ops & Qualité)** | ST-OPS-001..015, ST-SE-005, ST-Pe-001..015 | Docker + CI/CD + Prometheus + Lighthouse ≥ 90 |
| **S5 (ML & Données)** | ST-ML-001..021, ST-OC-003..015, ST-NL-009..021 | Modèles ML industrialisés, données alignées sur le formulaire source |
| **S6 (i18n & PWA)** | ST-E2E-006, ST-OPS-013, ST-OPS-014 | FR/AR complet, PWA installable |

### 6.2 Pipeline CI (suggestion)

```yaml
name: CI
on: [push, pull_request]
jobs:
  lint:
    steps: [black, ruff, mypy, oxlint]
  test-unit:
    steps: [pytest --cov --cov-fail-under=80]
  test-int:
    services: [postgres, redis, minio]
    steps: [pytest -m integration]
  test-e2e:
    steps: [cypress run --browser chrome]
  security:
    steps: [pip-audit, npm audit, trivy]
  build:
    steps: [docker build, docker push]
  lighthouse:
    steps: [lhci autorun]
```

### 6.3 Critères de sortie de sprint

```
[ ] Tous les tests P0 du sprint exécutés et PASSED
[ ] Couverture ≥ 80 % sur le périmètre du sprint
[ ] Performance SLO respectée
[ ] Démo fonctionnelle enregistrée
[ ] Documentation mise à jour
[ ] CHANGELOG.md incrémenté
[ ] Tag Git + release notes
```

---

## 7. Annexes

### 7.1 Jeu de données de test recommandé

| Dataset | Source | Taille | Usage |
|---|---|---|---|
| Golden set OCR | 20 DAO de référence du Ministère | 20 docs | Tests T-OC-*** |
| Golden set NLP | Mêmes 20 docs annotés manuellement | 20 docs | Tests T-NL-*** |
| Golden set ML | 200 docs labellisés | 200 docs | Tests T-ML-*** |
| Golden set FTS | 100 docs avec requêtes associées | 100 docs | Tests T-FT-*** |
| Stress test | 10 000 PDF aléatoires publics | 10 000 docs | Tests T-PE-*** |

### 7.2 Outils recommandés

| Domaine | Outil |
|---|---|
| Tests unitaires (Python) | Pytest + pytest-cov + pytest-mock |
| Tests API | Pytest + TestClient FastAPI + Schemathesis |
| Tests E2E (UI) | Cypress ou Playwright |
| Tests de charge | Locust / k6 |
| Sécurité OWASP | OWASP ZAP, Bandit, pip-audit, Trivy |
| Qualité code | Black, Ruff, mypy, oxlint |
| Monitoring | Prometheus, Grafana, Sentry, Loki, Tempo |
| Performance Lighthouse | `@lhci/cli` |
| Visual regression | Percy / Chromatic / Playwright snapshots |

### 7.3 Glossaire

| Terme | Définition |
|---|---|
| AO / DAO | Appel d'Offres / Dossier d'Appel d'Offres |
| CPS | Cahier des Prescriptions Spéciales |
| RC | Règlement de Consultation |
| FTS | Full-Text Search |
| GIN | Generalized Inverted Index (PostgreSQL) |
| CER / WER | Character / Word Error Rate |
| PFA | Projet de Fin d'Année |
| DSI | Direction des Systèmes d'Information |
| SLA / SLO | Service Level Agreement / Objective |
| RBAC | Role-Based Access Control |
| BM25 | algorithme de ranking FTS |
| NER | Named Entity Recognition |
| MLOps | Machine Learning Operations |
| RTL | Right-To-Left (layout arabe) |
| DoD | Definition of Done |
| FTS | Full-Text Search (synonyme de ST-FT-***) |

### 7.4 Matrice de traçabilité Ticket → Scénario

> Une matrice exhaustive est générée automatiquement par le fichier de tickets (`04-tickets-ameliorations.md`), chaque ticket référençant un ou plusieurs `ST-XXX-NNN`.

### 7.5 Légende des priorités (rappel)

| Priorité | Définition | Délai cible |
|---|---|---|
| 🔴 P0 | Bloquant pour la mise en production | Sprint 1-4 |
| 🟠 P1 | Important pour la BI | Sprint 5-6 |
| 🟡 P2 | Amélioration | V1 (post-soutenance) |

---

> **Conclusion** : Ce cahier de texte constitue le référentiel de validation unique. Chaque scénario est défini sans ambiguïté, mesurable, et relié à un ticket de remédiation dans le fichier `04-tickets-ameliorations.md`. La somme des `ST-***` validés PASS définit l'état de readiness pour la production.
