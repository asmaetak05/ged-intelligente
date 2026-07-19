# 📗 Fichier 2 — Améliorations, Corrections & Roadmap vers une vraie plateforme BI

> **Projet** : GED Intelligente — Gestion Électronique des Documents pour les marchés publics du Ministère de l'Équipement et de l'Eau du Maroc
> **Stage** : PFA (Projet de Fin d'Année)
> **Complément de** : `01-evaluation-et-tests.md`
> **Site de référence** : http://appels-offres.equipement.gov.ma/recherche/criteres.aspx
> **Version** : 1.0 — Backlog de corrections, d'évolutions et d'innovations

> 🎯 **Objectif de ce document** : transformer le prototype PFA en une **plateforme BI ministérielle de référence**, alignée sur le portail public, exploitable par les acheteurs, les analystes, les décideurs et les auditeurs.

---

## Table des matières

1. [Vision cible de la plateforme BI](#1-vision-cible-de-la-plateforme-bi)
2. [Corrections à apporter sur l'existant](#2-corrections-à-apporter-sur-lexistant)
   - 2.1 [Corrections Backend](#21-corrections-backend)
   - 2.2 [Corrections Frontend / UX](#22-corrections-frontend--ux)
   - 2.3 [Corrections Pipeline de données](#23-corrections-pipeline-de-données)
   - 2.4 [Corrections Modèles ML](#24-corrections-modèles-ml)
   - 2.5 [Corrections Sécurité & Ops](#25-corrections-sécurité--ops)
3. [Améliorations de l'existant (quick wins)](#3-améliorations-de-lexistant-quick-wins)
   - 3.1 [Module Ingestion](#31-module-ingestion)
   - 3.2 [Module OCR & NLP](#32-module-ocr--nlp)
   - 3.3 [Module Recherche FTS](#33-module-recherche-fts)
   - 3.4 [Module ML](#34-module-ml)
   - 3.5 [Écrans existants](#35-écrans-existants)
4. [Nouveaux écrans](#4-nouveaux-écrans)
   - 4.1 [E10 — Authentification & Gestion des utilisateurs](#e10--authentification--gestion-des-utilisateurs)
   - 4.2 [E11 — Centre d'alertes & watchlist personnalisée](#e11--centre-dalertes--watchlist-personnalisée)
   - 4.3 [E12 — Cartographie des AO](#e12--cartographie-des-ao)
   - 4.4 [E13 — Comparateur d'appels d'offres](#e13--comparateur-dappels-doffres)
   - 4.5 [E14 — Tableau de bord Acheteur](#e14--tableau-de-bord-acheteur)
   - 4.6 [E15 — Tableau de bord Fournisseur](#e15--tableau-de-bord-fournisseur)
   - 4.7 [E16 — Analytics Avancés (DataViz)](#e16--analytics-avancés-dataviz)
   - 4.8 [E17 — Prédictif & Prévisions](#e17--prédictif--prévisions)
   - 4.9 [E18 — Audit & Traçabilité](#e18--audit--traçabilité)
   - 4.10 [E19 — Labellisation collaborative](#e19--labellisation-collaborative)
   - 4.11 [E20 — Catalogue des modèles ML](#e20--catalogue-des-modèles-ml)
   - 4.12 [E21 — Notifications & Messagerie](#e21--notifications--messagerie)
   - 4.13 [E22 — Rapports programmés](#e22--rapports-programmés)
   - 4.14 [E23 — Mobile-first & PWA](#e23--mobile-first--pwa)
   - 4.15 [E24 — Data Lineage & Quality](#e24--data-lineage--quality)
5. [Nouvelles fonctionnalités transverses](#5-nouvelles-fonctionnalités-transverses)
   - 5.1 [Recherche sémantique par embedding (LLM)](#51-recherche-sémantique-par-embedding-llm)
   - 5.2 [Chatbot Q&A sur les DAO](#52-chatbot-qa-sur-les-dao)
   - 5.3 [Résumés automatiques](#53-résumés-automatiques)
   - 5.4 [i18n FR/AR](#54-i18n-frar)
   - 5.5 [Accessibilité WCAG 2.1 AA](#55-accessibilité-wcag-21-aa)
   - 5.6 [Multi-tenant](#56-multi-tenant)
   - 5.7 [API publique & Open Data](#57-api-publique--open-data)
   - 5.8 [Workflow d'approbation](#58-workflow-dapprobation)
   - 5.9 [Sauvegarde de recherche & alertes email](#59-sauvegarde-de-recherche--alertes-email)
   - 5.10 [Signature électronique des documents](#510-signature-électronique-des-documents)
6. [Architecture cible](#6-architecture-cible)
7. [Roadmap produit](#7-roadmap-produit)
   - 7.1 [Roadmap MVP (3 mois)](#71-roadmap-mvp-3-mois)
   - 7.2 [Roadmap V1 (6 mois)](#72-roadmap-v1-6-mois)
   - 7.3 [Roadmap V2 (12 mois)](#73-roadmap-v2-12-mois)
8. [KPIs de succès](#8-kpis-de-succès)
9. [Annexes](#9-annexes)

---

## 1. Vision cible de la plateforme BI

```
┌──────────────────────────────────────────────────────────────────────────┐
│                       🎯  PLATEFORME GED-BI 360  🎯                     │
├──────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│   Décideurs          Analystes          Acheteurs         Fournisseurs  │
│       │                  │                  │                  │         │
│       ▼                  ▼                  ▼                  ▼         │
│  ┌──────────┐      ┌──────────┐       ┌──────────┐       ┌──────────┐    │
│  │ Dashbord │      │ Recherche│       │ Pilotage │       │ Veille   │    │
│  │ exécutif │      │ avancée  │       │ achats   │       │ & alertes│    │
│  └────┬─────┘      └────┬─────┘       └────┬─────┘       └────┬─────┘    │
│       │                 │                   │                  │         │
│       └────────┬────────┴────────┬──────────┴──────────┬───────┘         │
│                ▼                 ▼                     ▼                 │
│      ┌──────────────────────────────────────────────────────────┐        │
│      │   API Gateway (FastAPI + GraphQL + WebSocket)            │        │
│      └─────┬──────────────────┬────────────────────┬───────────┘        │
│            ▼                  ▼                    ▼                    │
│   ┌───────────────┐  ┌─────────────────┐  ┌──────────────────┐          │
│   │   Data Lake   │  │ Feature Store   │  │  Model Registry  │          │
│   │   (MinIO)     │  │ (Feast)         │  │   (MLflow)       │          │
│   └───────┬───────┘  └────────┬────────┘  └────────┬─────────┘          │
│           └──────────────────┬┴───────────────────┘                    │
│                              ▼                                          │
│      ┌──────────────────────────────────────────────────┐              │
│      │      Orchestrateur (Airflow / Prefect)           │              │
│      │  Scraping │ OCR │ NLP │ Embeddings │ Training     │              │
│      └──────────────────────────────────────────────────┘              │
│                              │                                          │
│                              ▼                                          │
│      ┌──────────────────────────────────────────────────┐              │
│      │  PostgreSQL + Elasticsearch + Redis + Clickhouse │              │
│      └──────────────────────────────────────────────────┘              │
│                                                                          │
└──────────────────────────────────────────────────────────────────────────┘
```

**Personae cibles** :
1. **Décideur ministériel** : veut des KPIs synthétiques, des tendances, des alertes sur les dérives budgétaires.
2. **Analyste BI** : veut explorer, croiser, exporter, créer ses propres rapports.
3. **Acheteur public** (direction) : veut piloter ses propres marchés, suivre les anomalies, benchmarker.
4. **Fournisseur / entreprise** : veut une veille qualifiée, des alertes pertinentes.
5. **Auditeur / contrôleur** : veut la traçabilité complète, l'audit log, l'historique des modifications.
6. **Data scientist** : veut itérer sur les modèles, monitorer le drift, comparer les versions.

---

## 2. Corrections à apporter sur l'existant

### 2.1 Corrections Backend

| # | Constat | Correction proposée | Effort |
|---|---|---|---|
| B-01 | Pas d'authentification, API ouverte à tous | Ajouter JWT + middleware `Depends(get_current_user)`, Bcrypt pour les mots de passe | M |
| B-02 | Pas de rate limiting | Ajouter `slowapi` ou équivalent (100 req/min/user) | S |
| B-03 | Pas de pagination standardisée | Réponse `{items, total, page, size, took_ms}` partout | S |
| B-04 | Erreurs retournées en `500` au lieu de messages métier | Handler global d'exceptions, format RFC 7807 (Problem Details) | S |
| B-05 | Logs en `print()` | `structlog` ou `loguru` avec contexte (request_id, user_id) | S |
| B-06 | Pas de validation des schémas Pydantic versionnée | Versionner les schémas (`schemas/v1`, `v2`) | M |
| B-07 | `BackgroundTasks` non persistant | Passer à **Celery + Redis** ou **Dramatiq** avec RQ | L |
| B-08 | Pas de middleware CORS strict | CORS whitelist explicite | S |
| B-09 | Pas de cache | Cache Redis sur `/dashboard` (TTL 30 s) et `/search` (TTL 60 s) | M |
| B-10 | SQLite en dev seulement | Documenter le passage à PostgreSQL via docker-compose | S |
| B-11 | Pas de migrations seed | Ajouter seeds de catégories, régions, qualifications | S |
| B-12 | Pas de healthcheck profond | `/health` qui teste DB + Redis + stockage | S |
| B-13 | Pas de versionning de l'API | Préfixer `/api/v1` | S |
| B-14 | Modèles SQLAlchemy sans `__tablename__` explicite | Standardiser | S |
| B-15 | Pas de contrainte d'unicité sur la référence | Ajouter `UniqueConstraint('reference', name='uq_doc_reference')` | S |
| B-16 | Pas de `soft delete` | Ajouter `deleted_at` sur les entités métier | S |
| B-17 | Pas de `created_at` / `updated_at` | Ajouter à toutes les tables | S |
| B-18 | Pas de `request_id` | Middleware qui injecte un UUID et le propage | S |
| B-19 | Pas de `OpenTelemetry` | Activer l'auto-instrumentation FastAPI + SQLAlchemy | M |
| B-20 | Tests sans factory-boy | Introduire `factory-boy` + `pytest-postgresql` | S |

> Légende effort : **S** (< 1 j) • **M** (1-5 j) • **L** (> 5 j)

### 2.2 Corrections Frontend / UX

| # | Constat | Correction proposée | Effort |
|---|---|---|---|
| F-01 | Aucune gestion d'état globale (uniquement `useState`) | Introduire **Zustand** (léger) ou Redux Toolkit | M |
| F-02 | Pas de gestion centralisée des erreurs | Intercepteur Axios + toast Snackbar (Sonner / react-hot-toast) | S |
| F-03 | Pas de squelette de chargement | Skeleton sur Dashboard, SearchFTS, DocumentDetail | S |
| F-04 | Pas de page 404 / 403 / 500 | Créer les pages d'erreur et le boundary React | S |
| F-05 | Polling en `setInterval` non nettoyé | Utiliser `react-query` ou `swr` | M |
| F-06 | Pas de focus management | Ajouter `react-focus-lock` pour les modales | S |
| F-07 | Dark mode uniquement | Ajouter toggle light/dark avec persistance | S |
| F-08 | Pas de lazy loading des routes | `React.lazy` + `Suspense` | S |
| F-09 | Pas d'optimistic update | Pour les actions CRUD mineures | S |
| F-10 | Composants non testés | Ajouter Vitest + React Testing Library | M |
| F-11 | Pas de Storybook | Mettre en place Storybook pour les composants | M |
| F-12 | i18n absente | Configurer `i18next` avec bundles FR/AR | M |
| F-13 | Pas de `data-testid` | Convention pour les tests E2E | S |
| F-14 | Bundle non analysé | `vite-bundle-visualizer` pour traquer le poids | S |
| F-15 | Pas de PWA | `vite-plugin-pwa` pour install + offline | M |
| F-16 | Notifications navigateur absentes | Web Notifications API | S |
| F-17 | Pas de page de paramètres utilisateur | Profil, préférences, langue, thème | M |
| F-18 | Modales en `position: fixed` non trap focus | Utiliser `headlessui` ou `radix-ui` | S |
| F-19 | Pas de raccourcis clavier | `/` focus recherche, `g d` dashboard, `?` aide | S |
| F-20 | Formulaire d'upload ne montre pas la taille totale | Afficher poids cumulé, ETA, annulation | S |

### 2.3 Corrections Pipeline de données

| # | Constat | Correction proposée | Effort |
|---|---|---|---|
| P-01 | Scraping mono-thread | Pool Playwright + `asyncio.gather` | M |
| P-02 | Pas de reprise sur erreur | Checkpoint + reprise depuis offset | M |
| P-03 | Pas de déduplication robuste | Hash SHA-256 du contenu PDF + DB unique | S |
| P-04 | OCR arabe sous-performant | Tester EasyOCR / PaddleOCR en fallback, voting | L |
| P-05 | Pas de watermark temporel | `last_scrape_at` par source | S |
| P-06 | Pipeline bloqué si un PDF corrompu | Try/except granulaire, document marqué `failed` | S |
| P-07 | Pas de stockage des PDF originaux | MinIO ou S3 avec versioning | M |
| P-08 | Pas de séparation dev/prod | Profils `pydantic.BaseSettings` | S |
| P-09 | Pas de cache de scraping | Redis cache des résultats par requête | S |
| P-10 | Pas d'orchestrateur | Airflow / Prefect / Dagster pour DAGs | L |
| P-11 | Modèles ML non versionnés | MLflow Tracking | M |
| P-12 | Pas de validation de la donnée | Great Expectations / Pandera | M |
| P-13 | Pas de feature store | Feast (en V1) | L |
| P-14 | Embeddings non recalculés sur nouveaux docs | Job d'embedding quotidien | M |
| P-15 | Pas de règles d'archivage | Cold storage pour AO > 5 ans | S |

### 2.4 Corrections Modèles ML

| # | Constat | Correction proposée | Effort |
|---|---|---|---|
| ML-01 | Pas de baseline simple | Modèle majoritaire + régression logistique pour comparaison | S |
| ML-02 | Pas de cross-validation | `StratifiedKFold` (k=5) | S |
| ML-03 | SVM linéaire sur features bag-of-words | Tester **transformers** (`camembert-base`, `aubmindlab/bert-base-arabertv02`) | L |
| ML-04 | Pas de gestion du déséquilibre | SMOTE ou `class_weight='balanced'` | S |
| ML-05 | Pas d'explicabilité | SHAP (KernelExplainer) sur top features | M |
| ML-06 | IsolationForest non supervisé | Tester One-Class SVM, Elliptic Envelope, AutoEncoder | M |
| ML-07 | Pas de seuil ajustable | Slider UI pour le seuil d'anomalie | M |
| ML-08 | Pas de calibration des scores | `CalibratedClassifierCV` | S |
| ML-09 | Pas de confusion matrix | Affichage par classe | S |
| ML-10 | Pas de rapport de classification | Génération `classification_report` | S |
| ML-11 | Pas d'export ONNX | Sérialisation ONNX pour inférence rapide | M |
| ML-12 | Pas de monitoring drift | PSI / KS test sur inputs + outputs | M |
| ML-13 | Pas de test adversarial | FGSM, text perturbation | L |
| ML-14 | Dataset d'entraînement non audité | Audit biais (genre, région, langue) | M |
| ML-15 | Pas de labellisation continue | Pipeline d'active learning | L |

### 2.5 Corrections Sécurité & Ops

| # | Constat | Correction proposée | Effort |
|---|---|---|---|
| S-01 | Pas d'authentification | JWT + refresh tokens, MFA optionnelle | M |
| S-02 | Pas de RBAC | Modèle `User` + `Role` + `Permission` | M |
| S-03 | Pas d'audit log | Table `AuditEvent` immuable | M |
| S-04 | Headers HTTP non sécurisés | Helmet (ou équivalent) | S |
| S-05 | Pas de HTTPS | Let's Encrypt + redirection | S |
| S-06 | Secrets en clair | Vault / AWS Secrets Manager / Infisical | M |
| S-07 | Pas de backup BDD | `pg_dump` quotidien + rétention 30 j | S |
| S-08 | Pas de monitoring | Prometheus + Grafana + alertes PagerDuty | M |
| S-09 | Pas de tracing | OpenTelemetry + Jaeger | M |
| S-10 | Pas de log centralisé | Loki / ELK | M |
| S-11 | Pas de containerisation | Dockerfile multi-stage + docker-compose | S |
| S-12 | Pas de CI/CD | GitHub Actions / GitLab CI | M |
| S-13 | Pas de scan de vulnérabilités | Trivy, Snyk, Bandit dans CI | S |
| S-14 | Pas de politique de mots de passe | Politique configurable (longueur, complexité) | S |
| S-15 | Pas de rate limiting par user | 100 req/min/user | S |
| S-16 | Pas de session timeout | 30 min d'inactivité, configurable | S |
| S-17 | Pas de GDPR / droit à l'oubli | Endpoint `DELETE /users/{id}/data` | M |
| S-18 | Pas de chiffrement at rest | LUKS ou KMS | M |
| S-19 | Pas de WAF | Cloudflare ou mod_security | M |
| S-20 | Pas de test de pénétration | Audit externe annuel | L |

---

## 3. Améliorations de l'existant (quick wins)

### 3.1 Module Ingestion

#### I-01 — Planificateur de scraping
* **Description** : cron intégré qui scrape tous les jours à 02:00, avec backoff et alerting.
* **Spec** :
  * `POST /api/scraper/schedule` (cron expression)
  * `GET /api/scraper/jobs` (historique)
  * `GET /api/scraper/jobs/{id}` (état détaillé, logs)
  * Alerte email/Slack si échec.

#### I-02 — Multi-sources
* **Description** : permettre d'ajouter d'autres portails (marchespublics.gov.ma, autres ministères).
* **Spec** :
  * Table `Source` (URL, type, sélecteurs, schedule).
  * Interface PipelineAdmin pour ajouter/éditer une source.
  * Tests unitaires par source.

#### I-03 — Détection de changement (Change Detection)
* **Description** : hash SHA-256 du ZIP, alerte si l'AO est modifié (rectificatif).
* **Spec** : `VersionHistory` liée au document.

#### I-04 — Webhooks sortants
* **Description** : notifier un système externe (ERP, Slack) sur nouvel AO.
* **Spec** : `POST /api/webhooks` (URL, secret, events).

#### I-05 — Mode prévisualisation
* **Description** : dry-run du scraping sans écriture BDD.
* **Spec** : `?dry_run=true` sur l'endpoint.

### 3.2 Module OCR & NLP

#### O-01 — Cache OCR
* **Description** : si un même PDF est ré-uploadé, réutiliser l'OCR existant.
* **Spec** : clé de cache = `sha256(pdf_bytes)`.

#### O-02 — Multi-pages avec structure
* **Description** : préserver la structure (titres, paragraphes, tableaux).
* **Spec** : sortie JSON `[{page, blocks: [{type, text, bbox}]}]`.

#### O-03 — Extraction avancée par LLM
* **Description** : pour les documents complexes, utiliser un LLM (Mistral, GPT-4o) en complément.
* **Spec** : endpoint `POST /api/nlp/llm_extract` avec prompt configurable.

#### O-04 — Support du tif / jpeg / png scannés
* **Description** : accepter les images scannées en plus des PDF.
* **Spec** : préprocessing uniforme.

#### O-05 — Détection automatique de la langue principale
* **Description** : classifier FR/AR/bilingue par page.
* **Spec** : utilisation de `langdetect` ou `fasttext`.

#### O-06 — Extraction des références réglementaires
* **Description** : identifier les articles de loi cités (ex. « article 11 du décret 2-22-431 »).
* **Spec** : regex + LLM en fallback.

#### O-07 — Extraction des contacts (email, téléphone, adresse)
* **Spec** : regex + validation.

#### O-08 — Tableur des entités extraites
* **Description** : export CSV/Excel par document.

### 3.3 Module Recherche FTS

#### S-01 — Opérateurs avancés
* `AND`, `OR`, `NOT`, `"phrase exacte"`, `wildcard*`, `fuzzy~`, `champ:value`.
* Documentation dans l'UI avec infobulle.

#### S-02 — Surlignage (highlight)
* **Spec** : utiliser `ts_headline` (Postgres) ou Elasticsearch highlighter.

#### S-03 — Facettes dynamiques
* **Description** : à gauche de la liste, afficher les facettes (catégorie, ville, type) avec compteurs.
* **Spec** : `?facet=category&facet=ville&...`.

#### S-04 — Sauvegarde de recherche
* **Description** : utilisateur peut nommer un set de filtres et le relancer.
* **Spec** : table `SavedSearch` (user_id, name, filters_json).

#### S-05 — Recherche floue (typo tolerance)
* **Spec** : `pg_trgm` + seuil de similarité.

#### S-06 — Recherche par embedding (V1)
* **Spec** : index HNSW sur embeddings normalisés, recherche par cosinus.

#### S-07 — Historique de recherche
* **Spec** : dernières 20 requêtes par utilisateur, recherche rapide en un clic.

#### S-08 — Suggestions de recherche
* **Spec** : type-ahead, basées sur l'historique, l'index et la saisonnalité.

#### S-09 — Export des résultats
* **CSV**, **Excel** (mise en forme), **JSON**, **PDF** (avec entête).

#### S-10 — Tri multi-critères
* **Spec** : dropdowns combinés (date + budget).

### 3.4 Module ML

#### M-01 — Réentraînement planifié
* **Spec** : cron hebdomadaire, A/B test automatique.

#### M-02 — Modèle de scoring de risque
* **Description** : combiner SVM + IsolationForest + heuristiques pour un score 0-100.
* **Spec** : régression logistique méta-apprise.

#### M-03 — Détection de doublons inter-documents
* **Spec** : MinHash / LSH sur TF-IDF ou embeddings.

#### M-04 — Classification multi-label
* **Description** : un AO peut appartenir à plusieurs catégories (Travaux + Études).
* **Spec** : `OneVsRestClassifier` sur SVM.

#### M-05 — Détection d'incohérences dans un DAO
* **Description** : vérifier que la somme des lots = montant total, que le délai est cohérent, etc.
* **Spec** : moteur de règles + LLM.

#### M-06 — Modèle de recommandation
* **Description** : pour un fournisseur, recommander les AO pertinents.
* **Spec** : filtrage collaboratif (embedding profil fournisseur + cosine).

#### M-07 — Embeddings multilingues
* **Spec** : `paraphrase-multilingual-MiniLM-L12-v2` (50+ langues).

### 3.5 Écrans existants

| Écran | Améliorations prioritaires |
|---|---|
| **LandingPage** | • Section « Derniers AO » (carrousel)<br>• Section « Statistiques temps réel » (compteurs animés)<br>• CTA différenciés selon persona<br>• Section « Témoignages / cas d'usage »<br>• Témoignage vidéo d'un acheteur<br>• Bandeau d'alertes (système opérationnel ou incident) |
| **Dashboard** | (voir 3.5 nouveau Dashboard Avancé §4.7) |
| **SearchFTS** | • Filtres avancés (type d'avis, qualif, agrément, état)<br>• Bouton Réinitialiser<br>• Surlignage des résultats<br>• Tri configurable<br>• Export CSV/Excel<br>• Sauvegarde de recherche<br>• Mode « Recherche experte » (opérateurs booléens)<br>• Compteur dynamique de résultats |
| **DocumentDetail** | • Bouton « Voir le PDF original »<br>• Bouton « Télécharger le texte OCR »<br>• Comparaison côte-à-côte avec un autre AO<br>• Bouton « Signaler une anomalie »<br>• Historique des versions<br>• Partage par lien signé (expiration)<br>• Section « Documents similaires » (cosine > 0.8)<br>• Annotation collaborative |
| **Explorer** | • Vue grille + liste<br>• Drag & drop pour réorganiser<br>• Sélection multiple (actions groupées)<br>• Filtres avancés<br>• Prévisualisation rapide (modal) |
| **Upload** | • Barre de progression globale<br>• Annulation individuelle<br>• Reprise après erreur<br>• Templates (formats attendus)<br>• Validation en temps réel |
| **PredictorML** | • Métriques étendues (precision/recall/F1 par classe)<br>• Matrice de confusion interactive<br>• Feature importance (top 20)<br>• Comparaison de versions (graphique)<br>• Distribution des scores<br>• Bouton « Rollback modèle » |
| **Monitoring** | • Dashboard Grafana intégré (iframe ou intégration)<br>• Alertes en temps réel<br>• Heatmap d'activité par service<br>• Trace d'une requête (request_id)<br>• Métriques custom (DAOs/jour, OCR p95) |
| **PipelineAdmin** | • Multi-sources<br>• Planificateur visuel (cron builder)<br>• Logs structurés colorés<br>• Bouton « Pause / Reprise »<br>• Historique des exécutions avec diff |

---

## 4. Nouveaux écrans

### E10 — Authentification & Gestion des utilisateurs

**Objectif** : sécuriser l'accès, gérer les profils et les permissions.

**Layout** :

```
┌─────────────────────────────────────────────────────┐
│  ┌──────────────────┐    ┌───────────────────────┐  │
│  │                  │    │                       │  │
│  │   LOGO + slogan  │    │   Formulaire Login    │  │
│  │                  │    │  • Email              │  │
│  │   Visuel         │    │  • Mot de passe       │  │
│  │   institutionnel │    │  • [ Se connecter ]   │  │
│  │                  │    │  • MFA (optionnel)     │  │
│  │   3 illustrations│    │  • [Mot de passe      │  │
│  │   : Sécurité,    │    │     oublié ?]         │  │
│  │   BI, Gouvernance│    │                       │  │
│  └──────────────────┘    └───────────────────────┘  │
└─────────────────────────────────────────────────────┘
```

**Fonctionnalités** :
1. **Login** : email + mot de passe + MFA (TOTP).
2. **Mot de passe oublié** :流程 par email, lien à durée limitée (15 min).
3. **Premier login** : forcer changement de mot de passe + acceptation CGU.
4. **Gestion des utilisateurs** (admin) : CRUD utilisateurs, attribution de rôles.
5. **Gestion des rôles** : éditeur de permissions (matrice rôle × ressource).
6. **Profil personnel** : avatar, nom, email, langue, thème, notifications.
7. **Historique de connexion** : IP, user-agent, géolocalisation approximative.
8. **Sessions actives** : liste des sessions, kill switch.
9. **2FA** : QR code, codes de secours, réinitialisation par admin.
10. **SSO** (V1) : Keycloak + OIDC pour intégration avec l'annuaire ministériel.

**Stack** :
* Backend : `authlib` (OIDC), `pyotp` (TOTP), `passlib[bcrypt]`.
* Frontend : page dédiée React, intégration `react-hook-form` + `zod`.
* Stockage : table `User`, `Role`, `Permission`, `Session`, `MfaSecret`, `AuditEvent`.

**Critères d'acceptation** :
- T-AU-001 à T-AU-011 du Fichier 1 passent.
- Aucune donnée sensible n'apparaît dans les logs.
- Audit log complet pour toute action.

---

### E11 — Centre d'alertes & watchlist personnalisée

**Objectif** : permettre à chaque utilisateur de définir ses centres d'intérêt et de recevoir des alertes.

**Layout** :

```
┌──────────────────────────────────────────────────────────────┐
│  Centre d'alertes              [+ Nouvelle alerte]           │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌─ Mes alertes actives ──────────────────────────────────┐  │
│  │ • Travaux routiers à Casablanca       🔔 3 nouveaux     │  │
│  │ • Études techniques > 1M MAD          🔕 0              │  │
│  │ • AO de la DGR                        🔔 1              │  │
│  └────────────────────────────────────────────────────────┘  │
│                                                              │
│  ┌─ Builder visuel ───────────────────────────────────────┐  │
│  │ Catégorie  : [Travaux routiers    ▼]                    │  │
│  │ Ville      : [Casablanca         ▼]                    │  │
│  │ Budget min : [1 000 000         ] MAD                  │  │
│  │ Budget max : [                       ] MAD              │  │
│  │ Mots-clés  : [pont, viaduc, échangeur                 ]  │  │
│  │ Fréquence  : ( ) Réel  (•) Quotidien  ( ) Hebdo        │  │
│  │ Canal      : [✓] Email  [✓] Toast  [ ] Webhook         │  │
│  │                                  [Enregistrer]         │  │
│  └────────────────────────────────────────────────────────┘  │
│                                                              │
│  ┌─ Historique des alertes (30 j) ────────────────────────┐  │
│  │ Date       | Alerte              | Nb résultats | Action│  │
│  │ 18/07/2026 | Travaux routiers... | 3            | [voir]│  │
│  │ 17/07/2026 | AO de la DGR        | 1            | [voir]│  │
│  └────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────┘
```

**Fonctionnalités** :
1. Création d'alertes avec builder visuel (sans code).
2. Support des filtres avancés : catégorie, type d'avis, qualification, agrément, ville, région, plage de dates, plage budgétaire.
3. Multi-canaux : email, toast (in-app), webhook.
4. Fréquence configurable : temps réel, quotidien (digest 8h), hebdomadaire (lundi 9h).
5. Historique des alertes envoyées.
6. Désactivation/activation en un clic.
7. Statistiques : taux d'ouverture, taux de clic.
8. Templates d'alertes pré-configurés (« Marchés de la DGR », « Études > 5M MAD »).

**Stack** :
* Backend : table `Alert`, `AlertTrigger`, `AlertDelivery`. Worker Dramatiq qui tourne toutes les 5 min.
* Frontend : page React, formulaire avec `react-hook-form`.
* Email : SMTP (configurable) ou SendGrid/Mailgun.

**Critères d'acceptation** :
- Alerte créée → au moins 1 livraison si matching AO.
- Digest quotidien reçu à l'heure configurée.
- Pas d'envoi doublon.

---

### E12 — Cartographie des AO

**Objectif** : visualiser géographiquement les AO.

**Layout** :

```
┌──────────────────────────────────────────────────────────────┐
│  Cartographie des appels d'offres                            │
├──────────────────────────────────────────────────────────────┤
│ Filtres : [Période ▼] [Catégorie ▼] [État ▼] [Montant ▼]   │
│                                                              │
│   ┌──────────────────────────────────────┐ ┌──────────────┐ │
│   │                                      │ │ Top régions  │ │
│   │        CARTE DU MAROC (Leaflet)      │ │ Casablanca   │ │
│   │   - Marqueurs par ville (nb AO)      │ │  1 250 AO    │ │
│   │   - Choroplèthe par région (€)       │ │ Rabat        │ │
│   │   - Pop-up au clic (détails)         │ │   850 AO     │ │
│   │                                      │ │ Marrakech    │ │
│   │                                      │ │   620 AO     │ │
│   └──────────────────────────────────────┘ └──────────────┘ │
│                                                              │
│   ┌─ Légende ───────────────────────────────────────────┐   │
│   │ • < 10 AO  • 10-50  • 50-100  • > 100               │   │
│   │ Couleur : bleu (peu) → rouge (beaucoup)             │   │
│   └─────────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────────┘
```

**Fonctionnalités** :
1. Carte choroplèthe du Maroc colorée par région (nb AO ou volume).
2. Marqueurs par ville avec popup (top 5 AO).
3. Heatmap par densité financière.
4. Filtres : période, catégorie, état, type, qualification, agréments.
5. Mode comparaison : 2 périodes côte-à-côte.
6. Export PNG / SVG de la carte.
7. Vue « Satellite » et « Plan ».
8. Recherche inversée : dessiner une zone, voir les AO à l'intérieur.

**Stack** :
* Frontend : `react-leaflet` + tuiles OpenStreetMap ou Mapbox.
* Backend : endpoint `GET /api/geo/aggregates?level=region|ville&...`.
* Données géo : GeoJSON officiel du Maroc (régions, provinces, communes).

**Critères d'acceptation** :
- Carte chargée < 2 s.
- Filtres réactifs (recalcul < 500 ms).
- 12 régions du Maroc correctement dessinées.

---

### E13 — Comparateur d'appels d'offres

**Objectif** : mettre en regard jusqu'à 5 AO similaires pour benchmarker.

**Layout** :

```
┌──────────────────────────────────────────────────────────────────┐
│  Comparateur d'appels d'offres                                   │
├──────────────────────────────────────────────────────────────────┤
│  [+ Ajouter un AO]   [Charger depuis le panier]   [Exporter PDF]│
│                                                                  │
│  ┌─ Sélection (max 5) ───────────────────────────────────────┐  │
│  │ [✓] AO 122/2024 - Travaux route Rabat-Salé              │  │
│  │ [✓] AO 89/2024  - Travaux route Casablanca-Settat        │  │
│  │ [ ] AO 145/2024 - Travaux route Marrakech-Agadir          │  │
│  │ [ ] AO 201/2024 - Études techniques nationales            │  │
│  │ [ ] AO 76/2024  - Fournitures bureau Rabat                │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│  ┌─ Comparaison côte-à-côte ───────────────────────────────┐    │
│  │ Critère        │ AO 122/24 │ AO 89/24  │ Médiane marché │    │
│  │ Référence      │ 122/2024  │ 89/2024   │ -              │    │
│  │ Catégorie      │ Travaux   │ Travaux   │ -              │    │
│  │ Type           │ Ouvert    │ Restreint │ -              │    │
│  │ Montant (MAD)  │ 12.5M     │ 8.2M      │ 10.3M ⚠        │    │
│  │ Caution (MAD)  │ 250 000   │ 164 000   │ 206 000        │    │
│  │ Délai          │ 12 mois   │ 18 mois   │ 14 mois        │    │
│  │ Ville          │ Rabat     │ Casa.     │ -              │    │
│  │ Date ouverture │ 15/09/24  │ 22/10/24  │ -              │    │
│  │ Date limite    │ 30/09/24  │ 05/11/24  │ -              │    │
│  │ Acheteur       │ DGR       │ DRE Casa. │ -              │    │
│  │ Qualif requise │ Q1-Q3     │ Q2-Q4     │ -              │    │
│  │ Agréments      │ -         │ -         │ -              │    │
│  │ Score risque   │ 78/100 🟢 │ 92/100 🟢 │ -              │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                  │
│  ┌─ Indicateurs visuels ──────────────────────────────────┐     │
│  │ • Graphique radar multi-critères                       │     │
│  │ • Courbe de distribution des montants de la catégorie  │     │
│  └────────────────────────────────────────────────────────┘     │
└──────────────────────────────────────────────────────────────────┘
```

**Fonctionnalités** :
1. Sélection de 2 à 5 AO.
2. Tableau comparatif côte-à-côte avec médiane du marché.
3. Mise en évidence des écarts (vert/orange/rouge).
4. Graphique radar multi-critères (jusqu'à 8 dimensions).
5. Courbe de distribution du marché (positionnement percentile).
6. Export PDF du comparatif.
7. Sauvegarde de comparaisons.
8. Partage par lien.

**Stack** :
* Frontend : page React + `recharts` (radar) + tableau.
* Backend : `GET /api/compare?ids=1,2,3` + `GET /api/market/median?categorie=X`.

**Critères d'acceptation** :
- Comparaison de 5 AO < 1 s.
- Médiane du marché correctement calculée.
- Export PDF < 5 s.

---

### E14 — Tableau de bord Acheteur

**Objectif** : pour chaque **maître d'ouvrage** (acheteur public), un dashboard dédié.

**Layout** :

```
┌──────────────────────────────────────────────────────────────────┐
│  Tableau de bord Acheteur : Direction Générale des Routes        │
├──────────────────────────────────────────────────────────────────┤
│  Filtres : [Période ▼] [Type ▼] [Catégorie ▼] [Comparer à ▼]   │
│                                                                  │
│  ┌─ KPIs Acheteur ─────────────────────────────────────────┐    │
│  │  📋 142 marchés          💰 856 M MAD cumulés           │    │
│  │  ⏱ Délai moyen 14.2 mois  📈 +12% vs N-1                │    │
│  │  🎯 Taux attribution 87%  ⚠️ 4 anomalies                │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                  │
│  ┌─ Évolution temporelle ──────────────────────────────────┐    │
│  │  Courbe mensuelle des publications (12 mois glissants)  │    │
│  │  Aire : volume financier                                 │    │
│  │  Ligne : nombre de marchés                               │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                  │
│  ┌─ Répartition par catégorie ─┐ ┌─ Top catégories ────────┐    │
│  │     [Camembert]            │ │ 1. Travaux routiers 58% │    │
│  │                             │ │ 2. Études techniques 22%│    │
│  └─────────────────────────────┘ │ 3. Ouvrages d'art    12% │    │
│                                  └─────────────────────────┘    │
│                                                                  │
│  ┌─ Carte choroplèthe (lieux d'exécution) ─────────────────┐    │
│  │  Maroc colorée par région selon les projets de l'acheteur│   │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                  │
│  ┌─ Anomalies détectées ───────────────────────────────────┐    │
│  │  • AO 122/2024 — caution disproportionnée (rouge)       │    │
│  │  • AO 89/2024 — délai irréaliste (orange)               │    │
│  │  [Voir toutes les anomalies]                             │    │
│  └─────────────────────────────────────────────────────────┘    │
└──────────────────────────────────────────────────────────────────┘
```

**Fonctionnalités** :
1. Page dédiée par acheteur (route : `/acheteur/:id`).
2. KPIs Acheteur.
3. Évolution temporelle.
4. Répartition par catégorie.
5. Carte des lieux d'exécution.
6. Liste des anomalies.
7. Comparaison vs N-1.
8. Export PDF / PNG.
9. Liste filtrable des AO de l'acheteur.

**Stack** :
* Frontend : page React, `recharts`, `react-leaflet`.
* Backend : `GET /api/acheteur/:id/dashboard?from=...&to=...`.

**Critères d'acceptation** :
- Page < 2 s.
- Comparaison N-1 fonctionnelle.
- Drill-down cliquable.

---

### E15 — Tableau de bord Fournisseur

**Objectif** : pour une **entreprise** (fournisseur), un dashboard orienté veille et réponse aux AO.

**Layout** :

```
┌──────────────────────────────────────────────────────────────────┐
│  Tableau de bord Fournisseur : BTP Maroc SARL                    │
│  Profil : Qualification Q3, Agrément Routes, Casablanca          │
├──────────────────────────────────────────────────────────────────┤
│  ┌─ Opportunités du jour ───────────────────────────────────┐    │
│  │  5 nouveaux AO correspondent à votre profil              │    │
│  │  • AO 122/2024 — Travaux routiers, Casablanca, 12.5M MAD │    │
│  │  • AO 89/2024  — ...                                     │    │
│  │  [Voir toutes les opportunités]                           │    │
│  └──────────────────────────────────────────────────────────┘    │
│                                                                  │
│  ┌─ Score de compatibilité ─────────────────────────────────┐    │
│  │  Pour chaque AO : % de compatibilité avec votre profil    │    │
│  │  (qualifs, agréments, capacité financière, géographique) │    │
│  └──────────────────────────────────────────────────────────┘    │
│                                                                  │
│  ┌─ Statistiques mes soumissions ───────────────────────────┐    │
│  │  • Soumissions : 23                                       │    │
│  │  • Taux de succès : 13% (3 attributions)                  │    │
│  │  • Délai moyen d'instruction : 45 jours                   │    │
│  │  • Montant cumulé attribué : 18.4M MAD                    │    │
│  └──────────────────────────────────────────────────────────┘    │
│                                                                  │
│  ┌─ Veille personnalisée ───────────────────────────────────┐    │
│  │  Vos alertes actives : 3                                  │    │
│  │  • [Travaux routiers à Casa] 🔔 2 nouveaux                │    │
│  │  • [Études techniques > 1M] 🔕 0                          │    │
│  │  [Gérer mes alertes]                                      │    │
│  └──────────────────────────────────────────────────────────┘    │
└──────────────────────────────────────────────────────────────────┘
```

**Fonctionnalités** :
1. Profil fournisseur (qualifs, agréments, capacité).
2. Opportunités classées par compatibilité.
3. Suivi des soumissions (statut : à déposer, déposé, en cours, gagné, perdu).
4. Statistiques de performance.
5. Veille et alertes (cf. E11).
6. Documents utiles (modèles, attestations à renouveler).
7. Calendrier des deadlines à venir.

**Stack** :
* Frontend : page React + agenda.
* Backend : `GET /api/fournisseur/:id/dashboard`, `GET /api/fournisseur/:id/opportunites`.

**Critères d'acceptation** :
- Score de compatibilité calculé correctement.
- Statistiques mises à jour quotidiennement.

---

### E16 — Analytics Avancés (DataViz)

**Objectif** : une **salle de contrôle BI** avec des dizaines de widgets.

**Layout (style Power BI / Looker)** :

```
┌──────────────────────────────────────────────────────────────────┐
│  Analytics Avancés                          [+ Widget] [Exporter]│
├──────────────────────────────────────────────────────────────────┤
│  ┌─ Filtres globaux ─────────────────────────────────────────┐ │
│  │ Période | Catégories | Régions | Maîtres d'ouvrage | Type │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                  │
│  ┌──────────────────┐ ┌──────────────────┐ ┌─────────────────┐  │
│  │ KPI : Volume     │ │ KPI : Nb AO      │ │ KPI : Délai moy │  │
│  │ 1.2 Md MAD       │ │ 1 245            │ │ 13.2 mois       │  │
│  │ ↑ +15% vs N-1    │ │ ↑ +8% vs N-1     │ │ ↓ -3% vs N-1    │  │
│  └──────────────────┘ └──────────────────┘ └─────────────────┘  │
│                                                                  │
│  ┌─ Courbe temporelle ─────────────┐ ┌─ Camembert catégories ┐  │
│  │  Aire : volume financier       │ │                       │  │
│  │  Ligne : nombre d'AO           │ │   [Camembert]         │  │
│  │  (12 mois glissants)           │ │                       │  │
│  └─────────────────────────────────┘ └───────────────────────┘  │
│                                                                  │
│  ┌─ Heatmap calendrier ──────────────────────────────────────┐  │
│  │   jan  feb  mar  apr  may  jun  jul  aug  sep  oct  nov  │  │
│  │   ░░   ▓▓   ██   ██   ▓▓   ░░   ░░   ░░   ▓▓   ██   ██   │  │
│  └────────────────────────────────────────────────────────────┘  │
│                                                                  │
│  ┌─ Top 10 acheteurs ───────────────────────────────────────┐   │
│  │  [BarChart horizontal]                                     │  │
│  └────────────────────────────────────────────────────────────┘  │
│                                                                  │
│  ┌─ Funnel cycle de vie AO ──┐ ┌─ Treemap catégories × régions┐│
│  │ Publié → Ouvert → Attribué│ │   [Treemap]                  ││
│  │ [Funnel chart]            │ │                              ││
│  └───────────────────────────┘ └──────────────────────────────┘│
└──────────────────────────────────────────────────────────────────┘
```

**Widgets proposés (15 minimum)** :
1. KPI Volume cumulé
2. KPI Nombre d'AO
3. KPI Délai moyen
4. KPI Taux d'attribution
5. KPI Taux d'anomalies
6. Courbe temporelle (volume + nb)
7. Camembert catégories
8. Heatmap calendrier (publications)
9. BarChart top acheteurs
10. Funnel cycle de vie
11. Treemap catégories × régions
12. Carte choroplèthe Maroc
13. Bubble chart (volume × durée × risque)
14. Sankey (acheteur → catégorie → région)
15. Radar multi-axes (synthétique)
16. Word cloud des objets d'AO
17. Boîte à moustaches des montants par catégorie
18. Tableau des anomalies récentes

**Fonctionnalités** :
1. Drag & drop des widgets (librairie `react-grid-layout`).
2. Sauvegarde de dashboards personnalisés par utilisateur.
3. Filtres globaux qui s'appliquent à tous les widgets.
4. Mode focus (un widget en plein écran).
5. Export PDF / PNG / Excel.
6. Sous-tableaux (« dashboard du jour », « dashboard hebdomadaire »).
7. Mode présentation (rotation automatique).

**Stack** :
* Frontend : `react-grid-layout` + `recharts` + `d3.js` pour les widgets custom.
* Backend : endpoints d'agrégation, cache Redis.

**Critères d'acceptation** :
- Layout responsive (mobile, tablette, desktop).
- Sauvegarde persistée.
- Filtres globaux propagés < 300 ms.

---

### E17 — Prédictif & Prévisions

**Objectif** : anticiper les volumes d'AO, les dérives budgétaires, les risques.

**Layout** :

```
┌──────────────────────────────────────────────────────────────────┐
│  Prédictif & Prévisions                                          │
├──────────────────────────────────────────────────────────────────┤
│  ┌─ Prévision de volume (12 prochains mois) ─────────────────┐  │
│  │  Courbe réelle + intervalle de confiance                   │  │
│  │  SARIMA / Prophet                                         │  │
│  │  Accuracy backtest MAPE : 12%                             │  │
│  └────────────────────────────────────────────────────────────┘  │
│                                                                  │
│  ┌─ Prévision par catégorie ──────────────────────────────────┐   │
│  │  Facettes par catégorie, forecast 6 mois                  │   │
│  └────────────────────────────────────────────────────────────┘  │
│                                                                  │
│  ┌─ Risque de dépassement budgétaire ─────────────────────────┐   │
│  │  Pour chaque AO actif : probabilité de dépassement        │   │
│  │  Modèle : classification binaire                          │   │
│  │  Score de risque 0-100                                    │   │
│  └────────────────────────────────────────────────────────────┘  │
│                                                                  │
│  ┌─ Détection de saisonnalité ───────────────────────────────┐   │
│  │  Décomposition STL (saisonnier + tendance + résiduel)    │   │
│  └────────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────────┘
```

**Fonctionnalités** :
1. **Prévision de volume** : Prophet / SARIMA, 12 mois à venir.
2. **Prévision budgétaire** : trend + intervalle de confiance.
3. **Risque de dépassement** : modèle supervisé sur historique (features : catégorie, montant, acheteur, durée).
4. **Risque d'infructuosité** : probabilité qu'un AO n'aboutisse pas.
5. **Saisonnalité** : décomposition, mise en évidence des pics (mai-juin, sept-oct).
6. **Backtest** : comparaison prédictions vs réalité sur les 12 derniers mois.
7. **Export** des prévisions (CSV, Excel).

**Stack** :
* Backend : `prophet`, `statsmodels`, `scikit-learn`. Modèles versionnés avec MLflow.
* Frontend : page React + `recharts` (lignes, bandes de confiance).

**Critères d'acceptation** :
- MAPE < 15 % sur 12 mois de backtest.
- Intervalle de confiance 95 %.

---

### E18 — Audit & Traçabilité

**Objectif** : conformité réglementaire, auditabilité complète.

**Layout** :

```
┌──────────────────────────────────────────────────────────────────┐
│  Audit & Traçabilité                                             │
├──────────────────────────────────────────────────────────────────┤
│  Filtres : [Utilisateur ▼] [Action ▼] [Ressource ▼] [Période ▼] │
│                                                                  │
│  ┌─ Statistiques ───────────────────────────────────────────┐    │
│  │  18 472 événements audités (30 j)                        │    │
│  │  Top users : admin@dsi.gov.ma (2 134), analyst@... (876) │    │
│  │  Top actions : login (8 200), search (5 100), ...        │    │
│  └──────────────────────────────────────────────────────────┘    │
│                                                                  │
│  ┌─ Journal détaillé ───────────────────────────────────────┐    │
│  │ Date       | User    | Action       | Ressource | IP     │    │
│  │ 18/07 14:32| admin@  | model.train  | svm_v1.2  | 10.0...│    │
│  │ 18/07 14:30| admin@  | user.create  | user:42   | 10.0...│    │
│  │ 18/07 14:25| analyst@| search.query | q="..."   | 10.0...│    │
│  │ 18/07 14:22| analyst@| doc.download | doc:122   | 10.0...│    │
│  │ [Pagination] [Export CSV]                                │    │
│  └──────────────────────────────────────────────────────────┘    │
│                                                                  │
│  ┌─ Vue par ressource ──────────────────────────────────────┐    │
│  │  Sélectionner un document / modèle / utilisateur         │    │
│  │  → voir tout son historique                               │    │
│  └──────────────────────────────────────────────────────────┘    │
└──────────────────────────────────────────────────────────────────┘
```

**Fonctionnalités** :
1. Journal de tous les événements.
2. Filtres multi-dimensionnels.
3. Vue par utilisateur / par ressource.
4. Export pour audit externe.
5. Rétention configurable (par défaut 5 ans).
6. Détection d'anomalies comportementales (login depuis IP inhabituelle).
7. Alertes en temps réel (admin notifié sur action sensible).

**Stack** :
* Backend : table `AuditEvent` append-only, déclencheur SQL pour empêcher UPDATE/DELETE.
* Frontend : page React avec tableau virtualisé.

**Critères d'acceptation** :
- Tout événement sensible est journalisé.
- Impossibilité de modifier l'historique.
- Recherche full-text sur les événements.

---

### E19 — Labellisation collaborative

**Objectif** : produire un dataset de qualité pour les modèles ML.

**Layout** :

```
┌──────────────────────────────────────────────────────────────────┐
│  Labellisation collaborative                                     │
├──────────────────────────────────────────────────────────────────┤
│  Campagne : Classification de 500 AO « zone grise »              │
│  Progression : 234 / 500 (47%)                                  │
│                                                                  │
│  ┌─ Document à labelliser ──────────────────────────────────┐    │
│  │  Référence : AO 122/2024                                  │    │
│  │  Objet : Travaux d'aménagement de la route nationale ... │    │
│  │  Texte OCR : [aperçu 5 lignes + bouton "voir tout"]       │    │
│  │                                                          │    │
│  │  Catégorie : ( ) Travaux routiers                         │    │
│  │              (•) Ouvrages d'art                           │    │
│  │              ( ) Études techniques                        │    │
│  │              ( ) Fournitures                              │    │
│  │  Score IA suggéré : Ouvrages d'art (87%)                 │    │
│  │                                                          │    │
│  │  Tags libres : [pont, viaduc, métallique]                │    │
│  │  Notes : "Semble inclure une étude géotechnique"        │    │
│  │                                                          │    │
│  │  [Précédent] [Sauter] [Confirmer] [Signaler doute]       │    │
│  └──────────────────────────────────────────────────────────┘    │
│                                                                  │
│  ┌─ Statistiques de la campagne ────────────────────────────┐    │
│  │  Agreement inter-annotateurs (Cohen's κ) : 0.78          │    │
│  │  Documents validés par 2+ : 189                           │    │
│  │  Documents en désaccord : 22                              │    │
│  └──────────────────────────────────────────────────────────┘    │
└──────────────────────────────────────────────────────────────────┘
```

**Fonctionnalités** :
1. File de documents à labelliser.
2. Formulaire de labellisation (catégorie, tags, notes).
3. Suggestion IA + correction humaine.
4. Multi-annotateur avec calcul d'accord (Cohen's κ, Fleiss' κ).
5. Mode « difficile » (entraînement actif : le modèle demande de l'aide sur les cas ambigus).
6. Progression et quotas.
7. Export du dataset labellisé (CSV, JSONL, COCO format).

**Stack** :
* Backend : tables `LabelingTask`, `LabelingAnnotation`. Worker Dramatiq pour la distribution.
* Frontend : interface style Label Studio, simplifiée.
* Modèle d'active learning : incertitude = entropie des probabilités SVM.

**Critères d'acceptation** :
- Au moins 2 annotateurs par document (gold standard).
- Métriques d'accord affichées.
- Export conforme au format attendu par scikit-learn.

---

### E20 — Catalogue des modèles ML

**Objectif** : gouvernance MLOps — référencer toutes les versions de modèles.

**Layout** :

```
┌──────────────────────────────────────────────────────────────────┐
│  Catalogue des modèles ML                                        │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─ svm_classifier ──────────────────────────────────────────┐  │
│  │  Catégorie : Classification                               │  │
│  │  Versions :                                               │  │
│  │  v1.3 (prod)   2026-07-12  accuracy 88%   ◀ actuelle     │  │
│  │  v1.2          2026-06-28  accuracy 86%                   │  │
│  │  v1.1          2026-06-15  accuracy 84%                   │  │
│  │  v1.0          2026-05-30  accuracy 81%                   │  │
│  │                                                          │  │
│  │  [Rollback vers v1.2] [Comparer] [Promouvoir en staging] │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│  ┌─ isolation_forest ────────────────────────────────────────┐  │
│  │  Catégorie : Détection d'anomalies                        │  │
│  │  Versions :                                               │  │
│  │  v2.0 (prod)   2026-07-01  contamination 0.05            │  │
│  │  v1.5          2026-06-15                                  │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│  ┌─ embeddings_v1 ───────────────────────────────────────────┐  │
│  │  Catégorie : Recherche sémantique                         │  │
│  │  v1.0  paraphrase-multilingual-MiniLM-L12-v2             │  │
│  └──────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────────┘
```

**Fonctionnalités** :
1. Liste de tous les modèles avec versions.
2. Métriques par version.
3. Comparaison côte-à-côte.
4. Rollback en un clic.
5. Promotion staging → production.
6. Lineage : features utilisées, dataset d'entraînement, hash du code.
7. Logs d'inférence.
8. Tests de régression attachés.

**Stack** :
* Backend : MLflow Tracking + Model Registry (ou custom si budget MLflow trop lourd).
* Frontend : page React.

**Critères d'acceptation** :
- Toutes les versions sont versionnées (Git LFS + DVC).
- Rollback < 30 s.
- Lineage complet (code + data + hyperparams + métriques).

---

### E21 — Notifications & Messagerie

**Objectif** : un centre de notifications unifié.

**Layout** :

```
┌──────────────────────────────────────────────────────────────────┐
│  🔔 Notifications (12 non lues)                                  │
├──────────────────────────────────────────────────────────────────┤
│  Filtres : [Tout ▼] [Système] [Alertes] [Anomalies] [Mentions] │
│                                                                  │
│  ● 14:32  Anomalie détectée — AO 122/2024 (caution 2x)    [voir]│
│  ● 14:25  Nouvel AO correspond à votre alerte « Ponts »   [voir]│
│  ● 09:00  Le modèle SVM v1.3 a été promu en production    [voir]│
│  ● Hier   3 nouveaux AO publiés par la DGR                [voir]│
│  ○ 18/07  Rapport hebdomadaire envoyé                       [voir]│
│                                                                  │
│  [Tout marquer comme lu] [Paramètres de notification]            │
└──────────────────────────────────────────────────────────────────┘
```

**Fonctionnalités** :
1. Centre de notifications in-app.
2. Cloche avec badge.
3. WebSocket pour temps réel.
4. Web Notifications API pour le bureau.
5. Email digest (configurable).
6. Préférences fines (par type, par canal).

**Stack** :
* Backend : table `Notification`, WebSocket FastAPI (`websockets`).
* Frontend : `react-hot-toast` + page dédiée.

---

### E22 — Rapports programmés

**Objectif** : générer et distribuer automatiquement des rapports PDF/Excel.

**Layout (modal de configuration)** :

```
┌─────────────────────────────────────────────────────┐
│  Nouveau rapport programmé                          │
├─────────────────────────────────────────────────────┤
│  Nom : Rapport hebdomadaire DSI                    │
│  Type : PDF [▼]                                     │
│  Source :                                           │
│    (•) Dashboard Analytics Avancés                 │
│    ( ) Comparateur                                  │
│    ( ) Custom (SQL)                                 │
│  Période : ( ) Hier  (•) Semaine dernière  ( ) Mois│
│  Destinataires : [email1, email2, +]               │
│  Fréquence : (•) Hebdomadaire (lundi 9h)            │
│              ( ) Mensuel (1er du mois)              │
│  Format :  (✓) PDF  (✓) Excel  ( ) Lien seul        │
│                                                     │
│  [Tester] [Enregistrer] [Annuler]                  │
└─────────────────────────────────────────────────────┘
```

**Fonctionnalités** :
1. Configuration de rapports récurrents.
2. Rendu PDF avec graphiques (ReportLab, WeasyPrint).
3. Export Excel (openpyxl).
4. Distribution email.
5. Stockage dans la GED (audit, re-téléchargement).
6. Prévisualisation avant envoi.

**Stack** :
* Backend : Celery beat + WeasyPrint + openpyxl.
* Frontend : modal + page de gestion des rapports.

---

### E23 — Mobile-first & PWA

**Objectif** : expérience mobile native.

**Layout (mobile)** :

```
┌──────────────────────────────┐
│  ☰  GED-BI            🔔 3   │
├──────────────────────────────┤
│  Bonjour, Analyste 👋        │
│                              │
│  ┌────────────────────────┐  │
│  │  📊 Dashboard          │  │
│  │  Volume : 1.2 Md MAD   │  │
│  │  Nouveaux : 12         │  │
│  └────────────────────────┘  │
│                              │
│  ┌────────────────────────┐  │
│  │  🔍 Recherche          │  │
│  │  [_______________] 🎤  │  │
│  └────────────────────────┘  │
│                              │
│  ┌────────────────────────┐  │
│  │  🔔 Alertes            │  │
│  │  3 nouvelles ce matin  │  │
│  └────────────────────────┘  │
│                              │
│  ┌────────────────────────┐  │
│  │  📋 Mes tâches         │  │
│  │  5 docs à labelliser   │  │
│  └────────────────────────┘  │
│                              │
│  [🏠] [🔍] [🔔] [👤]        │
└──────────────────────────────┘
```

**Fonctionnalités** :
1. PWA installable.
2. Mode offline (cache des derniers AO consultés).
3. Notifications push.
4. Gestes swipe (swipe pour archiver une notif).
5. Capture photo d'un document → OCR direct.
6. Géolocalisation pour AO à proximité.

**Stack** :
* Frontend : `vite-plugin-pwa`, manifest.json, service worker.
* Push : Web Push API + VAPID.

---

### E24 — Data Lineage & Quality

**Objectif** : transparence sur la qualité et la traçabilité des données.

**Layout** :

```
┌──────────────────────────────────────────────────────────────────┐
│  Data Lineage                                                    │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Source ──► Scraping ──► OCR ──► NLP ──► BDD ──► Dashboard      │
│  (site)   (Playwright)  (Tesseract)  (spaCy) (Postgres) (Recharts)│
│                                                                  │
│  ┌─ Qualité par étape ──────────────────────────────────────┐   │
│  │  Scraping : 98.2% succès                                 │   │
│  │  OCR : 91.4% confidence moyenne                          │   │
│  │  NLP : 87.1% extraction correcte (échantillon 50)         │   │
│  │  BDD : 0 documents orphelins                             │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                  │
│  ┌─ Anomalies de qualité ───────────────────────────────────┐   │
│  │  3 documents sans montant extrait                        │   │
│  │  1 document avec OCR confidence < 50%                    │   │
│  │  2 documents en doublon (résolu)                         │   │
│  └──────────────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────────────┘
```

**Fonctionnalités** :
1. Vue graphe du lineage.
2. Métriques de qualité par étape.
3. Alertes qualité (seuils configurables).
4. Action corrective en un clic (relancer OCR, etc.).
5. Historique des incidents qualité.

**Stack** :
* Backend : Great Expectations + métriques custom.
* Frontend : page React + `react-flow` pour le graphe.

---

## 5. Nouvelles fonctionnalités transverses

### 5.1 Recherche sémantique par embedding (LLM)

**Description** : permet de trouver un AO conceptuellement proche d'une question en langage naturel, pas seulement par mots-clés.

**Spec** :
1. Embeddings multilingues : `paraphrase-multilingual-MiniLM-L12-v2` (par défaut) ou `text-embedding-3-small` (OpenAI) ou `embed-multilingual-v3.0` (Cohere).
2. Index vectoriel : `pgvector` (HNSW) ou `Qdrant` ou `Weaviate`.
3. Endpoint `POST /api/search/semantic` (`query: "Quels AO concernent la construction de ponts en zone montagneuse ?"`).
4. Re-ranking hybride : combiner BM25 + cosinus via `Reciprocal Rank Fusion`.
5. UI : toggle « Mots-clés / Sémantique » dans SearchFTS.

**Valeur** : trouver des AO qu'on ne sait pas chercher par mots-clés, gain de temps pour les nouveaux arrivants.

**Effort** : M (1-2 sprints)

### 5.2 Chatbot Q&A sur les DAO

**Description** : poser une question en langage naturel sur un ou plusieurs DAO.

**Spec** :
1. Stack : RAG (Retrieval-Augmented Generation) avec LangChain ou LlamaIndex.
2. LLM : Mistral 7B (auto-hébergé) ou GPT-4o (API).
3. Sources : texte OCR du/des DAO sélectionnés.
4. Mémoire de conversation (par session).
5. Citations cliquables vers le passage source.
6. Streaming des réponses.
7. Garde-fous : refus de répondre si hors contexte, indication du niveau de confiance.

**Layout** :
```
┌────────────────────────────────────────────┐
│  💬 Assistant DAO                          │
├────────────────────────────────────────────┤
│  Contexte : [AO 122/2024 ▼] [+ Ajouter]    │
│                                            │
│  Vous : Quel est le délai d'exécution ?    │
│  Bot : Le délai d'exécution est de 12 mois │
│  [Source : page 3, paragraphe 2]           │
│                                            │
│  Vous : Et la caution provisoire ?         │
│  Bot : La caution est fixée à 250 000 MAD  │
│  [Source : page 5, paragraphe 1]           │
│                                            │
│  [Tapez votre question...]            [▶]  │
└────────────────────────────────────────────┘
```

**Valeur** : extraire une info précise d'un PDF de 200 pages en 5 secondes.

**Effort** : L (3-4 sprints)

### 5.3 Résumés automatiques

**Description** : un résumé exécutif de chaque AO (5 phrases clés).

**Spec** :
1. Pipeline : `textrank` (extractive) + LLM (abstractive, optionnel).
2. Génération à l'upload + cache.
3. Affichage en haut du DocumentDetail.
4. Possibilité de régénérer.
5. Multi-langue (FR/AR).

**Valeur** : lecture rapide avant d'ouvrir le PDF.

**Effort** : M

### 5.4 i18n FR/AR

**Description** : interface bilingue avec support RTL.

**Spec** :
1. `i18next` côté front, `gettext` côté back (emails).
2. Bundles : `fr.json`, `ar.json` (par namespace : common, dashboard, search, etc.).
3. Détection automatique de la langue navigateur.
4. Sélecteur de langue persistant.
5. Layout RTL pour l'arabe (Tailwind `dir="rtl"`).
6. Nombres en chiffres arabes (option).
7. Calendrier hégirien (option, en plus du grégorien).
8. Charts : labels traduits.

**Effort** : M-L (selon le volume de chaînes)

### 5.5 Accessibilité WCAG 2.1 AA

**Spec** :
1. Tous les éléments interactifs navigables au clavier.
2. Contraste ≥ 4.5:1.
3. `aria-label` sur les icônes boutons.
4. Sous-titres sur les vidéos.
5. Mode daltonien (palettes alternatives).
6. Mode contraste élevé.
7. Test avec NVDA / VoiceOver.
8. Audit Lighthouse ≥ 90.

**Effort** : M

### 5.6 Multi-tenant

**Description** : héberger plusieurs administrations (autres ministères, collectivités).

**Spec** :
1. Champ `tenant_id` sur toutes les tables.
2. Row-Level Security (RLS) PostgreSQL.
3. Sous-domaine par tenant (`acme.ged-bi.ma`) ou path (`/acme`).
4. Branding customisable (logo, couleur primaire).
5. Isolation des données (pas de fuite inter-tenant).

**Effort** : L (refonte importante)

### 5.7 API publique & Open Data

**Description** : exposer certaines données en open data.

**Spec** :
1. Endpoints publics (sans auth) : statistiques agrégées, top catégories, volume par région.
2. Documentation OpenAPI séparée.
3. Rate limiting spécifique (200 req/h par IP).
4. Licence CC-BY-SA 4.0.
5. Export CSV/JSON en masse.
6. Miroir data.gouv.ma (synchro quotidienne).

**Effort** : M

### 5.8 Workflow d'approbation

**Description** : circuit de validation pour les actions sensibles (publication de rapport, modification modèle).

**Spec** :
1. Moteur de workflow (Camunda léger ou custom).
2. Étapes : demandeur → validateur N1 → validateur N2 → exécution.
3. Notifications à chaque étape.
4. Délai SLA configurable.
5. Possibilité de délégation.
6. Historique complet.

**Effort** : L

### 5.9 Sauvegarde de recherche & alertes email

(cf. E11)

### 5.10 Signature électronique des documents

**Description** : signer numériquement les rapports exportés.

**Spec** :
1. Signature PDF (PAdES).
2. Certificat X.509 stocké sur HSM.
3. Horodatage qualifié.
4. Vérification en ligne (lien vers le document signé).
5. Intégration possible avec Barid eSign.

**Effort** : M

---

## 6. Architecture cible

```
┌──────────────────────────────────────────────────────────────────┐
│                          CLIENTS                                 │
│  Web (React PWA) │ Mobile (PWA) │ Email │ API consumers          │
└──────────┬───────────────────────────────────────────────────────┘
           │
           ▼
┌──────────────────────────────────────────────────────────────────┐
│                      API GATEWAY                                 │
│  Traefik / Nginx │ Auth │ Rate limit │ CORS │ TLS │ WAF         │
└──────────┬───────────────────────────────────────────────────────┘
           │
           ▼
┌──────────────────────────────────────────────────────────────────┐
│                    SERVICES MÉTIER (FastAPI)                      │
│  ┌──────────┬──────────┬──────────┬──────────┬──────────────┐    │
│  │ Search   │ Analytics│ ML       │ Workflow │ Notification │    │
│  │ Service  │ Service  │ Service  │ Service  │ Service      │    │
│  └────┬─────┴────┬─────┴────┬─────┴────┬─────┴──────┬───────┘    │
│       │          │          │          │            │            │
└───────┼──────────┼──────────┼──────────┼────────────┼────────────┘
        │          │          │          │            │
        ▼          ▼          ▼          ▼            ▼
┌──────────────────────────────────────────────────────────────────┐
│                     COUCHE DONNÉES                                │
│  ┌────────────┐ ┌─────────────┐ ┌────────────┐ ┌──────────────┐  │
│  │ PostgreSQL │ │ Redis cache │ │ Elasticsearch│ MinIO/S3    │  │
│  │ (données)  │ │ + queue     │ │ (search)   │ │ (fichiers)   │  │
│  └────────────┘ └─────────────┘ └────────────┘ └──────────────┘  │
│  ┌────────────┐ ┌─────────────┐ ┌────────────┐                  │
│  │ Clickhouse │ │ Qdrant      │ │ MLflow     │                  │
│  │ (OLAP)     │ │ (vectors)   │ │ (registry) │                  │
│  └────────────┘ └─────────────┘ └────────────┘                  │
└──────────────────────────────────────────────────────────────────┘
        │
        ▼
┌──────────────────────────────────────────────────────────────────┐
│                  PIPELINE DE DONNÉES                              │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐             │
│  │ Scraper  │ │ OCR      │ │ NLP      │ │ Embedding│             │
│  │ (Airflow │ │ Worker   │ │ Worker   │ │ Worker   │             │
│  │ DAG)     │ │          │ │          │ │          │             │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘             │
└──────────────────────────────────────────────────────────────────┘
        │
        ▼
┌──────────────────────────────────────────────────────────────────┐
│                     OBSERVABILITÉ                                 │
│  Prometheus + Grafana + Loki + Tempo + Sentry + Alertmanager    │
└──────────────────────────────────────────────────────────────────┘
```

**Choix techniques clés** :
- **Orchestration** : Airflow (DAGs data) + Celery/Dramatiq (tâches async).
- **Recherche** : Elasticsearch (mature, facettes riches) ou Postgres FTS (plus simple).
- **Vecteurs** : Qdrant (open source, simple) ou pgvector (intégré Postgres).
- **OLAP** : Clickhouse ou DuckDB (pour les analytics rapides).
- **Stockage objet** : MinIO (S3-compatible, on-premise).
- **MLOps** : MLflow (tracking + registry + serving).

---

## 7. Roadmap produit

### 7.1 Roadmap MVP (3 mois)

**Objectif** : corriger les P0 du Fichier 1, ajouter l'authentification, et finaliser le mapping avec le formulaire source.

| Sprint | Objectif | Livrables |
|---|---|---|
| **S1** | Durcir l'existant | • Auth JWT + RBAC<br>• Audit log<br>• Aligner BDD sur les champs `criteres.aspx`<br>• Tests E2E (Cypress) : 10 scénarios |
| **S2** | Compléter la recherche | • Filtres : type d'avis, qualif, agrément, état, date ouverture, date limite<br>• Tri configurable<br>• Bouton Réinitialiser<br>• Surlignage<br>• Export CSV/Excel<br>• Tests T-FT-*** (P0+P1) |
| **S3** | Enrichir le Dashboard | • 10 widgets supplémentaires (cf. E16)<br>• Filtres temporels<br>• Comparaison N vs N-1<br>• Export PNG/PDF<br>• Tests T-DB-*** (P0+P1) |
| **S4** | Ops & Qualité | • Dockerisation<br>• CI/CD GitHub Actions<br>• Prometheus + Grafana<br>• Sentry<br>• Tests T-AU-*** et T-SE-*** passants |
| **S5** | ML & Données | • Extraction type d'avis, qualif, agrément (NLP)<br>• IsolationForest tuning + explicabilité<br>• Watchlist évoluée<br>• Réentraînement planifié |
| **S6** | i18n & PWA | • i18next FR/AR + RTL<br>• PWA installable<br>• Notifications navigateur<br>• Tests E2E en arabe |

**KPIs MVP** :
- Couverture fonctionnelle ≥ 90 % du formulaire source
- 100 % des tests P0 passent
- Couverture code ≥ 80 %
- Lighthouse ≥ 90
- Auth + RBAC opérationnels
- Déploiement one-click via `docker compose up`

### 7.2 Roadmap V1 (6 mois)

**Objectif** : devenir une plateforme BI à part entière.

| # | Épic | Livrables |
|---|---|---|
| 1 | **Centre d'alertes** (E11) | Builder visuel, multi-canaux, fréquence configurable |
| 2 | **Cartographie** (E12) | Leaflet, choroplèthe, marqueurs, heatmap |
| 3 | **Comparateur** (E13) | Sélection multi-AO, radar, médiane marché |
| 4 | **Dashboard Acheteur** (E14) | Page dédiée par maître d'ouvrage |
| 5 | **Dashboard Fournisseur** (E15) | Profil, score compatibilité, suivi soumissions |
| 6 | **Rapports programmés** (E22) | PDF/Excel auto, distribution email |
| 7 | **Recherche sémantique** (5.1) | Embeddings, pgvector, hybrid search |
| 8 | **Chatbot Q&A** (5.2) | RAG sur les DAO, streaming, citations |
| 9 | **Résumés automatiques** (5.3) | Résumé exécutif 5 phrases par AO |
| 10 | **Prédictif** (E17) | Prévision de volume, risque dépassement |
| 11 | **MLOps** (E20) | Catalogue modèles, rollback, lineage |
| 12 | **Mobile PWA** (E23) | Installable, offline, push |

### 7.3 Roadmap V2 (12 mois)

| # | Épic | Livrables |
|---|---|---|
| 1 | **Analytics Avancés** (E16) | Dashboard widgets custom, layout drag & drop |
| 2 | **Labellisation** (E19) | Campagnes multi-annotateurs, active learning |
| 3 | **Multi-tenant** (5.6) | Sous-domaines, branding, isolation |
| 4 | **Open Data** (5.7) | API publique, miroirs data.gouv.ma |
| 5 | **Workflow** (5.8) | Circuit d'approbation, SLA |
| 6 | **Signature électronique** (5.10) | PAdES, HSM, horodatage |
| 7 | **Data Lineage** (E24) | Graphe, métriques qualité, alertes |
| 8 | **Notifications** (E21) | WebSocket, cloche, préférences fines |
| 9 | **Internationalisation complète** | EN, ES (multilingue) |
| 10 | **API v2 GraphQL** | Pour intégrations tierces |
| 11 | **Mobile natif** (React Native) | App iOS + Android |
| 12 | **Federated Learning** | Modèles entraînés sur plusieurs ministères sans partage de données |

---

## 8. KPIs de succès

| Catégorie | KPI | Cible V1 |
|---|---|---|
| **Adoption** | Nombre d'utilisateurs actifs / mois (MAU) | 200+ |
| **Adoption** | Nombre d'AO indexés | 50 000+ |
| **Adoption** | Nombre de recherches / jour | 1 000+ |
| **Performance** | p95 latence API | < 500 ms |
| **Performance** | p95 latence recherche FTS | < 500 ms |
| **Performance** | Disponibilité (uptime) | 99.5 % |
| **Qualité** | Précision extraction montants | > 95 % |
| **Qualité** | Précision SVM | > 88 % |
| **Qualité** | Couverture tests | > 80 % |
| **Qualité** | Bugs en production / sprint | < 5 critiques |
| **Sécurité** | Incidents sécurité | 0 |
| **Sécurité** | Score OWASP ZAP | > 80/100 |
| **UX** | Score SUS (System Usability Scale) | > 75 |
| **UX** | Taux d'adoption des alertes | > 60 % des utilisateurs |
| **UX** | NPS (Net Promoter Score) | > 40 |

---

## 9. Annexes

### 9.1 Backlog global consolidé (P0/P1/P2)

| Priorité | Item | Type | Effort | Sprint cible |
|---|---|---|---|---|
| P0 | Auth JWT + RBAC | Correction | M | S1 |
| P0 | Audit log | Correction | M | S1 |
| P0 | Aligner BDD sur `criteres.aspx` | Amélioration | M | S1 |
| P0 | Filtres recherche manquants (type avis, qualif, agrément, état) | Amélioration | M | S2 |
| P0 | Tests E2E (Cypress) | Correction | M | S1-S6 |
| P0 | CI/CD | Correction | M | S4 |
| P0 | Export CSV/Excel des résultats | Amélioration | S | S2 |
| P0 | Bouton Réinitialiser | Correction | S | S2 |
| P0 | Tri configurable | Amélioration | S | S2 |
| P0 | Docker + compose | Correction | S | S4 |
| P0 | Headers sécurité HTTP | Correction | S | S4 |
| P0 | HTTPS / TLS | Correction | S | S4 |
| P0 | SLO + monitoring | Correction | M | S4 |
| P1 | i18n FR/AR | Amélioration | M-L | S6 |
| P1 | PWA | Amélioration | M | S6 |
| P1 | Cartographie (E12) | Nouveau | L | V1 |
| P1 | Centre d'alertes (E11) | Nouveau | L | V1 |
| P1 | Comparateur (E13) | Nouveau | L | V1 |
| P1 | Dashboard Acheteur (E14) | Nouveau | L | V1 |
| P1 | Dashboard Fournisseur (E15) | Nouveau | L | V1 |
| P1 | Recherche sémantique | Nouveau | M | V1 |
| P1 | Chatbot Q&A | Nouveau | L | V1 |
| P1 | Résumés automatiques | Nouveau | M | V1 |
| P1 | Prédictif (E17) | Nouveau | L | V1 |
| P1 | Catalogue ML (E20) | Nouveau | M | V1 |
| P1 | Rapports programmés (E22) | Nouveau | M | V1 |
| P2 | Analytics Avancés (E16) | Nouveau | L | V2 |
| P2 | Labellisation (E19) | Nouveau | L | V2 |
| P2 | Multi-tenant | Nouveau | XL | V2 |
| P2 | Open Data | Nouveau | M | V2 |
| P2 | Workflow approbation | Nouveau | L | V2 |
| P2 | Signature électronique | Nouveau | M | V2 |
| P2 | Data Lineage (E24) | Nouveau | L | V2 |
| P2 | Notifications (E21) | Nouveau | M | V2 |
| P2 | Mobile natif | Nouveau | XL | V2 |
| P2 | Federated Learning | Nouveau | XL | V2+ |

### 9.2 Matrice de couverture fonctionnelle cible (V1)

| Domaine | MVP | V1 | V2 |
|---|---|---|---|
| Auth & RBAC | ✅ | ✅ | ✅ Multi-tenant |
| Recherche FTS | ✅ | ✅ Sémantique | ✅ Federated |
| Dashboard BI | 🟡 | ✅ Avancé | ✅ Custom |
| Cartographie | ❌ | ✅ | ✅ |
| Alertes | ❌ | ✅ | ✅ Cross-tenant |
| ML | 🟡 SVM + IF | ✅ Prédictif | ✅ AutoML |
| Rapports | ❌ | ✅ Programmés | ✅ Workflow |
| MLOps | 🟡 Basique | ✅ Catalogue | ✅ Auto-retrain |
| i18n | 🟡 FR/AR | ✅ + EN/ES | ✅ Toutes langues |
| Sécurité | 🟡 Basique | ✅ MFA + Audit | ✅ HSM + eIDAS |

### 9.3 Estimation budgétaire indicative

| Phase | Durée | Coût devs | Coût infra (an) |
|---|---|---|---|
| MVP | 3 mois | 1 dev senior + 1 dev junior | 1 500 € |
| V1 | 6 mois | 2 devs seniors + 1 data scientist | 5 000 € |
| V2 | 12 mois | 3 devs seniors + 1 data engineer + 1 UX | 12 000 € |

**Note** : estimation pour un contexte open source / on-premise ; à multiplier par 3-5 en mode SaaS hébergé.

### 9.4 Veille et inspiration

Pour rester à l'état de l'art, surveiller :
- [Apache Superset](https://superset.apache.org/) (open source BI)
- [Metabase](https://www.metabase.com/) (open source BI)
- [Label Studio](https://labelstud.io/) (labellisation)
- [Argilla](https://github.com/argilla-io/argilla) (labellisation pour NLP)
- [Qdrant](https://qdrant.tech/) (vectoriel)
- [LangChain](https://python.langchain.com/) (RAG)
- [Mistral AI](https://mistral.ai/) (LLM FR/AR)
- Portail National des Marchés Publics (référentiel marocain)
- Décret n° 2-22-431 (cadre réglementaire)

### 9.5 Glossaire étendu

* **PFA** : Projet de Fin d'Année
* **GED** : Gestion Électronique des Documents
* **DAO** : Dossier d'Appel d'Offres
* **CPS** : Cahier des Prescriptions Spéciales
* **RC** : Règlement de Consultation
* **DSI** : Direction des Systèmes d'Information
* **DGR** : Direction Générale des Routes
* **CFR** : Caisse pour le Financement Routier
* **DEQCA** : Document d'Engagement de Qualification et de Classification (équivalent)
* **FTS** : Full-Text Search
* **GIN** : Generalized Inverted Index
* **PWA** : Progressive Web App
* **RAG** : Retrieval-Augmented Generation
* **LLM** : Large Language Model
* **MLOps** : Machine Learning Operations
* **MLflow** : plateforme MLOps open source
* **RLS** : Row-Level Security
* **RBAC** : Role-Based Access Control
* **HNSW** : Hierarchical Navigable Small World (index vectoriel)
* **NLP** : Natural Language Processing
* **OCR** : Optical Character Recognition
* **CER / WER** : Character / Word Error Rate
* **RTL** : Right-To-Left
* **SLA / SLO** : Service Level Agreement / Objective
* **OIDC** : OpenID Connect
* **MFA** : Multi-Factor Authentication
* **HSM** : Hardware Security Module
* **eIDAS** : règlement européen sur l'identification électronique
* **PAdES** : PDF Advanced Electronic Signatures

---

> **Conclusion Fichier 2** : Le projet PFA a un socle NLP/ML solide qui peut servir de fondation à une vraie plateforme BI ministérielle. Les corrections prioritaires (auth, audit, mapping complet du formulaire source) sécurisent l'existant, tandis que les nouveaux écrans (cartographie, comparateur, dashboards dédiés, alertes) et fonctionnalités transverses (recherche sémantique, chatbot, prédictif) ouvrent la voie à une plateforme de référence. La roadmap sur 12 mois est ambitieuse mais séquencée pour livrer de la valeur à chaque sprint.
