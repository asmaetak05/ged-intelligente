# Phase 1 — Unification de la couche données

> **Effort** : 1,5 journée · **Risque** : élevé (touche au cœur de l'API) · **Pré-requis** : Phase 0 terminée

---

## T1.1 — Réécrire `models.py` compatible SQLite + PostgreSQL

**Description & objectif** : supprimer les types PostgreSQL-spécifiques (`TSVECTOR`, `ARRAY`) qui empêchent l'usage en SQLite, ajouter les champs obligatoires du plan (`date_parution`, `date_limite`, `reference`, `region`, `montant` typé), tout en gardant la compatibilité PostgreSQL via `JSON` au lieu d'`ARRAY`.

**Modifications** :

| Module | Action | Détail |
|---|---|---|
| `backend` | `MODIFY` | `backend/models.py` :<br>1. Remplacer `from sqlalchemy.dialects.postgresql import TSVECTOR, ARRAY` par `from sqlalchemy import JSON`.<br>2. `Marche.tsv_search` (TSVECTOR) → `tsv_search = Column(Text, nullable=True)`.<br>3. `Marche.agreements_exiges` (ARRAY) → `Column(JSON, nullable=True)`.<br>4. Ajouter colonnes :<br>   - `montant = Column(Numeric(15, 2), nullable=True)`<br>   - `date_parution = Column(Date, nullable=True, index=True)`<br>   - `date_limite = Column(Date, nullable=True, index=True)`<br>   - `reference = Column(String(100), nullable=True, index=True)`<br>   - `region = Column(String(100), nullable=True, index=True)`<br>5. Renommer `delai_execution_mois` → garder tel quel (Integer).<br>6. Renommer `penalite_retard_mille` → garder tel quel.<br>7. Garder `__table_args__` Index mais sans `postgresql_using='gin'`. |

**Plan de vérification** :
- [ ] `python -c "from backend.models import Base, Marche, Document; print('OK')"` ne lève pas d'exception.
- [ ] `python -c "from backend import models; print([c.name for c in models.Marche.__table__.columns])"` liste les nouveaux champs.
- [ ] Aucune référence à `TSVECTOR` ou `ARRAY` ne subsiste : `grep -rn "TSVECTOR\|ARRAY" backend/models.py` → vide.

---

## T1.2 — Réécrire `database.py` avec bascule auto

**Description & objectif** : permettre à l'API de tourner aussi bien en SQLite (POC) qu'en PostgreSQL (prod) sans modifier le code applicatif.

**Modifications** :

| Module | Action | Détail |
|---|---|---|
| `backend` | `MODIFY` | `backend/database.py` :<br>1. Lire `DATABASE_URL` (défaut : `sqlite:///./ged.db`).<br>2. Si la valeur commence par `sqlite`, utiliser `connect_args={"check_same_thread": False}`.<br>3. Sinon, comportement PostgreSQL par défaut.<br>4. Garder `engine`, `SessionLocal`, `Base`, `get_db()`. |
| `repo` | `NEW` | `.env` (local, non versionné) : `DATABASE_URL=sqlite:///./ged.db` |
| `repo` | `NEW` | `.env.example` : ajouter `DATABASE_URL=sqlite:///./ged.db` ou `postgresql://...` |

**Plan de vérification** :
- [ ] `python -c "from backend.database import engine; print(engine.url)"` affiche le bon driver.
- [ ] Avec `DATABASE_URL=sqlite:///./test.db`, `engine.url.drivername == 'sqlite'`.
- [ ] Avec `DATABASE_URL=postgresql://...`, `engine.url.drivername == 'postgresql'`.

---

## T1.3 — Créer le repository unique

**Description & objectif** : toute la logique SQL/SQLAlchemy doit sortir de `main.py`. Les endpoints ne manipulent plus directement la base.

**Modifications** :

| Module | Action | Détail |
|---|---|---|
| `backend` | `NEW` | `backend/repository.py` (≈ 300 lignes) avec classes :<br>- `MarcheRepository(db: Session)` : `get(id)`, `get_by_numero(numero)`, `list(filters, page, page_size)`, `count(filters)`, `create(payload)`, `update(marche, payload)`, `search_fts(query, limit)`, `kpis()`, `by_month()`, `by_category_month()`, `delai_moyen()`, `top_buyers(limit=10)`, `ocr_quality_pct()`.<br>- `DocumentRepository(db: Session)` : `create()`, `get()`, `update_status()`.<br>- `OcrLogRepository(db: Session)` : `create()`, `list_by_document()`. |

**Plan de vérification** :
- [ ] `python -c "from backend.repository import MarcheRepository"` ne lève pas d'exception.
- [ ] `pytest tests/test_repository.py` (créé en T1.10) passe.

---

## T1.4 — Réécrire `main.py`

**Description & objectif** : `main.py` ne contient plus aucun `sqlite3.connect`. Tous les endpoints passent par les repositories. Ajout des endpoints manquants du plan.

**Modifications** :

| Module | Action | Détail |
|---|---|---|
| `backend` | `MODIFY` | `backend/main.py` :<br>1. Supprimer `import sqlite3`, `def get_db_connection()`, tous les `conn = get_db_connection()`.<br>2. Convertir chaque endpoint en `Depends(get_db)` + repository.<br>3. **Ajouter** :<br>   - `GET /api/v1/ged/appels-offres` (avec query params `page, page_size, ville, organisme, categorie, date_min, date_max, q`)<br>   - `GET /api/v1/ged/appels-offres/{numero_ordre}` (détail + OcrLog + Document.storage_path)<br>   - `GET /api/v1/ged/ocr-quality` (taux réel)<br>   - `GET /api/v1/analytics/delai-moyen`<br>   - `GET /api/v1/analytics/trends/by-category`<br>4. Conserver la **même signature externe** pour les 19 endpoints existants. |
| `backend` | `MODIFY` | `backend/main.py` ligne 292 : changer `app.mount("/", StaticFiles(directory="frontend", html=True))` en `app.mount("/app", StaticFiles(directory="frontend-react/dist", html=True))` (sera effectif après `npm run build` en Phase 5). |

**Plan de vérification** :
- [ ] `grep -n "sqlite3" backend/main.py` → vide.
- [ ] `uvicorn backend.main:app --reload` démarre sans erreur.
- [ ] `curl -s http://localhost:8000/api/v1/ged/appels-offres | python -m json.tool` retourne au moins 1 AO.
- [ ] `curl -s http://localhost:8000/openapi.json | python -c "import sys, json; d=json.load(sys.stdin); print(len(d['paths']))"` → ≥ 22 paths (19 anciens + 3 nouveaux + 1 trends/by-category).

---

## T1.5 — Réécrire `init_db.py`

**Description & objectif** : corriger l'import cassé `AppelOffre`, rendre l'init idempotente.

**Modifications** :

| Module | Action | Détail |
|---|---|---|
| `backend` | `MODIFY` | `backend/init_db.py` :<br>1. Supprimer `from backend.models import AppelOffre`.<br>2. Garder `from backend.models import Base`.<br>3. Appeler `Base.metadata.create_all(bind=engine)` dans un `try/except` avec message clair si PostgreSQL inaccessible. |

**Plan de vérification** :
- [ ] `python -m backend.init_db` crée toutes les tables (idempotent : ré-exécutable sans erreur).
- [ ] `python -c "from backend import models; assert hasattr(models, 'Marche')"` passe.

---

## T1.6 — Configurer Alembic

**Description & objectif** : passer du `create_all` ad hoc à des migrations versionnées (bonne pratique, valorisable en soutenance).

**Modifications** :

| Module | Action | Détail |
|---|---|---|
| `alembic` | `CMD` | `alembic init alembic` |
| `alembic` | `MODIFY` | `alembic/env.py` : importer `Base` depuis `backend.database`, `target_metadata = Base.metadata`. |
| `alembic` | `CMD` | `alembic revision --autogenerate -m "initial schema"` |
| `alembic` | `CMD` | `alembic upgrade head` |
| `alembic` | `NEW` | `alembic/versions/0001_initial_schema.py` (auto-généré) |
| `repo` | `MODIFY` | `docs/installation.md` : ajouter section "Migrations : `alembic upgrade head`" |

**Plan de vérification** :
- [ ] `alembic current` affiche la révision courante.
- [ ] `alembic history` liste la migration.
- [ ] Supprimer `ged.db` puis `alembic upgrade head` recrée le schéma.

---

## T1.7 — Corriger `populate_db.py`

**Description & objectif** : la route utilisée est fausse (`/api/appels_offres/` au lieu de `/api/v1/ged/appels-offres`).

**Modifications** :

| Module | Action | Détail |
|---|---|---|
| `scripts` | `MODIFY` | `scripts/populate_db.py` :<br>1. Changer `api_url_ao = "http://127.0.0.1:8000/api/v1/ged/appels-offres"`.<br>2. Ajouter 18 AO supplémentaires (variété : 6 Travaux, 6 Fournitures, 6 Services/Études).<br>3. Rendre le script idempotent : vérifier l'existence avant POST. |
| `scripts` | `NEW` | `scripts/seed_demo.py` (active) : reprend la logique de populate mais chargeable en module Python (utilisé par Phase 3). |

**Plan de vérification** :
- [ ] `python scripts/populate_db.py` injecte ≥ 20 AO sans erreur 404.
- [ ] `python -c "import sqlite3; print(sqlite3.connect('ged.db').execute('SELECT count(*) FROM appels_offres').fetchone()[0])"` → ≥ 20.

---

## T1.8 — Supprimer les doublons de structure

**Description & objectif** : éviter la confusion entre `backend/init_db.py` et `scripts/init_db.py` (déjà supprimé en T0.8). Supprimer aussi le frontend vanilla.

**Modifications** :

| Module | Action | Détail |
|---|---|---|
| `repo` | `CMD` | `git rm -r frontend/` (vanilla) |
| `repo` | `MODIFY` | `README.md` : pointer exclusivement sur `frontend-react/` |
| `repo` | `MODIFY` | `docker-compose.yml` : retirer la mention du frontend vanilla (s'il y en a une) |

**Plan de vérification** :
- [ ] `ls frontend/` retourne `No such file or directory`.
- [ ] `grep -rn "frontend/" backend/main.py` → ne référence plus que `frontend-react/dist/`.

---

## T1.9 — Mettre à jour `schemas.py`

**Description & objectif** : aligner les schémas Pydantic avec les nouveaux champs du modèle.

**Modifications** :

| Module | Action | Détail |
|---|---|---|
| `backend` | `MODIFY` | `backend/schemas.py` : ajouter champs Pydantic pour `montant`, `date_parution`, `date_limite`, `reference`, `region`, et les filtres (`MarcheFilter`). |

**Plan de vérification** :
- [ ] `python -c "from backend.schemas import MarcheFilter; m=MarcheFilter(ville='Casablanca'); print(m)"` ne lève pas d'erreur.

---

## T1.10 — Tests d'intégration repository

**Description & objectif** : valider que le repository fonctionne avec une base SQLite en mémoire.

**Modifications** :

| Module | Action | Détail |
|---|---|---|
| `tests` | `MODIFY` | `tests/conftest.py` : ajouter fixture `db_session` qui crée un engine SQLite en mémoire + `Base.metadata.create_all`. |
| `tests` | `NEW` | `tests/test_repository.py` (≥ 5 tests) :<br>- `test_create_marche`<br>- `test_get_by_numero`<br>- `test_list_with_filters`<br>- `test_search_fts`<br>- `test_kpis_aggregation` |

**Plan de vérification** :
- [ ] `pytest tests/test_repository.py -v` → 5 passed.
- [ ] Coverage de `backend/repository.py` ≥ 70 % : `pytest --cov=backend.repository --cov-report=term-missing tests/test_repository.py`.

---

## T1.11 — Tests de non-régression des endpoints

**Description & objectif** : s'assurer que les 19 endpoints existants retournent toujours la bonne forme de réponse.

**Modifications** :

| Module | Action | Détail |
|---|---|---|
| `tests` | `NEW` | `tests/test_api_endpoints.py` (≥ 10 tests) : un test par endpoint avec assertions sur le JSON retourné (statut HTTP + clés). |

**Plan de vérification** :
- [ ] `pytest tests/test_api_endpoints.py -v` → ≥ 10 passed.
- [ ] Aucun endpoint ne retourne 500.

---

## ✅ Critères de sortie de la Phase 1

- [ ] `grep -rn "sqlite3" backend/` → vide.
- [ ] `uvicorn backend.main:app` démarre et `GET /api/v1/ged/appels-offres` retourne les AO seedés.
- [ ] `alembic upgrade head` puis `alembic downgrade base` puis `alembic upgrade head` : schéma identique.
- [ ] `pytest tests/` → 100 % vert (≥ 17 tests).
- [ ] Coverage `backend/repository.py` ≥ 70 %.

**Effort total** : 1,5 jour ouvré.
