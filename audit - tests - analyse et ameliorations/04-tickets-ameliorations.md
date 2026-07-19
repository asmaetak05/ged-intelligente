# 🎫 Fichier 4 — Backlog de tickets d'amélioration (P0 / P1 / P2)

> **Projet** : GED Intelligente — Gestion Électronique des Documents pour les marchés publics du Ministère de l'Équipement et de l'Eau du Maroc
> **Stage** : PFA (Projet de Fin d'Année)
> **Complément de** : `01-evaluation-et-tests.md`, `02-ameliorations-et-roadmap.md`, `03-cahier-de-texte-specifications.md`
> **Site de référence** : http://appels-offres.equipement.gov.ma/recherche/criteres.aspx
> **Version** : 1.0 — Backlog complet et détaillé pour la transformation du PFA en plateforme BI industrialisable

> 📋 **Convention** : Chaque ticket est numéroté, catégorisé (Backend, Frontend, ML, BDD, Sécurité, DevOps, UX, etc.), priorisé (P0/P1/P2), estimé (S/M/L/XL), et lié aux scénarios de validation (`ST-XXX-NNN`) définis dans le cahier de texte. Un estimateur (« points ») est fourni à titre indicatif en plus de la durée (S = < 1 j, M = 1-5 j, L = > 5 j).

---

## Table des matières

1. [Légende & conventions](#1-légende--conventions)
2. [Tickets BDD — Modèle de données & migrations (BDD-01..15)](#2-tickets-bdd--modèle-de-données--migrations-bdd-01-15)
3. [Tickets Backend — API FastAPI (B-01..35)](#3-tickets-backend--api-fastapi-b-01-35)
4. [Tickets Ingestion & Scraping (ING-01..12)](#4-tickets-ingestion--scraping-ing-01-12)
5. [Tickets OCR & PDF (OC-01..10)](#5-tickets-ocr--pdf-oc-01-10)
6. [Tickets NLP & Extraction (NLP-01..18)](#6-tickets-nlp--extraction-nlp-01-18)
7. [Tickets Machine Learning (ML-01..18)](#7-tickets-machine-learning-ml-01-18)
8. [Tickets Frontend / UX (UI-01..40)](#8-tickets-frontend--ux-ui-01-40)
9. [Tickets Authentification & RBAC (AU-01..15)](#9-tickets-authentification--rbac-au-01-15)
10. [Tickets Sécurité (SE-01..15)](#10-tickets-sécurité-se-01-15)
11. [Tickets DevOps / CI-CD / Observabilité (OPS-01..18)](#11-tickets-devops--ci-cd--observabilité-ops-01-18)
12. [Tickets Tests & Qualité (T-01..15)](#12-tickets-tests--qualité-t-01-15)
13. [Tickets Documentation (DOC-01..10)](#13-tickets-documentation-doc-01-10)
14. [Tickets Nouveaux écrans (E-10..E-24)](#14-tickets-nouveaux-écrans-e-10-e-24)
15. [Tickets Fonctionnalités transverses (F-01..10)](#15-tickets-fonctionnalités-transverses-f-01-10)
16. [Synthèse & Roadmap](#16-synthèse--roadmap)

---

## 1. Légende & conventions

| Code | Catégorie | Préfixe tickets |
|---|---|---|
| 🔴 **P0** | Bloquant — à faire avant production | — |
| 🟠 **P1** | Important — à faire avant soutenance | — |
| 🟡 **P2** | Amélioration — post-soutenance | — |

| Effort | Durée | Points (Fibonacci) |
|---|---|---|
| **S** (Small) | < 1 jour | 2 |
| **M** (Medium) | 1 à 5 jours | 5 |
| **L** (Large) | > 5 jours | 8 ou 13 |
| **XL** (Extra-Large) | > 2 semaines | 21 |

| Statut | Signification |
|---|---|
| `BACKLOG` | Ticket créé, pas encore démarré |
| `TODO` | Prêt à faire |
| `IN_PROGRESS` | En cours |
| `REVIEW` | En revue de code |
| `DONE` | Terminé et déployé |
| `BLOCKED` | Bloqué (préciser la cause) |

| Sprint cible | Période |
|---|---|
| S1 | 2 semaines — Durcir l'existant |
| S2 | 2 semaines — Compléter la recherche |
| S3 | 2 semaines — Enrichir le Dashboard |
| S4 | 2 semaines — Ops & Qualité |
| S5 | 2 semaines — ML & Données |
| S6 | 2 semaines — i18n & PWA |
| V1 | 6 mois post-soutenance |
| V2 | 12 mois post-soutenance |

---

## 2. Tickets BDD — Modèle de données & migrations (BDD-01..15)

### BDD-01 — Aligner le modèle de données sur le formulaire `criteres.aspx` 🔴
| Champ | Détail |
|---|---|
| **Priorité** | 🔴 P0 |
| **Effort** | L (5 j) |
| **Sprint cible** | S1 |
| **Catégorie** | Backend / BDD / Migration |
| **Composant** | `backend/models.py`, `alembic/versions/` |
| **Scénarios liés** | ST-NL-009, ST-NL-010, ST-NL-012, ST-FT-008, ST-FT-011, ST-FT-013, ST-FT-015, ST-FT-016, ST-FT-018 |
| **Description** | Le modèle `Marche` actuel couvre ~57 % des champs du formulaire source. Ajouter : `typeavis_id` (FK), `procedure_id` (FK), `etat_id` (FK), `date_ouverture_plis` (DateTime), `langue` (String(5)), `province` (String(100)), `direction_id` (FK), `modele_reference` (String(50)), `low_quality` (Boolean). |
| **Travail à faire** | 1. Créer tables de référence : `type_avis`, `type_procedure`, `etat_avis`, `direction`, `province`, `source`, `qualification`.<br>2. Ajouter colonnes à `marches` via migration Alembic.<br>3. Ajouter contraintes (`CHECK` langue ∈ {FR, AR, BI}, `CHECK` etat ∈ {En cours, Clôturé, …}).<br>4. Ajouter index sur `typeavis_id`, `etat_id`, `date_ouverture_plis`.<br>5. Seeder les valeurs de référence (scripts `scripts/seed_ref_tables.py`).<br>6. Backfill des anciens marchés : best-effort sur `typeavis` via NLP. |
| **Critère d'acceptation** | Migration `alembic upgrade head` OK, 13/23 champs source désormais en BDD, seeders exécutables, `pytest tests/test_bdd_migrations.py` PASS. |
| **Risques** | Migration destructive sur données existantes — utiliser `op.alter_column` avec default et backfill SQL progressif. |

### BDD-02 — Table `direction` (hiérarchie Maître d'ouvrage → Direction → Service) 🔴
| Champ | Détail |
|---|---|
| **Priorité** | 🔴 P0 |
| **Effort** | M (2 j) |
| **Sprint cible** | S1 |
| **Catégorie** | BDD |
| **Composant** | `backend/models.py` |
| **Scénarios liés** | ST-FT-008 (filtre maître d'ouvrage hiérarchique) |
| **Description** | Permettre une hiérarchie Direction → Service dans les acheteurs publics. |
| **Travail à faire** | 1. Table `direction(id, name, parent_id, type)` (auto-référencée).<br>2. Colonne `marches.direction_id` (FK nullable).<br>3. Seeder avec l'arborescence officielle du Ministère (DGR, DRE, …).<br>4. Endpoint `GET /api/v1/ref/directions?type=...`. |
| **Critère d'acceptation** | Seeder exécutable, jointure `marches → direction` fonctionnelle. |

### BDD-03 — Tables `qualification` et `marche_qualification` (N:N) 🔴
| Champ | Détail |
|---|---|
| **Priorité** | 🔴 P0 |
| **Effort** | M (2 j) |
| **Sprint cible** | S1 |
| **Catégorie** | BDD |
| **Composant** | `backend/models.py` |
| **Scénarios liés** | ST-NL-010, ST-FT-013 |
| **Description** | Modéliser les qualifications et agréments comme entités propres (au lieu de listes JSON). |
| **Travail à faire** | 1. Table `qualification(id, code, label, classe, categorie)` (ex. Q1-Q6 BTP).<br>2. Table `agrement(id, code, label, type)` (ex. Routes, Assainissement).<br>3. Tables d'association `marche_qualification(marche_id, qualification_id)` et `marche_agrement(marche_id, agrement_id)`.<br>4. Migration Alembic.<br>5. Seeder avec référentiel BTP marocain officiel. |
| **Critère d'acceptation** | Jointures fonctionnelles, données seed chargées. |

### BDD-04 — Table `source` pour multi-portails 🟠
| Champ | Détail |
|---|---|
| **Priorité** | 🟠 P1 |
| **Effort** | S (1 j) |
| **Sprint cible** | V1 |
| **Catégorie** | BDD |
| **Composant** | `backend/models.py` |
| **Scénarios liés** | ST-API-008, scénario I-02 (multi-sources) |
| **Description** | Préparer le terrain pour le multi-sources (marchespublics.gov.ma, autres ministères). |
| **Travail à faire** | 1. Table `source(id, name, base_url, scraper_class, schedule_cron, selectors_json)`.<br>2. Colonne `marches.source_id` (FK).<br>3. Seeder avec la source actuelle « Ministère Équipement ». |
| **Critère d'acceptation** | Inscription d'une nouvelle source via UI possible (côté admin). |

### BDD-05 — Table `ville` (géographie normalisée) 🟠
| Champ | Détail |
|---|---|
| **Priorité** | 🟠 P1 |
| **Effort** | M (2 j) |
| **Sprint cible** | S1 |
| **Catégorie** | BDD |
| **Composant** | `backend/models.py`, `nlp/villes_maroc.py` |
| **Scénarios liés** | ST-NL-004, ST-FT-008 |
| **Description** | Remplacer la liste Python `VILLES_MAROC` par une table SQL avec région et province. |
| **Travail à faire** | 1. Table `ville(id, name, province, region, lat, lon)` (charger GeoJSON officiel).<br>2. Colonne `marches.ville_id` (FK) en plus de `ville_execution` (legacy).<br>3. Endpoint `GET /api/v1/ref/villes?region=...&q=...`.<br>4. Migration des données existantes (lookup par `ville_execution`). |
| **Critère d'acceptation** | 1 500+ villes chargées, autocomplétion du filtre « Ville » fonctionnelle. |

### BDD-06 — Colonnes `created_at` / `updated_at` / `deleted_at` (audit) 🔴
| Champ | Détail |
|---|---|
| **Priorité** | 🔴 P0 |
| **Effort** | M (2 j) |
| **Sprint cible** | S1 |
| **Catégorie** | BDD |
| **Composant** | `backend/models.py` |
| **Scénarios liés** | ST-API-005, AU-11 (audit) |
| **Description** | Toutes les tables métier doivent avoir `created_at`, `updated_at`, `deleted_at` (soft delete). |
| **Travail à faire** | 1. Mixin SQLAlchemy `TimestampMixin`.<br>2. Appliquer à `Document`, `Marche`, `OcrLog`, `MlInsight`, `ExtractionNlp`.<br>3. Migration Alembic pour ajouter les colonnes.<br>4. Mettre à jour `MarcheRepository.list` pour filtrer `deleted_at IS NULL` par défaut. |
| **Critère de succès** | Soft delete fonctionnel, requêtes excluent les lignes supprimées. |

### BDD-07 — Contrainte d'unicité stricte sur `numero_appel_offre` 🔴
| Champ | Détail |
|---|---|
| **Priorité** | 🔴 P0 |
| **Effort** | S (0.5 j) |
| **Sprint cible** | S1 |
| **Catégorie** | BDD |
| **Composant** | `backend/models.py:Marche` |
| **Scénarios liés** | ST-IN-008, ST-DQ-002 |
| **Description** | `numero_appel_offre` doit être unique, déjà déclaré en `unique=True` mais sans gestion fine des conflits en cas de normalisation Unicode. |
| **Travail à faire** | 1. Ajouter contrainte `UNIQUE(numero_appel_offre)` au niveau SQL (idempotent).<br>2. Ajouter une `CHECK` `length(numero_appel_offre) > 0`.<br>3. Tests : 2 DAO avec même référence → 2e insertion `IntegrityError`.<br>4. Normaliser la valeur (strip + uppercase + NFKC Unicode). |
| **Critère de succès** | `pytest tests/test_dq_unique.py` PASS. |

### BDD-08 — Index GIN PostgreSQL + `tsvector` pour FTS 🔴
| Champ | Détail |
|---|---|
| **Priorité** | 🔴 P0 |
| **Effort** | M (3 j) |
| **Sprint cible** | S1 |
| **Catégorie** | BDD / Performance |
| **Composant** | `alembic/versions/`, `scripts/setup_postgres_triggers.sql` |
| **Scénarios liés** | ST-FT-001..032, ST-PE-003 |
| **Description** | Activer le FTS natif PostgreSQL : colonne `tsv_search` calculée + index GIN + trigger de mise à jour. |
| **Travail à faire** | 1. Migration conditionnelle au dialecte PostgreSQL (déjà amorcée dans `setup_postgres_triggers.sql`).<br>2. Trigger `BEFORE INSERT OR UPDATE` calculant `tsv_search = to_tsvector('french', titre_projet \|\| ' ' \|\| COALESCE(tsv_search,''))`.<br>3. Index GIN `CREATE INDEX idx_marches_tsv_gin ON marches USING GIN(tsv_search)`.<br>4. Refactor `MarcheRepository.search_fts` pour utiliser `to_tsquery` sur PostgreSQL, fallback LIKE sur SQLite (dev).<br>5. Vérifier `EXPLAIN ANALYZE` : Seq Scan disparu, Bitmap Index Scan présent. |
| **Critère de succès** | p95 < 100 ms sur 10 000 docs (vs ~500 ms en LIKE). |

### BDD-09 — Stockage des PDF sources (versioning, hash) 🔴
| Champ | Détail |
|---|---|
| **Priorité** | 🔴 P0 |
| **Effort** | M (3 j) |
| **Sprint cible** | S1 |
| **Catégorie** | BDD / Stockage |
| **Composant** | `backend/models.py:Document`, MinIO |
| **Scénarios liés** | ST-IN-006, ST-DQ-001 |
| **Description** | Stocker les PDF/ZIP avec hash SHA-256 pour intégrité + déduplication. |
| **Travail à faire** | 1. Colonne `documents.checksum_sha256` (String(64), indexé).<br>2. Colonne `documents.storage_uri` (S3 URI).<br>3. Service de stockage MinIO (`ingestion/storage.py`).<br>4. Calcul du hash à l'upload, vérification à chaque re-upload.<br>5. Tests d'intégrité. |
| **Critère de succès** | Hash unique par fichier, déduplication inter-scraping effective. |

### BDD-10 — Table `user`, `role`, `permission` 🔴
| Champ | Détail |
|---|---|
| **Priorité** | 🔴 P0 |
| **Effort** | M (3 j) |
| **Sprint cible** | S1 |
| **Catégorie** | BDD / Auth |
| **Composant** | `backend/models.py` |
| **Scénarios liés** | ST-AU-008..010 |
| **Description** | Implémenter RBAC (Role-Based Access Control) complet. |
| **Travail à faire** | 1. Table `user(id, email UNIQUE, hashed_password, full_name, mfa_secret, is_active, last_login_at)`.<br>2. Table `role(id, name, description)` (seed : `reader`, `analyst`, `admin` + custom).<br>3. Table `permission(id, code, description)` (ex. `scraper:run`, `ml:retrain`, `user:manage`).<br>4. Tables d'association `user_role` et `role_permission`.<br>5. Colonne `marches.created_by_user_id` (FK) pour traçabilité.<br>6. Seeder avec 1 admin par défaut (mot de passe changé au 1er login). |
| **Critère de succès** | Tests AU-008/009/010 PASS. |

### BDD-11 — Table `audit_event` (Append-Only) 🔴
| Champ | Détail |
|---|---|
| **Priorité** | 🔴 P0 |
| **Effort** | M (2 j) |
| **Sprint cible** | S1 |
| **Catégorie** | BDD / Audit |
| **Composant** | `backend/models.py` |
| **Scénarios liés** | ST-AU-011, ST-E2E-001 |
| **Description** | Tracer toutes les actions sensibles. |
| **Travail à faire** | 1. Table `audit_event(id, user_id, action, resource_type, resource_id, ip_address, user_agent, request_id, payload_json, created_at)`.<br>2. Trigger SQL `BEFORE UPDATE OR DELETE ON audit_event → RAISE EXCEPTION` (Append-Only).<br>3. Service `audit/log.py` avec helpers `log_event(db, user, action, resource)`.<br>4. Middleware FastAPI qui injecte `request_id` (UUID v4). |
| **Critère de succès** | Tentative d'UPDATE/DELETE rejetée par la BDD. |

### BDD-12 — Table `saved_search` 🟡
| Champ | Détail |
|---|---|
| **Priorité** | 🟡 P2 |
| **Effort** | S (1 j) |
| **Sprint cible** | V1 |
| **Scénarios liés** | ST-FT-027 |
| **Description** | Permettre à un utilisateur de sauvegarder une recherche. |
| **Travail** | Table `saved_search(id, user_id, name, filters_json, created_at)`, endpoint `GET/POST/DELETE /api/v1/saved-searches`. |

### BDD-13 — Table `alert` et `alert_delivery` 🟠
| Champ | Détail |
|---|---|
| **Priorité** | 🟠 P1 |
| **Effort** | M (2 j) |
| **Sprint cible** | V1 |
| **Scénarios liés** | Scénario E11, ST-E2E-011 |
| **Description** | Système d'alertes personnalisées. |
| **Travail** | Tables `alert(id, user_id, name, filters_json, frequency, channels_json, is_active)`, `alert_delivery(id, alert_id, triggered_at, results_count, sent_at, channel)`, worker Dramatiq toutes les 5 min. |

### BDD-14 — Partitionnement temporel sur `marches` et `audit_event` 🟡
| Champ | Détail |
|---|---|
| **Priorité** | 🟡 P2 |
| **Effort** | L (5 j) |
| **Sprint cible** | V1 |
| **Description** | Partitionner par année pour scaler à 1M+ documents. |
| **Travail** | `CREATE TABLE marches_2024 PARTITION OF marches FOR VALUES FROM ('2024-01-01') TO ('2025-01-01')` ; idem pour `audit_event`. |

### BDD-15 — Chiffrement at-rest (champs sensibles) 🟡
| Champ | Détail |
|---|---|
| **Priorité** | 🟡 P2 |
| **Effort** | M (3 j) |
| **Sprint cible** | V1 |
| **Scénarios liés** | ST-SE-012 |
| **Description** | Chiffrer les colonnes sensibles (caution provisoire, hashed_password) côté BDD. |
| **Travail** | Utiliser `pgcrypto` ou KMS AWS. |

---

## 3. Tickets Backend — API FastAPI (B-01..35)

### B-01 — Authentification JWT (login, refresh, logout) 🔴
| Champ | Détail |
|---|---|
| **Priorité** | 🔴 P0 |
| **Effort** | M (3 j) |
| **Sprint cible** | S1 |
| **Composant** | `backend/main.py`, `backend/auth.py` (à créer) |
| **Scénarios liés** | ST-AU-001..003 |
| **Description** | Aucun système d'authentification actuellement — **bloquant**. |
| **Travail** | 1. `auth/jwt.py` (création/vérification de tokens via `python-jose`).<br>2. `auth/password.py` (`passlib[bcrypt]`).<br>3. `POST /api/v1/auth/login` (retourne access + refresh).<br>4. `POST /api/v1/auth/refresh`.<br>5. `POST /api/v1/auth/logout` (blacklist token).<br>6. Middleware `Depends(get_current_user)`.<br>7. Cookie httpOnly + SameSite=Strict en plus du header Bearer. |
| **Critère de succès** | Tests AU-001..003 PASS, JWT signé avec RS256. |

### B-02 — RBAC (3 rôles : reader / analyst / admin) 🔴
| Champ | Détail |
|---|---|
| **Priorité** | 🔴 P0 |
| **Effort** | M (3 j) |
| **Sprint cible** | S1 |
| **Composant** | `backend/auth/rbac.py` |
| **Scénarios liés** | ST-AU-008..010 |
| **Description** | Distinguer les permissions selon le rôle. |
| **Travail** | 1. Décorateur `@require_role("admin")` ou `@require_permission("scraper:run")`.<br>2. Mapping rôle × ressource × action.<br>3. Tests par rôle.<br>4. UI : masquer les boutons non autorisés. |
| **Critère de succès** | Tests AU-008/009/010 PASS. |

### B-03 — Rate limiting (slowapi) 🟠
| Champ | Détail |
|---|---|
| **Priorité** | 🟠 P1 |
| **Effort** | S (0.5 j) |
| **Sprint cible** | S1 |
| **Composant** | `backend/main.py` |
| **Scénarios liés** | ST-SE-009, ST-API-015 |
| **Travail** | `from slowapi import Limiter` ; `limiter = Limiter(key_func=get_remote_address, default_limits=["100/minute"])` ; `@limiter.limit("5/minute")` sur `/auth/login`. |

### B-04 — Handler global d'exceptions (RFC 7807) 🟠
| Champ | Détail |
|---|---|
| **Priorité** | 🟠 P1 |
| **Effort** | S (1 j) |
| **Sprint cible** | S1 |
| **Composant** | `backend/main.py` |
| **Scénarios liés** | ST-API-017 |
| **Description** | Remplacer les `raise HTTPException(500)` par un format `application/problem+json` uniforme. |
| **Travail** | `@app.exception_handler(Exception)` qui retourne `{"type": "...", "title": "...", "status": ..., "detail": ..., "instance": request_id}`. |

### B-05 — Logs structurés (structlog) 🟠
| Champ | Détail |
|---|---|
| **Priorité** | 🟠 P1 |
| **Effort** | S (1 j) |
| **Sprint cible** | S1 |
| **Composant** | `backend/logging_config.py` |
| **Scénarios liés** | ST-OPS-004, ST-IN-013 |
| **Description** | Remplacer tous les `print()` par `logger.info(event="...", request_id=...)`. |
| **Travail** | 1. `structlog.configure(processors=[add_log_level, JSONRenderer()])`.<br>2. Middleware qui injecte `request_id` dans le `contextvars`.<br>3. Tests : `assert '"event": "document_uploaded"' in log_output`. |

### B-06 — Versionner les schémas Pydantic 🟠
| Champ | Détail |
|---|---|
| **Priorité** | 🟠 P1 |
| **Effort** | S (1 j) |
| **Sprint cible** | S1 |
| **Composant** | `backend/schemas/v1/` |
| **Travail** | Créer `schemas/v1/marche.py`, `schemas/v2/...` ; import via `from backend.schemas.v1 import MarcheCreate`. |

### B-07 — File de tâches persistante (Celery + Redis) 🟠
| Champ | Détail |
|---|---|
| **Priorité** | 🟠 P1 |
| **Effort** | L (5 j) |
| **Sprint cible** | S1 |
| **Composant** | `backend/celery_app.py` |
| **Scénarios liés** | ST-IN-005, ST-ML-005, ST-API-008/009 |
| **Description** | Remplacer `BackgroundTasks` (non persistant) par Celery avec Redis. |
| **Travail** | 1. `celery_app = Celery("ged", broker="redis://localhost:6379/0")`.<br>2. Tâches : `process_document_async`, `retrain_models`, `compute_embeddings`.<br>3. Suivi via `GET /api/v1/jobs/{id}` (statut Celery).<br>4. Tests : `assert task.status == "SUCCESS"`. |

### B-08 — CORS strict (whitelist) 🟠
| Champ | Détail |
|---|---|
| **Priorité** | 🟠 P1 |
| **Effort** | S (0.5 j) |
| **Sprint cible** | S1 |
| **Composant** | `backend/main.py:55` |
| **Scénarios liés** | ST-SE-008 |
| **Description** | ⚠️ **Vulnérabilité actuelle** : `allow_origins=["*"]` est non-conforme. |
| **Travail** | `allow_origins=settings.CORS_ALLOWED_ORIGINS` (variable d'env : `https://app.ged-bi.ma,http://localhost:5173`). |

### B-09 — Cache Redis (dashboard, search) 🟠
| Champ | Détail |
|---|---|
| **Priorité** | 🟠 P1 |
| **Effort** | M (2 j) |
| **Sprint cible** | S1 |
| **Composant** | `backend/cache.py` |
| **Scénarios liés** | ST-DB-012, ST-PE-003 |
| **Travail** | 1. `@cache.cached(timeout=30)` sur `/api/v1/analytics/kpis`.<br>2. Invalidation sur `POST /api/v1/ged/appels-offres` (cache bust).<br>3. Tests : 2e appel < 50 ms (depuis cache). |

### B-10 — Health check profond 🟠
| Champ | Détail |
|---|---|
| **Priorité** | 🟠 P1 |
| **Effort** | S (0.5 j) |
| **Sprint cible** | S1 |
| **Composant** | `backend/main.py:601` |
| **Scénarios liés** | ST-OPS-011 |
| **Travail** | `/api/v1/system/health` qui teste DB (`SELECT 1`) + Redis (`PING`) + MinIO (`stat` sur bucket). |

### B-11..B-35 — Autres tickets Backend
Liste condensée (détails disponibles sur demande) :

| ID | Titre | Pri. | Effort | Sprint |
|---|---|---|---|---|
| B-11 | Endpoint `GET /api/v1/system/schema` (déjà partiel) | 🟡 | S | S1 |
| B-12 | Endpoint pagination `{items, total, page, size, took_ms}` (déjà partiel) | 🟢 | — | — |
| B-13 | Préfixe `/api/v1/` partout (déjà fait) | 🟢 | — | — |
| B-14 | Standardiser `__tablename__` explicite | 🟠 | S | S1 |
| B-15 | Champ `request_id` middleware UUID | 🟠 | S | S1 |
| B-16 | OpenTelemetry auto-instrumentation | 🟡 | M | V1 |
| B-17 | `factory-boy` + `pytest-postgresql` | 🟠 | S | S1 |
| B-18 | Documentation OpenAPI enrichie | 🟡 | M | S4 |
| B-19 | Endpoint `GET /api/v1/analytics/dashboard` unifié | 🟠 | S | S3 |
| B-20 | Endpoint `POST /api/v1/ged/appels-offres/export?format=csv` | 🔴 | M | S2 |
| B-21 | Endpoint `GET /api/v1/ged/appels-offres/export?format=xlsx` | 🟠 | M | S2 |
| B-22 | Endpoint `POST /api/v1/auth/forgot-password` | 🟠 | S | S1 |
| B-23 | Endpoint `POST /api/v1/auth/reset-password` | 🟠 | S | S1 |
| B-24 | Endpoint `POST /api/v1/auth/change-password` | 🟠 | S | S1 |
| B-25 | Endpoint `GET /api/v1/users` (admin) | 🟠 | M | S1 |
| B-26 | Endpoint `POST /api/v1/users` (admin) | 🟠 | S | S1 |
| B-27 | Endpoint `DELETE /api/v1/users/{id}` (admin) | 🟠 | S | S1 |
| B-28 | Endpoint `GET /api/v1/audit/events` | 🟡 | M | S1 |
| B-29 | Endpoint `GET /api/v1/ml/metrics` | 🟠 | S | S5 |
| B-30 | Endpoint `GET /api/v1/geo/aggregates?level=region` | 🟡 | L | V1 |
| B-31 | Endpoint `GET /api/v1/compare?ids=1,2,3` | 🟡 | M | V1 |
| B-32 | Endpoint `GET /api/v1/alerts/feed` (WebSocket) | 🟡 | M | V1 |
| B-33 | Endpoint `POST /api/v1/webhooks` | 🟡 | S | V1 |
| B-34 | Endpoint `POST /api/v1/scraper/schedule` | 🟠 | M | S1 |
| B-35 | Endpoint `GET /api/v1/jobs/{id}` (suivi des tâches) | 🟠 | S | S1 |

---

## 4. Tickets Ingestion & Scraping (ING-01..12)

### ING-01 — Pool Playwright + parallélisation contrôlée 🟠
| Champ | Détail |
|---|---|
| **Priorité** | 🟠 P1 |
| **Effort** | M (3 j) |
| **Sprint cible** | S1 |
| **Composant** | `ingestion/playwright_pool.py` |
| **Scénarios liés** | ST-IN-015, ST-PE-001, ST-PE-002 |
| **Description** | Remplacer le mode mono-thread par un pool de workers Playwright. |
| **Travail** | 1. `asyncio.Queue` partagée entre N workers.<br>2. `async with async_playwright()` par worker.<br>3. `asyncio.gather(*tasks)`.<br>4. Lock applicatif (`asyncio.Lock`) sur l'écriture BDD.<br>5. Tests de concurrence. |

### ING-02 — Découplage des sélecteurs (config externe) 🔴
| Champ | Détail |
|---|---|
| **Priorité** | 🔴 P0 |
| **Effort** | M (2 j) |
| **Sprint cible** | S1 |
| **Composant** | `ingestion/selectors.yaml` |
| **Scénarios liés** | ST-IN-009 |
| **Description** | Les sélecteurs sont hard-codés dans le code Python — toute modification HTML du site oblige à modifier le code. |
| **Travail** | 1. Fichier `selectors.yaml` avec clés : `search_input`, `result_table`, `pagination_next`, `download_button`.<br>2. `SelectorLocator` qui charge le YAML et applique.<br>3. Test snapshot HTML (cf. ST-IN-009). |

### ING-03 — Reprise sur erreur (checkpoint + offset) 🔴
| Champ | Détail |
|---|---|
| **Priorité** | 🔴 P0 |
| **Effort** | M (3 j) |
| **Sprint cible** | S1 |
| **Composant** | `ingestion/scraper.py` |
| **Scénarios liés** | ST-IN-005, ST-IN-010 |
| **Description** | Aucune reprise actuelle après crash — les longs scrapings doivent tout recommencer. |
| **Travail** | 1. Sauvegarder `(date, page, doc_id)` dans un fichier `checkpoint.json` ou table `scraper_state`.<br>2. Reprise au démarrage si `checkpoint.json` existe.<br>3. Tests d'injection de crash à mi-parcours. |

### ING-04 — Idempotence et déduplication par hash SHA-256 🔴
| Champ | Détail |
|---|---|
| **Priorité** | 🔴 P0 |
| **Effort** | S (1 j) |
| **Sprint cible** | S1 |
| **Composant** | `ingestion/extractor.py` |
| **Scénarios liés** | ST-IN-008 |
| **Travail** | Calculer `sha256(zip_bytes)` à l'upload, vérifier unicité en BDD avant insertion. |

### ING-05 — Watermark temporel `last_scrape_at` 🟠
| Champ | Détail |
|---|---|
| **Priorité** | 🟠 P1 |
| **Effort** | S (0.5 j) |
| **Sprint cible** | S1 |
| **Composant** | `backend/models.py:Source` |
| **Scénarios liés** | Scénario I-01 (scraping incrémental) |
| **Travail** | Colonne `sources.last_scrape_at`, incrémentée à chaque run réussi ; endpoint `GET /api/v1/scraper/jobs` qui liste l'historique. |

### ING-06 — Endpoint `POST /api/v1/scraper/run` (asynchrone) 🟠
| Champ | Détail |
|---|---|
| **Priorité** | 🟠 P1 |
| **Effort** | M (2 j) |
| **Sprint cible** | S1 |
| **Composant** | `backend/main.py` |
| **Scénarios liés** | ST-API-009, ST-API-010 |
| **Description** | Actuellement, le lancement se fait via WebSocket — il faut un endpoint REST asynchrone. |
| **Travail** | 1. `@app.post("/api/v1/scraper/run")` qui crée un `ScraperJob` et dispatch Celery.<br>2. `GET /api/v1/scraper/jobs/{id}` retourne statut.<br>3. UI : bouton « Lancer » affiche le job ID et écoute les updates. |

### ING-07 — Multi-sources (table `source`) 🟡
| Champ | Détail |
|---|---|
| **Priorité** | 🟡 P2 |
| **Effort** | L (5 j) |
| **Sprint cible** | V1 |
| **Composant** | `ingestion/registry.py` |
| **Scénarios liés** | Scénario I-02 |
| **Travail** | 1. Classe abstraite `Scraper` ; sous-classes `MinistereEquipementScraper`, `MarchesPublicsScraper`.<br>2. Registry des sources.<br>3. UI PipelineAdmin : ajouter/éditer une source. |

### ING-08 — Mode prévisualisation (dry-run) 🟡
| Champ | Détail |
|---|---|
| **Priorité** | 🟡 P2 |
| **Effort** | S (1 j) |
| **Sprint cible** | V1 |
| **Composant** | `ingestion/scraper.py` |
| **Travail** | `?dry_run=true` : le scraper récupère les URLs sans télécharger ni écrire en BDD ; retourne la liste. |

### ING-09 — Webhooks sortants (Slack, ERP) 🟡
| Champ | Détail |
|---|---|
| **Priorité** | 🟡 P2 |
| **Effort** | M (2 j) |
| **Sprint cible** | V1 |
| **Composant** | `backend/webhooks.py` |
| **Travail** | 1. Table `webhook(id, url, secret, events_json)`.<br>2. À chaque `marches.created`, POST sur les webhooks abonnés.<br>3. Retry exponentiel 3× en cas d'échec. |

### ING-10 — Détection de changement (versioning ZIP) 🟡
| Champ | Détail |
|---|---|
| **Priorité** | 🟡 P2 |
| **Effort** | M (2 j) |
| **Sprint cible** | V1 |
| **Travail** | Table `version_history(id, marche_id, checksum, file_uri, created_at)` ; détection d'un ZIP déjà connu avec checksum différent → flag `rectificatif`. |

### ING-11 — Tests d'intégration avec snapshot HTML 🟠
| Champ | Détail |
|---|---|
| **Priorité** | 🟠 P1 |
| **Effort** | M (2 j) |
| **Sprint cible** | S1 |
| **Composant** | `tests/fixtures/portal_snapshot.html`, `tests/test_scraper_snapshot.py` |
| **Scénarios liés** | ST-IN-009 |
| **Travail** | Charger un snapshot HTML réel (collecté manuellement) ; exécuter le scraper en mode `offline=True` ; vérifier que les champs-clés sont extraits. |

### ING-12 — Planificateur de scraping (cron intégré) 🟠
| Champ | Détail |
|---|---|
| **Priorité** | 🟠 P1 |
| **Effort** | M (2 j) |
| **Sprint cible** | S1 |
| **Composant** | `backend/scheduler.py` |
| **Scénarios liés** | Scénario I-01 |
| **Travail** | 1. `APScheduler` ou Celery beat.<br>2. Cron quotidien à 02h00 : `scraper.run(last_scrape_at, today)`.<br>3. UI : cron builder visuel (optionnel, V1). |

---

## 5. Tickets OCR & PDF (OC-01..10)

### OC-01 — Cache OCR (clé = SHA-256 du PDF) 🟠
| Champ | Détail |
|---|---|
| **Priorité** | 🟠 P1 |
| **Effort** | S (1 j) |
| **Sprint cible** | S1 |
| **Composant** | `ocr/cache.py` |
| **Scénarios liés** | Scénario O-01 |
| **Description** | Si un même PDF est ré-uploadé, l'OCR est refait — gain de temps possible. |
| **Travail** | Clé = `sha256(pdf_bytes)` ; vérifier `OcrLog.raw_text_extracted IS NOT NULL` avant de relancer Tesseract. |

### OC-02 — OCR multi-moteurs (Tesseract + EasyOCR fallback) 🟠
| Champ | Détail |
|---|---|
| **Priorité** | 🟠 P1 |
| **Effort** | L (5 j) |
| **Sprint cible** | V1 |
| **Composant** | `ocr/multi_engine.py` |
| **Scénarios liés** | ST-OC-003, ST-OC-004 |
| **Description** | Améliorer la qualité OCR arabe (Tesseract sous-performe). |
| **Travail** | 1. Voter entre Tesseract FR, Tesseract AR, EasyOCR.<br>2. Choisir la sortie avec confiance max.<br>3. Métriques CER/WER stockées. |

### OC-03 — Métriques qualité CER/WER par page 🟡
| Champ | Détail |
|---|---|
| **Priorité** | 🟡 P2 |
| **Effort** | M (2 j) |
| **Sprint cible** | S5 |
| **Composant** | `ocr/metrics.py` |
| **Scénarios liés** | ST-OC-014 |
| **Travail** | Calculer `cer = jiwer.cer(reference, hypothesis)` sur un échantillon annoté ; agréger par document. |

### OC-04 — Reprise OCR après crash (checkpoint par page) 🔴
| Champ | Détail |
|---|---|
| **Priorité** | 🔴 P0 |
| **Effort** | M (2 j) |
| **Sprint cible** | S1 |
| **Composant** | `ocr/checkpoint.py` |
| **Scénarios liés** | ST-OC-010 |
| **Travail** | Sauvegarder `documents.ocr_progress` (int = page courante) ; reprise au démarrage. |

### OC-05 — Prétraitement avancé (deskew, denoise) 🟠
| Champ | Détail |
|---|---|
| **Priorité** | 🟠 P1 |
| **Effort** | M (2 j) |
| **Sprint cible** | S5 |
| **Composant** | `ocr/preprocess.py` |
| **Scénarios liés** | ST-OC-007 |
| **Travail** | Bibliothèque `opencv-python` ; algorithme de Hough transform pour deskew ; Gaussian blur + seuillage adaptatif. |

### OC-06 — OCR bilingue FR/AR par page 🟠
| Champ | Détail |
|---|---|
| **Priorité** | 🟠 P1 |
| **Effort** | M (2 j) |
| **Sprint cible** | S5 |
| **Composant** | `ocr/multilang.py` |
| **Scénarios liés** | ST-OC-005, ST-OC-015 |
| **Travail** | 1. Tesseract `lang='fra+ara'` (les deux modèles combinés).<br>2. Détection automatique de la langue par page (`langdetect`).<br>3. Stockage `OcrLog.detected_languages`. |

### OC-07 — Support TIFF / JPEG / PNG scannés 🟡
| Champ | Détail |
|---|---|
| **Priorité** | 🟡 P2 |
| **Effort** | S (1 j) |
| **Sprint cible** | V1 |
| **Composant** | `ocr/image_input.py` |
| **Scénarios liés** | Scénario O-04 |
| **Travail** | Uniformiser l'entrée : image ou PDF → `np.array` → prétraitement → Tesseract. |

### OC-08 — Streaming PyMuPDF pour PDF > 200 pages 🟠
| Champ | Détail |
|---|---|
| **Priorité** | 🟠 P1 |
| **Effort** | M (2 j) |
| **Sprint cible** | S5 |
| **Composant** | `ocr/stream_extract.py` |
| **Scénarios liés** | ST-OC-009 |
| **Travail** | `page = doc.load_page(i)` au lieu de `text = doc[i].get_text()` ; libérer la mémoire entre pages. |

### OC-09 — Préservation de la structure (titres, tableaux) 🟡
| Champ | Détail |
|---|---|
| **Priorité** | 🟡 P2 |
| **Effort** | L (5 j) |
| **Sprint cible** | V1 |
| **Composant** | `ocr/structured.py` |
| **Scénarios liés** | ST-OC-012, Scénario O-02 |
| **Travail** | Sortie JSON `[{page, blocks: [{type, text, bbox, font_size}]}]` ; `pymupdf.get_text("dict")`. |

### OC-10 — Gestion des PDF chiffrés 🟠
| Champ | Détail |
|---|---|
| **Priorité** | 🟠 P1 |
| **Effort** | S (0.5 j) |
| **Sprint cible** | S5 |
| **Composant** | `ocr/security.py` |
| **Scénarios liés** | ST-OC-013 |
| **Travail** | `if doc.is_encrypted: raise EncryptedPdfError()` ; log de l'incident dans `audit_event`. |

---

## 6. Tickets NLP & Extraction (NLP-01..18)

### NLP-01 — Extraction du type d'avis (8 valeurs) 🔴
| Champ | Détail |
|---|---|
| **Priorité** | 🔴 P0 |
| **Effort** | M (3 j) |
| **Sprint cible** | S1 |
| **Composant** | `nlp/extract_typeavis.py` |
| **Scénarios liés** | ST-NL-009, ST-FT-015 |
| **Description** | Type d'avis (Ouvert, Restreint, Simplifié, etc.) n'est pas extrait. |
| **Travail** | 1. Patterns regex : `r"appel d'offres?\s+(ouvert|restreint|simplifié)"` etc.<br>2. Lookup table des 8 valeurs officielles.<br>3. Validation par `marches.typeavis_id` (FK).<br>4. Tests sur 20 DAO. |

### NLP-02 — Extraction des qualifications (Q1-Q6 BTP) 🟠
| Champ | Détail |
|---|---|
| **Priorité** | 🟠 P1 |
| **Effort** | M (2 j) |
| **Sprint cible** | S5 |
| **Composant** | `nlp/extract_qualif.py` |
| **Scénarios liés** | ST-NL-010, ST-FT-013 |
| **Travail** | Regex `r"qualification\s+(?:et\s+classification\s+)?(?:catégorie\s+)?([Qq][1-6])"` ; mapping vers table `qualification`. |

### NLP-03 — Extraction des agréments structurée 🟠
| Champ | Détail |
|---|---|
| **Priorité** | 🟠 P1 |
| **Effort** | M (2 j) |
| **Sprint cible** | S5 |
| **Composant** | `nlp/extract_agrement.py` |
| **Scénarios liés** | ST-NL-011, ST-FT-014 |
| **Travail** | `r"agr[ée]ment\s+(?:de\s+classe\s+)?([A-Z0-9]+)"` ; sortie `[{type, classe}]`. |

### NLP-04 — Extraction date d'ouverture des plis 🟠
| Champ | Détail |
|---|---|
| **Priorité** | 🟠 P1 |
| **Effort** | M (2 j) |
| **Sprint cible** | S5 |
| **Composant** | `nlp/extract_dates_ouverture.py` |
| **Scénarios liés** | ST-NL-012, ST-FT-011 |
| **Travail** | Patterns : `r"séance d'ouverture.*?(\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\s*(?:à\s*)?\d{1,2}h\d{0,2})"` ; normaliser en ISO 8601. |

### NLP-05 — Extraction date limite de remise (déjà partiellement OK) 🟡
| Champ | Détail |
|---|---|
| **Priorité** | 🟡 P2 |
| **Effort** | S (0.5 j) |
| **Sprint cible** | S5 |
| **Composant** | `nlp/extract_entities.py` |
| **Scénarios liés** | ST-NL-013, ST-FT-012 |
| **Travail** | Améliorer la précision du pattern existant ; distinguer « date limite de remise » vs « date d'ouverture ». |

### NLP-06 — Reconnaissance des modèles d'avis 12-10, 13-10 🟡
| Champ | Détail |
|---|---|
| **Priorité** | 🟡 P2 |
| **Effort** | S (1 j) |
| **Sprint cible** | S5 |
| **Composant** | `nlp/extract_modele.py` |
| **Scénarios liés** | ST-NL-021 |
| **Travail** | Patterns officiels (avis 12-10, 13-10, etc.) ; remplissage de `marches.modele_reference`. |

### NLP-07 — Extraction des contacts (email, téléphone, adresse) 🟡
| Champ | Détail |
|---|---|
| **Priorité** | 🟡 P2 |
| **Effort** | S (1 j) |
| **Sprint cible** | V1 |
| **Composant** | `nlp/extract_contacts.py` |
| **Scénarios liés** | Scénario O-07 |
| **Travail** | Regex email + téléphone marocain `(+212|0)[5-7]\d{8}` ; normalisation. |

### NLP-08 — Extraction des références réglementaires 🟡
| Champ | Détail |
|---|---|
| **Priorité** | 🟡 P2 |
| **Effort** | S (1 j) |
| **Sprint cible** | V1 |
| **Composant** | `nlp/extract_refs_reglementaires.py` |
| **Scénarios liés** | Scénario O-06 |
| **Travail** | `r"(article\s+\d+\s+du\s+d[ée]cret\s+n[°º]?\s*[\d-]+)"` ; LLM en fallback. |

### NLP-09 — Reconnaissance bilingue FR/AR sur les entités 🟠
| Champ | Détail |
|---|---|
| **Priorité** | 🟠 P1 |
| **Effort** | L (5 j) |
| **Sprint cible** | V1 |
| **Composant** | `nlp/multilang_extract.py` |
| **Scénarios liés** | ST-NL-014 |
| **Travail** | spaCy `xx` (multilingue) + CamemBERT (FR) + AraBERT (AR) ; voter les sorties. |

### NLP-10 — Extraction avancée par LLM (Mistral / GPT-4o) 🟡
| Champ | Détail |
|---|---|
| **Priorité** | 🟡 P2 |
| **Effort** | M (3 j) |
| **Sprint cible** | V1 |
| **Composant** | `nlp/llm_extract.py` |
| **Scénarios liés** | Scénario O-03 |
| **Travail** | 1. Prompt structuré : « Extrais les entités de ce DAO au format JSON. ».<br>2. Cache des résultats par hash.<br>3. Mode « fallback » activé si confiance regex < 0.7. |

### NLP-11 — Détection automatique de la langue principale 🟠
| Champ | Détail |
|---|---|
| **Priorité** | 🟠 P1 |
| **Effort** | S (0.5 j) |
| **Sprint cible** | S5 |
| **Composant** | `nlp/lang_detect.py` |
| **Scénarios liés** | Scénario O-05 |
| **Travail** | `from langdetect import detect` ; sortie par page ; stockée dans `OcrLog.detected_languages`. |

### NLP-12 — Score de confiance par entité 🟡
| Champ | Détail |
|---|---|
| **Priorité** | 🟡 P2 |
| **Effort** | M (2 j) |
| **Sprint cible** | S5 |
| **Composant** | `nlp/extract_entities.py` |
| **Scénarios liés** | ST-NL-015 |
| **Travail** | Pour chaque regex, calculer un score (longueur match / contexte, présence de mots-clés validant, etc.). |

### NLP-13 — Détection de documents non conformes (`low_quality`) 🟠
| Champ | Détail |
|---|---|
| **Priorité** | 🟠 P1 |
| **Effort** | S (0.5 j) |
| **Sprint cible** | S5 |
| **Composant** | `nlp/quality.py` |
| **Scénarios liés** | ST-NL-017 |
| **Travail** | Si < 3 entités extraites → `documents.low_quality = True`. |

### NLP-14 — Idempotence de l'extraction 🟡
| Champ | Détail |
|---|---|
| **Priorité** | 🟡 P2 |
| **Effort** | S (0.5 j) |
| **Sprint cible** | S5 |
| **Composant** | `nlp/extract_entities.py` |
| **Scénarios liés** | ST-NL-018 |
| **Travail** | Contrainte `UNIQUE(document_id, field_name)` sur `extractions_nlp` ; upsert. |

### NLP-15 — Audit des regex utilisées (≥ 50 patterns) 🟡
| Champ | Détail |
|---|---|
| **Priorité** | 🟡 P2 |
| **Effort** | M (2 j) |
| **Sprint cible** | S5 |
| **Composant** | `tests/test_nlp_patterns.py` |
| **Scénarios liés** | ST-NL-020 |
| **Travail** | Suite de tests paramétrée sur 50+ cas. |

### NLP-16 — Améliorer l'extraction du maître d'ouvrage (spaCy) 🟠
| Champ | Détail |
|---|---|
| **Priorité** | 🟠 P1 |
| **Effort** | M (2 j) |
| **Sprint cible** | S5 |
| **Composant** | `nlp/extract_entities.py:84-94` |
| **Scénarios liés** | ST-NL-003 |
| **Description** | Le code actuel a un fallback bizarre : `elif mo_match: add_field(...)` n'est jamais atteint si `nlp` est `True` car le `if nlp:` est prioritaire. |
| **Travail** | 1. Refactor avec scoring.<br>2. Améliorer le modèle spaCy avec un `EntityRuler` custom pour les ministères marocains. |

### NLP-17 — Pipeline d'extraction asynchrone 🟠
| Champ | Détail |
|---|---|
| **Priorité** | 🟠 P1 |
| **Effort** | M (2 j) |
| **Sprint cible** | S5 |
| **Composant** | `backend/tasks.py` |
| **Scénarios liés** | Scénario I-04 (webhooks) |
| **Travail** | Refactor `process_document_async` pour utiliser Celery ; suivi via `GET /jobs/{id}`. |

### NLP-18 — Tableur des entités extraites (export CSV/Excel) 🟡
| Champ | Détail |
|---|---|
| **Priorité** | 🟡 P2 |
| **Effort** | S (1 j) |
| **Sprint cible** | V1 |
| **Composant** | `nlp/export.py` |
| **Scénarios liés** | Scénario O-08 |
| **Travail** | `GET /api/v1/documents/{id}/entities?format=csv`. |

---

## 7. Tickets Machine Learning (ML-01..18)

### ML-01 — Cross-validation StratifiedKFold (k=5) 🟠
| Champ | Détail |
|---|---|
| **Priorité** | 🟠 P1 |
| **Effort** | S (1 j) |
| **Sprint cible** | S5 |
| **Composant** | `ml/train_classifier.py` |
| **Scénarios liés** | ST-ML-001 |
| **Travail** | `from sklearn.model_selection import StratifiedKFold, cross_val_score` ; `scores = cross_val_score(svm, X, y, cv=5)` ; rapport. |

### ML-02 — Modèles baseline (DummyClassifier) 🟠
| Champ | Détail |
|---|---|
| **Priorité** | 🟠 P1 |
| **Effort** | S (0.5 j) |
| **Sprint cible** | S5 |
| **Composant** | `ml/baseline.py` |
| **Scénarios liés** | Scénario ML-01 (correction) |
| **Travail** | `from sklearn.dummy import DummyClassifier` ; comparer la SVM au baseline majoritaire. |

### ML-03 — Gestion du déséquilibre (`class_weight='balanced'`) 🟠
| Champ | Détail |
|---|---|
| **Priorité** | 🟠 P1 |
| **Effort** | S (0.5 j) |
| **Sprint cible** | S5 |
| **Composant** | `ml/train_classifier.py` |
| **Scénarios liés** | ST-ML-021 |
| **Travail** | `SVC(class_weight='balanced')` ou `SMOTE` via `imbalanced-learn`. |

### ML-04 — Explicabilité (SHAP) 🟠
| Champ | Détail |
|---|---|
| **Priorité** | 🟠 P1 |
| **Effort** | M (3 j) |
| **Sprint cible** | V1 |
| **Composant** | `ml/explain.py` |
| **Scénarios liés** | ST-ML-007, ST-ML-012 |
| **Travail** | `import shap` ; `KernelExplainer` sur top features TF-IDF ; sortie JSON + UI. |

### ML-05 — Confusion matrix + classification report 🟠
| Champ | Détail |
|---|---|
| **Priorité** | 🟠 P1 |
| **Effort** | S (0.5 j) |
| **Sprint cible** | S5 |
| **Composant** | `ml/metrics.py` |
| **Scénarios liés** | ST-ML-010, ST-ML-011 |
| **Travail** | `from sklearn.metrics import confusion_matrix, classification_report` ; endpoint `GET /api/v1/ml/metrics` retourne le rapport. |

### ML-06 — Feature importance (top 20) 🟡
| Champ | Détail |
|---|---|
| **Priorité** | 🟡 P2 |
| **Effort** | S (1 j) |
| **Sprint cible** | V1 |
| **Composant** | `ml/importance.py` |
| **Scénarios liés** | ST-ML-012 |
| **Travail** | `coef = svm.coef_.toarray().argsort()[:, -20:]` ; top features par classe. |

### ML-07 — Versioning des modèles (MLflow ou table custom) 🟠
| Champ | Détail |
|---|---|
| **Priorité** | 🟠 P1 |
| **Effort** | M (3 j) |
| **Sprint cible** | V1 |
| **Composant** | `ml/registry.py` |
| **Scénarios liés** | ST-ML-013, E20 |
| **Travail** | 1. `mlflow.set_tracking_uri` ; `mlflow.sklearn.log_model(svm, "svm")`.<br>2. UI : rollback en un clic.<br>3. OU table custom `model_version(id, name, version, metrics, is_active, created_at)`. |

### ML-08 — Drift monitoring (PSI / KS test) 🟡
| Champ | Détail |
|---|---|
| **Priorité** | 🟡 P2 |
| **Effort** | M (3 j) |
| **Sprint cible** | V1 |
| **Composant** | `ml/drift.py` |
| **Scénarios liés** | ST-ML-014 |
| **Travail** | Job quotidien ; `psi = (ref - cur) * ln(ref / cur)` ; alerte Prometheus si PSI > 0.2. |

### ML-09 — A/B testing entre deux versions 🟡
| Champ | Détail |
|---|---|
| **Priorité** | 🟡 P2 |
| **Effort** | M (2 j) |
| **Sprint cible** | V1 |
| **Composant** | `ml/ab_test.py` |
| **Scénarios liés** | ST-ML-015 |
| **Travail** | Hash du `marche_id % 2` pour router vers v1 ou v2 ; métriques comparées. |

### ML-10 — Audit biais (genre, région, langue) 🟡
| Champ | Détail |
|---|---|
| **Priorité** | 🟡 P2 |
| **Effort** | M (2 j) |
| **Sprint cible** | V1 |
| **Composant** | `ml/bias.py` |
| **Scénarios liés** | ST-ML-016 |
| **Travail** | Calculer accuracy par sous-groupe ; rapport `audit/biais_<date>.json`. |

### ML-11 — Calibration des scores (`CalibratedClassifierCV`) 🟠
| Champ | Détail |
|---|---|
| **Priorité** | 🟠 P1 |
| **Effort** | S (0.5 j) |
| **Sprint cible** | S5 |
| **Composant** | `ml/calibration.py` |
| **Scénarios liés** | Scénario ML-08 |
| **Travail** | `CalibratedClassifierCV(svm, method='sigmoid', cv=3)`. |

### ML-12 — IsolationForest : seuil ajustable 🟠
| Champ | Détail |
|---|---|
| **Priorité** | 🟠 P1 |
| **Effort** | S (1 j) |
| **Sprint cible** | S5 |
| **Composant** | `ml/anomaly.py` |
| **Scénarios liés** | Scénario ML-07 |
| **Travail** | Slider UI `contamination` de 0.01 à 0.20 ; persistance en BDD. |

### ML-13 — Test de régression modèle (golden dataset) 🟡
| Champ | Détail |
|---|---|
| **Priorité** | 🟡 P2 |
| **Effort** | S (1 j) |
| **Sprint cible** | V1 |
| **Composant** | `tests/test_ml_regression.py` |
| **Scénarios liés** | ST-ML-020 |
| **Travail** | `tests/fixtures/golden_predictions.json` ; assertion sur les prédictions. |

### ML-14 — Modèle de scoring de risque (méta-apprentissage) 🟡
| Champ | Détail |
|---|---|
| **Priorité** | 🟡 P2 |
| **Effort** | L (5 j) |
| **Sprint cible** | V1 |
| **Composant** | `ml/risk_score.py` |
| **Scénarios liés** | Scénario M-02 |
| **Travail** | Combiner SVM + IsolationForest + heuristiques via régression logistique. Score 0-100. |

### ML-15 — Détection de doublons inter-documents (MinHash/LSH) 🟡
| Champ | Détail |
|---|---|
| **Priorité** | 🟡 P2 |
| **Effort** | M (3 j) |
| **Sprint cible** | V1 |
| **Composant** | `ml/dedup.py` |
| **Scénarios liés** | Scénario M-03 |
| **Travail** | `datasketch.MinHash` ; seuil Jaccard > 0.8. |

### ML-16 — Embeddings multilingues pour recherche sémantique 🟠
| Champ | Détail |
|---|---|
| **Priorité** | 🟠 P1 |
| **Effort** | L (5 j) |
| **Sprint cible** | V1 |
| **Composant** | `ml/embeddings.py` |
| **Scénarios liés** | Scénario 5.1, M-07 |
| **Travail** | 1. `paraphrase-multilingual-MiniLM-L12-v2` (Sentence-Transformers).<br>2. Index `pgvector` (HNSW).<br>3. Endpoint `POST /api/v1/search/semantic`. |

### ML-17 — Chatbot Q&A (RAG) sur les DAO 🟡
| Champ | Détail |
|---|---|
| **Priorité** | 🟡 P2 |
| **Effort** | L (8 j) |
| **Sprint cible** | V1 |
| **Composant** | `ml/rag_chatbot.py` |
| **Scénarios liés** | Scénario 5.2 |
| **Travail** | 1. LangChain + Mistral 7B (auto-hébergé) ou GPT-4o (API).<br>2. Citations cliquables vers le PDF source. |

### ML-18 — Modèles de prévision (Prophet) 🟡
| Champ | Détail |
|---|---|
| **Priorité** | 🟡 P2 |
| **Effort** | L (5 j) |
| **Sprint cible** | V1 |
| **Composant** | `ml/forecast.py` |
| **Scénarios liés** | E17, Scénario M-01 |
| **Travail** | `prophet` ; 12 mois forecast ; intervalle de confiance 95 %. |

---

## 8. Tickets Frontend / UX (UI-01..40)

### UI-01 — Gestion d'état globale (Zustand) 🟠
| Champ | Détail |
|---|---|
| **Priorité** | 🟠 P1 |
| **Effort** | M (2 j) |
| **Sprint cible** | S2 |
| **Composant** | `frontend-react/src/store/` |
| **Scénarios liés** | Scénario F-01 |
| **Travail** | Installer Zustand ; stores `useAuthStore`, `useFiltersStore`, `useUIStore`. |

### UI-02 — Intercepteur Axios + Toast (Sonner) 🟠
| Champ | Détail |
|---|---|
| **Priorité** | 🟠 P1 |
| **Effort** | S (1 j) |
| **Sprint cible** | S1 |
| **Composant** | `frontend-react/src/api/axios.js` |
| **Scénarios liés** | Scénario F-02 |
| **Travail** | `axios.interceptors.response.use(onSuccess, onError)` ; toast rouge sur 4xx/5xx. |

### UI-03 — Skeleton de chargement 🟠
| Champ | Détail |
|---|---|
| **Priorité** | 🟠 P1 |
| **Effort** | S (1 j) |
| **Sprint cible** | S2 |
| **Composant** | `frontend-react/src/components/Skeleton.jsx` |
| **Scénarios liés** | ST-DB-005 |
| **Travail** | Composant `<Skeleton />` réutilisable ; appliqué sur Dashboard, SearchFTS, DocumentDetail. |

### UI-04 — Bouton « Réinitialiser » sur la recherche 🔴
| Champ | Détail |
|---|---|
| **Priorité** | 🔴 P0 |
| **Effort** | S (0.5 j) |
| **Sprint cible** | S2 |
| **Composant** | `frontend-react/src/components/SearchFTS.jsx` |
| **Scénarios liés** | ST-FT-026, ST-E2E-010 |
| **Travail** | Ajouter `<button onClick={resetFilters}>Réinitialiser</button>` à côté du bouton « Rechercher ». |

### UI-05 — Filtres avancés (type d'avis, qualif, agrément, état) 🔴
| Champ | Détail |
|---|---|
| **Priorité** | 🔴 P0 |
| **Effort** | M (3 j) |
| **Sprint cible** | S2 |
| **Composant** | `frontend-react/src/components/AdvancedFilters.jsx` |
| **Scénarios liés** | ST-UI-016, ST-FT-013..016 |
| **Travail** | 1. Dropdown `type_avis` (8 valeurs) chargé via `/api/v1/ref/type-avis`.<br>2. Multi-select `qualifications`.<br>3. Multi-select `agrements`.<br>4. Dropdown `etat` (5 valeurs).<br>5. 2 date pickers `date_ouverture_plis`. |

### UI-06 — Tri configurable (date / montant / pertinence) 🟠
| Champ | Détail |
|---|---|
| **Priorité** | 🟠 P1 |
| **Effort** | S (1 j) |
| **Sprint cible** | S2 |
| **Composant** | `frontend-react/src/components/SearchFTS.jsx` |
| **Scénarios liés** | ST-FT-019..021, ST-UI-013 |
| **Travail** | Dropdown `sortBy=date|montant|pertinence` ; `orderDir=asc|desc`. |

### UI-07 — Export CSV/Excel depuis la recherche 🔴
| Champ | Détail |
|---|---|
| **Priorité** | 🔴 P0 |
| **Effort** | M (2 j) |
| **Sprint cible** | S2 |
| **Composant** | `frontend-react/src/components/SearchFTS.jsx` |
| **Scénarios liés** | ST-FT-028, ST-FT-029, ST-E2E-009 |
| **Travail** | Boutons « Exporter CSV » et « Exporter Excel » ; `axios.get(..., {responseType: 'blob'})` ; `URL.createObjectURL`. |

### UI-08 — Surlignage des termes trouvés 🟠
| Champ | Détail |
|---|---|
| **Priorité** | 🟠 P1 |
| **Effort** | S (1 j) |
| **Sprint cible** | S2 |
| **Composant** | `frontend-react/src/components/SearchResult.jsx` |
| **Scénarios liés** | ST-FT-022, ST-UI-011 |
| **Travail** | `dangerouslySetInnerHTML={{__html: result.highlight}}` (avec sanitize DOMPurify). |

### UI-09 — Filtre par état (En cours, Clôturé…) 🔴
| Champ | Détail |
|---|---|
| **Priorité** | 🔴 P0 |
| **Effort** | S (0.5 j) |
| **Sprint cible** | S2 |
| **Composant** | `frontend-react/src/components/AdvancedFilters.jsx` |
| **Scénarios liés** | ST-FT-016 |
| **Travail** | Dropdown `etat` dans le panneau de filtres avancés. |

### UI-10..UI-40 — Autres tickets Frontend

| ID | Titre | Pri. | Effort | Sprint |
|---|---|---|---|---|
| UI-10 | i18next FR/AR | 🟠 | M | S6 |
| UI-11 | Page Login | 🔴 | M | S1 |
| UI-12 | Page Profil utilisateur | 🟠 | M | S1 |
| UI-13 | Page Gestion des utilisateurs (admin) | 🟠 | M | S1 |
| UI-14 | Page Audit & Traçabilité | 🟡 | M | S1 |
| UI-15 | Page Centre d'alertes (E11) | 🟡 | L | V1 |
| UI-16 | Page Cartographie (E12) | 🟡 | L | V1 |
| UI-17 | Page Comparateur (E13) | 🟡 | L | V1 |
| UI-18 | Page Dashboard Acheteur (E14) | 🟡 | L | V1 |
| UI-19 | Page Dashboard Fournisseur (E15) | 🟡 | L | V1 |
| UI-20 | Page Analytics Avancés (E16) | 🟡 | L | V2 |
| UI-21 | Page Prédictif (E17) | 🟡 | L | V1 |
| UI-22 | Page Labellisation (E19) | 🟡 | L | V2 |
| UI-23 | Page Catalogue ML (E20) | 🟡 | M | V1 |
| UI-24 | Page Notifications (E21) | 🟡 | M | V2 |
| UI-25 | Page Rapports programmés (E22) | 🟡 | M | V1 |
| UI-26 | PWA installable (vite-plugin-pwa) | 🟡 | M | S6 |
| UI-27 | Mode sombre/clair toggle | 🟠 | S | S2 |
| UI-28 | Raccourcis clavier (`/` focus recherche) | 🟠 | S | S2 |
| UI-29 | Lazy loading des routes (React.lazy) | 🟠 | S | S2 |
| UI-30 | 404 / 403 / 500 pages | 🟠 | S | S1 |
| UI-31 | `data-testid` partout (convention) | 🟠 | S | S1 |
| UI-32 | Bundle visualizer (`vite-bundle-visualizer`) | 🟡 | S | S2 |
| UI-33 | Storybook | 🟡 | M | S2 |
| UI-34 | Tests Vitest + React Testing Library | 🟠 | M | S1-S6 |
| UI-35 | Tests Cypress (≥ 20 scénarios) | 🟠 | L | S1-S6 |
| UI-36 | Accessibilité (aria-label, focus visible) | 🟠 | M | S2 |
| UI-37 | Notifications navigateur (Web Notifications API) | 🟡 | S | V1 |
| UI-38 | Drag & drop widgets (E16) | 🟡 | M | V2 |
| UI-39 | WebSocket Monitoring (logs temps réel) | 🟠 | M | S1 |
| UI-40 | Heatmap calendrier des publications | 🟡 | M | V1 |

---

## 9. Tickets Authentification & RBAC (AU-01..15)

### AU-01 — Page Login (UI-11) 🔴
| Champ | Détail |
|---|---|
| **Priorité** | 🔴 P0 |
| **Effort** | M (2 j) |
| **Sprint cible** | S1 |
| **Composant** | `frontend-react/src/components/Login.jsx` (à créer) |
| **Scénarios liés** | ST-AU-001..003 |
| **Travail** | 1. Formulaire email + password + bouton « Se connecter ».<br>2. `react-hook-form` + `zod` pour validation.<br>3. Stockage du JWT en `httpOnly cookie` (sécurisé).<br>4. Redirection vers `/` après login.<br>5. Lien « Mot de passe oublié ». |

### AU-02 — Logout 🔴
| Champ | Détail |
|---|---|
| **Priorité** | 🔴 P0 |
| **Effort** | S (0.5 j) |
| **Sprint cible** | S1 |
| **Scénarios liés** | ST-E2E-001 |
| **Travail** | Bouton « Déconnexion » dans la Topbar ; appel `POST /auth/logout`. |

### AU-03 — Mot de passe oublié (email + token) 🟠
| Champ | Détail |
|---|---|
| **Priorité** | 🟠 P1 |
| **Effort** | M (2 j) |
| **Sprint cible** | S1 |
| **Composant** | `backend/auth/forgot_password.py` |
| **Scénarios liés** | ST-AU-004 |
| **Travail** | 1. `POST /api/v1/auth/forgot-password` génère token (15 min).<br>2. Email via SMTP (MailHog en dev).<br>3. `POST /api/v1/auth/reset-password?token=...` met à jour le mot de passe.<br>4. Table `password_reset_token`. |

### AU-04 — Changement de mot de passe 🟠
| Champ | Détail |
|---|---|
| **Priorité** | 🟠 P1 |
| **Effort** | S (1 j) |
| **Sprint cible** | S1 |
| **Scénarios liés** | ST-AU-005 |
| **Travail** | Page `/profile` ; formulaire ancien + nouveau + confirmation ; validation complexité. |

### AU-05 — Verrouillage de compte (5 tentatives) 🔴
| Champ | Détail |
|---|---|
| **Priorité** | 🔴 P0 |
| **Effort** | S (1 j) |
| **Sprint cible** | S1 |
| **Scénarios liés** | ST-AU-006 |
| **Travail** | 1. Colonne `user.failed_login_attempts`, `user.locked_until`.<br>2. Après 5 échecs → blocage 15 min, email admin.<br>3. Logout des sessions actives. |

### AU-06 — Session timeout (30 min) 🟠
| Champ | Détail |
|---|---|
| **Priorité** | 🟠 P1 |
| **Effort** | S (0.5 j) |
| **Sprint cible** | S1 |
| **Scénarios liés** | ST-AU-007 |
| **Travail** | JWT `exp = now() + 30min` ; refresh token sliding window. |

### AU-07 — MFA (TOTP) 🟠
| Champ | Détail |
|---|---|
| **Priorité** | 🟠 P1 |
| **Effort** | M (2 j) |
| **Sprint cible** | V1 |
| **Scénarios liés** | Scénario E10 |
| **Travail** | 1. `pyotp.TOTP` ; QR code.<br>2. Colonne `user.mfa_secret`, `user.mfa_enabled`.<br>3. UI : setup MFA dans `/profile`. |

### AU-08..AU-15 — Autres tickets Auth

| ID | Titre | Pri. | Effort | Sprint |
|---|---|---|---|---|
| AU-08 | Page Gestion des utilisateurs (admin) | 🟠 | M | S1 |
| AU-09 | Éditeur de rôles et permissions | 🟠 | M | S1 |
| AU-10 | Audit log immuable | 🔴 | M | S1 |
| AU-11 | Politique de mot de passe configurable | 🟠 | S | S1 |
| AU-12 | Rate limiting par utilisateur | 🟠 | S | S1 |
| AU-13 | GDPR / droit à l'oubli | 🟡 | M | V1 |
| AU-14 | SSO OIDC (Keycloak) | 🟡 | L | V1 |
| AU-15 | Historique de connexion (IP, géoloc) | 🟠 | S | S1 |

---

## 10. Tickets Sécurité (SE-01..15)

### SE-01 — Helmet (headers HTTP) 🔴
| Champ | Détail |
|---|---|
| **Priorité** | 🔴 P0 |
| **Effort** | S (0.5 j) |
| **Sprint cible** | S1 |
| **Composant** | `backend/main.py` |
| **Scénarios liés** | ST-SE-005, ST-API-018 |
| **Travail** | `from secure import Secure` ; middleware FastAPI qui ajoute `Strict-Transport-Security`, `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, `Content-Security-Policy`. |

### SE-02 — HTTPS obligatoire (Let's Encrypt) 🔴
| Champ | Détail |
|---|---|
| **Priorité** | 🔴 P0 |
| **Effort** | S (1 j) |
| **Sprint cible** | S4 |
| **Composant** | Nginx reverse proxy, `docker-compose.yml` |
| **Scénarios liés** | ST-SE-007 |
| **Travail** | 1. Certbot en cron.<br>2. Nginx : `return 301 https://$host$request_uri`. |

### SE-03 — Gestionnaire de secrets (Vault / Infisical) 🟠
| Champ | Détail |
|---|---|
| **Priorité** | 🟠 P1 |
| **Effort** | M (2 j) |
| **Sprint cible** | S4 |
| **Composant** | `backend/config.py` |
| **Scénarios liés** | ST-SE-006 |
| **Travail** | 1. Remplacer `.env` par Vault.<br>2. `pydantic.BaseSettings` charge depuis Vault.<br>3. Tests : `grep -r "OPENAI_API_KEY" dist/` doit retourner 0 hit. |

### SE-04 — Tests OWASP ZAP automatisés 🟠
| Champ | Détail |
|---|---|
| **Priorité** | 🟠 P1 |
| **Effort** | M (2 j) |
| **Sprint cible** | S4 |
| **Composant** | `.github/workflows/owasp.yml` |
| **Travail** | Lancement `zap-baseline.py` en CI ; alerte si alertes HIGH. |

### SE-05..SE-15 — Autres tickets Sécurité

| ID | Titre | Pri. | Effort | Sprint |
|---|---|---|---|---|
| SE-05 | Scan `pip-audit` + `npm audit` en CI | 🟠 | S | S1 |
| SE-06 | Scan `trivy` des images Docker | 🟠 | S | S4 |
| SE-07 | CSRF protection | 🟠 | S | S1 |
| SE-08 | Validation stricte des uploads (mime + size) | 🟠 | S | S1 |
| SE-09 | Sanitization des inputs (DOMPurify côté front) | 🟠 | S | S1 |
| SE-10 | Chiffrement at rest (LUKS ou KMS) | 🟡 | M | V1 |
| SE-11 | WAF (Cloudflare) | 🟡 | M | V1 |
| SE-12 | Penetration testing annuel | 🟡 | XL | V1 |
| SE-13 | Backup chiffré BDD | 🟠 | S | S4 |
| SE-14 | Rotation des secrets JWT | 🟠 | S | S4 |
| SE-15 | Politique CORS stricte (déjà traitée en B-08) | 🟠 | S | S1 |

---

## 11. Tickets DevOps / CI-CD / Observabilité (OPS-01..18)

### OPS-01 — Pipeline CI GitHub Actions 🟠
| Champ | Détail |
|---|---|
| **Priorité** | 🟠 P1 |
| **Effort** | M (2 j) |
| **Sprint cible** | S4 |
| **Composant** | `.github/workflows/ci.yml` |
| **Travail** | Étapes : lint, test-unit, test-int, test-e2e, security, build, lighthouse. |

### OPS-02 — Dockerfile multi-stage 🟠
| Champ | Détail |
|---|---|
| **Priorité** | 🟠 P1 |
| **Effort** | S (1 j) |
| **Sprint cible** | S4 |
| **Composant** | `Dockerfile`, `backend/Dockerfile` |
| **Travail** | Stage 1 : `python:3.11-slim` + `pip install` ; Stage 2 : `python:3.11-slim` + copy artifacts. Image finale < 500 Mo. |

### OPS-03 — docker-compose complet 🟠
| Champ | Détail |
|---|---|
| **Priorité** | 🟠 P1 |
| **Effort** | S (1 j) |
| **Sprint cible** | S4 |
| **Composant** | `docker-compose.yml` |
| **Travail** | Services : `api`, `postgres`, `redis`, `minio`, `prometheus`, `grafana`, `nginx`, `frontend`. |

### OPS-04 — Métriques Prometheus 🟠
| Champ | Détail |
|---|---|
| **Priorité** | 🟠 P1 |
| **Effort** | M (2 j) |
| **Sprint cible** | S4 |
| **Composant** | `backend/metrics.py` |
| **Travail** | `prometheus_fastapi_instrumentator` ; `GET /metrics`. |

### OPS-05 — Dashboards Grafana 🟡
| Champ | Détail |
|---|---|
| **Priorité** | 🟡 P2 |
| **Effort** | M (2 j) |
| **Sprint cible** | S4 |
| **Composant** | `ops/grafana/dashboards/` |
| **Travail** | Dashboard « GED-Production » avec 6 panneaux. |

### OPS-06..OPS-18 — Autres tickets Ops

| ID | Titre | Pri. | Effort | Sprint |
|---|---|---|---|---|
| OPS-06 | Alertes PagerDuty / email | 🟡 | S | S4 |
| OPS-07 | Backup PostgreSQL quotidien | 🟠 | S | S4 |
| OPS-08 | Logs centralisés (Loki / ELK) | 🟡 | M | V1 |
| OPS-09 | Tracing OpenTelemetry + Jaeger | 🟡 | M | V1 |
| OPS-10 | Healthcheck profond (DB+Redis+MinIO) | 🟠 | S | S1 |
| OPS-11 | Front Dockerfile (Vite build + nginx) | 🟠 | S | S4 |
| OPS-12 | Tagging Git (semver + changelog auto) | 🟠 | S | S4 |
| OPS-13 | Lighthouse CI | 🟠 | S | S4 |
| OPS-14 | Documentation OpenAPI enrichie | 🟡 | M | S4 |
| OPS-15 | Cache Redis | 🟠 | M | S1 |
| OPS-16 | File d'attente Celery + Redis | 🟠 | M | S1 |
| OPS-17 | MinIO (stockage objet S3-compat) | 🟠 | M | S1 |
| OPS-18 | Politique de retention (archivage > 5 ans) | 🟡 | S | V1 |

---

## 12. Tickets Tests & Qualité (T-01..15)

### T-01 — Couverture ≥ 80 % 🔴
| Champ | Détail |
|---|---|
| **Priorité** | 🔴 P0 |
| **Effort** | L (5 j) |
| **Sprint cible** | S1-S6 |
| **Composant** | `tests/`, `pytest.ini` |
| **Travail** | Couvrir `backend/`, `nlp/`, `ml/`, `ingestion/`, `ocr/` ; `pytest --cov-fail-under=80`. |

### T-02 — Tests E2E Cypress (≥ 20 scénarios) 🔴
| Champ | Détail |
|---|---|
| **Priorité** | 🔴 P0 |
| **Effort** | L (5 j) |
| **Sprint cible** | S1-S6 |
| **Composant** | `frontend-react/cypress/e2e/` |
| **Travail** | 20 scénarios couvrant les parcours Lecteur, Analyste, Admin. |

### T-03 — Tests de régression visuelle (Playwright snapshots) 🟠
| Champ | Détail |
|---|---|
| **Priorité** | 🟠 P1 |
| **Effort** | M (2 j) |
| **Sprint cible** | S4 |
| **Composant** | `tests/visual/` |
| **Travail** | Snapshots LandingPage, Dashboard, DocumentDetail (FR + AR). |

### T-04..T-15 — Autres tickets Tests

| ID | Titre | Pri. | Effort | Sprint |
|---|---|---|---|---|
| T-04 | Tests de charge (k6 / Locust) | 🟠 | M | S4 |
| T-05 | Tests de sécurité (OWASP ZAP) | 🟠 | M | S4 |
| T-06 | Contract testing (Schemathesis) | 🟡 | M | V1 |
| T-07 | Tests composants (Vitest + RTL) | 🟠 | M | S1-S6 |
| T-08 | Tests de mutation (mutmut) | 🟡 | M | V1 |
| T-09 | Tests d'accessibilité (axe-core) | 🟠 | S | S2 |
| T-10 | Tests de performance (k6 + SLO) | 🟠 | M | S4 |
| T-11 | Tests DRP (disaster recovery) | 🟡 | S | V1 |
| T-12 | Fixtures golden (OCR, NLP, ML, FTS) | 🟠 | M | S1-S5 |
| T-13 | Tests snapshot HTML du portail | 🟠 | M | S1 |
| T-14 | `pytest-postgresql` (CI real DB) | 🟠 | S | S1 |
| T-15 | `factory-boy` (génération de données) | 🟠 | S | S1 |

---

## 13. Tickets Documentation (DOC-01..10)

### DOC-01 — README enrichi 🟠
| Champ | Détail |
|---|---|
| **Priorité** | 🟠 P1 |
| **Effort** | S (1 j) |
| **Travail** | Ajouter : description, prérequis, installation, lancement, structure du projet, contribution. |

### DOC-02 — Guide d'utilisation 🟠
| Champ | Détail |
|---|---|
| **Priorité** | 🟠 P1 |
| **Effort** | M (2 j) |
| **Composant** | `docs/user_guide.md` |
| **Travail** | Captures d'écran par écran ; parcours utilisateur. |

### DOC-03 — Guide de déploiement 🟠
| Champ | Détail |
|---|---|
| **Priorité** | 🟠 P1 |
| **Effort** | M (2 j) |
| **Composant** | `docs/deployment.md` |
| **Travail** | Docker, Kubernetes, variables d'env, scaling, monitoring. |

### DOC-04 — Architecture 🟠
| Champ | Détail |
|---|---|
| **Priorité** | 🟠 P1 |
| **Effort** | M (1 j) |
| **Composant** | `docs/architecture.md` |
| **Travail** | Diagrammes C4 (Contexte, Conteneur, Composant, Code). |

### DOC-05..DOC-10 — Autres docs

| ID | Titre | Pri. | Effort |
|---|---|---|---|
| DOC-05 | Guide du modèle de données (ERD) | 🟠 | M |
| DOC-06 | ADRs (Architecture Decision Records) | 🟠 | S |
| DOC-07 | Guide de contribution (CONTRIBUTING.md) | 🟡 | S |
| DOC-08 | Changelog auto (`git-chglog`) | 🟠 | S |
| DOC-09 | Documentation API (OpenAPI + exemples) | 🟠 | M |
| DOC-10 | Postman / Insomnia collection | 🟡 | S |

---

## 14. Tickets Nouveaux écrans (E-10..E-24)

> Détails complets dans `02-ameliorations-et-roadmap.md` §4. Ci-dessous, fiches condensées avec priorités et estimation.

| ID | Écran | Pri. | Effort | Sprint | Dépendances |
|---|---|---|---|---|---|
| E-10 | Authentification & Gestion des utilisateurs | 🔴 | L | S1 | AU-01, AU-08, BDD-10 |
| E-11 | Centre d'alertes & watchlist personnalisée | 🟡 | L | V1 | BDD-13, ING-09 |
| E-12 | Cartographie des AO (Leaflet) | 🟡 | L | V1 | BDD-05, B-30 |
| E-13 | Comparateur d'appels d'offres | 🟡 | L | V1 | B-31, ML-04 |
| E-14 | Tableau de bord Acheteur | 🟡 | L | V1 | BDD-02, E16 |
| E-15 | Tableau de bord Fournisseur | 🟡 | L | V1 | E-11, ML-06 |
| E-16 | Analytics Avancés (DataViz, drag & drop) | 🟡 | XL | V2 | D-09..D-20 |
| E-17 | Prédictif & Prévisions (Prophet) | 🟡 | L | V1 | ML-18 |
| E-18 | Audit & Traçabilité | 🟠 | M | S1 | BDD-11, AU-10 |
| E-19 | Labellisation collaborative | 🟡 | XL | V2 | ML-13, BDD-12 |
| E-20 | Catalogue des modèles ML | 🟡 | M | V1 | ML-07 |
| E-21 | Notifications & Messagerie (WebSocket) | 🟡 | M | V2 | OPS-08, B-32 |
| E-22 | Rapports programmés (PDF/Excel) | 🟡 | M | V1 | DOC-09 |
| E-23 | Mobile-first & PWA | 🟡 | M | S6 | UI-26, OPS-15 |
| E-24 | Data Lineage & Quality | 🟡 | L | V2 | D-12, ML-08 |

---

## 15. Tickets Fonctionnalités transverses (F-01..10)

| ID | Titre | Pri. | Effort | Sprint | Description |
|---|---|---|---|---|---|
| F-01 | Recherche sémantique par embedding (LLM) | 🟡 | M | V1 | Index vectoriel pgvector ; re-ranking hybride BM25 + cosinus |
| F-02 | Chatbot Q&A sur les DAO | 🟡 | L | V1 | RAG LangChain + Mistral/GPT-4o ; citations |
| F-03 | Résumés automatiques | 🟡 | M | V1 | TextRank + LLM abstractive |
| F-04 | i18n FR/AR | 🟠 | M-L | S6 | i18next, RTL layout, dates en chiffres arabes |
| F-05 | Accessibilité WCAG 2.1 AA | 🟠 | M | S2 | Audit Lighthouse ≥ 90 ; NVDA/VoiceOver |
| F-06 | Multi-tenant | 🟡 | XL | V2 | RLS PostgreSQL, sous-domaines |
| F-07 | API publique & Open Data | 🟡 | M | V2 | Endpoints publics, licence CC-BY-SA 4.0 |
| F-08 | Workflow d'approbation | 🟡 | L | V2 | Circuit demandeur → N1 → N2 → exécution |
| F-09 | Sauvegarde de recherche & alertes email | 🟡 | M | V1 | cf. BDD-12, BDD-13 |
| F-10 | Signature électronique (PAdES) | 🟡 | M | V2 | Certificat X.509, HSM, horodatage |

---

## 16. Synthèse & Roadmap

### 16.1 Backlog global consolidé par sprint

| Sprint | Tickets P0 | Tickets P1 | Tickets P2 | Total |
|---|---|---|---|---|
| **S1 — Durcir l'existant** | BDD-01, BDD-06, BDD-07, BDD-08, BDD-09, BDD-10, BDD-11, B-01, B-02, B-08, ING-02, ING-03, ING-04, OC-04, NLP-01, E-10, E-18, AU-01, AU-02, AU-05, AU-10, SE-01, SE-02, OPS-10, OPS-15..17, T-01..03, DOC-01..05, UI-11, UI-13, UI-30, UI-31, UI-34 | B-03, B-04, B-05, B-06, B-09, B-10, ING-01, ING-05, ING-06, ING-11, ING-12, OC-01, OC-05, NLP-02..04, UI-02, UI-39, AU-03, AU-04, AU-06, AU-08, AU-09, AU-11, AU-12, AU-15, SE-03, SE-05, SE-07..09, SE-13, OPS-07 | — | ≈ 80 |
| **S2 — Compléter la recherche** | UI-04, UI-05, UI-07, UI-09, B-20 | UI-01, UI-03, UI-06, UI-08, UI-27, UI-28, UI-29, UI-32, UI-33, UI-36, T-07, T-09, T-12, DOC-09, F-05 | — | ≈ 25 |
| **S3 — Enrichir le Dashboard** | — | B-19, UI-10..UI-25 (sous-ensemble) | — | ≈ 15 |
| **S4 — Ops & Qualité** | T-01 (finalisation), T-02 (≥ 20) | OPS-01..07, OPS-11..14, SE-02, SE-04, SE-06, T-03, T-04, T-10 | — | ≈ 25 |
| **S5 — ML & Données** | — | ML-01..05, ML-11, ML-12, NLP-09, NLP-11, NLP-13, NLP-16, NLP-17, OC-05, OC-08, OC-10, T-13, T-14, T-15 | ML-06, ML-13..15, NLP-12, NLP-14, NLP-15, OC-03, OC-09 | ≈ 30 |
| **S6 — i18n & PWA** | — | F-04, E-23, UI-10, UI-26 | — | ≈ 10 |
| **V1 (post-soutenance, 6 mois)** | — | E-11..E-15, E-17, E-20, E-22, ML-07, ML-16, B-30, B-31, B-32, B-33, ING-07, ING-08, ING-09, ING-10, OC-02, NLP-08, NLP-10, NLP-18, F-01, F-02, F-03, F-09, AU-07, AU-14 | E-21, OPS-08, OPS-09, OPS-18, SE-10, SE-11, T-06, T-08, T-11, F-08 | ≈ 50 |
| **V2 (post-soutenance, 12 mois)** | — | E-16, E-19, E-24, F-06, F-07, F-10 | — | ≈ 15 |

**Total ≈ 250 tickets détaillés** (dont 50 P0 et 100 P1).

### 16.2 Estimations globales

| Phase | Durée | Points totaux | Équipe |
|---|---|---|---|
| MVP (S1-S6) | 12 semaines | ≈ 250 pts | 1 dev senior + 1 dev junior + 1 data scientist |
| V1 (6 mois) | 24 semaines | ≈ 200 pts | 2 devs seniors + 1 data scientist |
| V2 (12 mois) | 36 semaines | ≈ 80 pts | 3 devs seniors + 1 data engineer + 1 UX |

### 16.3 KPIs de succès cibles (V1)

| Catégorie | KPI | Cible |
|---|---|---|
| Adoption | MAU | 200+ |
| Adoption | AO indexés | 50 000+ |
| Adoption | Recherches / jour | 1 000+ |
| Performance | p95 latence API | < 500 ms |
| Performance | p95 latence FTS | < 500 ms |
| Performance | Uptime | 99.5 % |
| Qualité | Précision extraction montants | > 95 % |
| Qualité | Précision SVM | > 88 % |
| Qualité | Couverture tests | > 80 % |
| Qualité | Bugs critiques / sprint | < 5 |
| Sécurité | Incidents | 0 |
| UX | Score SUS | > 75 |
| UX | NPS | > 40 |

### 16.4 Traçabilité Cahier de texte ↔ Tickets

> Chaque scénario `ST-XXX-NNN` du cahier de texte est référencé par au moins un ticket. La matrice complète est disponible en Annexe du cahier de texte (§7.4).

Exemples :
- `ST-FT-028` (export CSV) → UI-07 + B-20
- `ST-AU-001` (accès sans auth) → AU-01 + B-01
- `ST-IN-005` (reprise après crash) → ING-03 + OC-04
- `ST-NL-009` (extraction type d'avis) → NLP-01 + BDD-01
- `ST-DB-012` (perf dashboard p95) → OPS-04 + B-09

---

> **Conclusion Fichier 4** : Ce backlog de **≈ 250 tickets** détaille exhaustivement les actions à mener pour transformer le PFA GED Intelligente en plateforme BI industrialisable. Chaque ticket est chiffré (effort), priorisé (P0/P1/P2), rattaché à un sprint cible, et lié à un ou plusieurs scénarios de validation du cahier de texte. La roadmap MVP (6 sprints) traite l'ensemble des bloquants P0 ; les roadmaps V1 et V2 ouvrent la voie vers la plateforme de référence.
