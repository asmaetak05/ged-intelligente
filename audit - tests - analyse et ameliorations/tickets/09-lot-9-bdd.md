# Lot 9 : Refonte et Consolidation des Données (BDD)

## Tickets Détaillés

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
