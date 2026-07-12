# Phase 0 — Fondations & alignement

> **Effort** : ½ journée · **Risque** : très faible · **Pré-requis** : aucun

---

## T0.1 — Isoler le refactoring sur une branche

**Description & objectif** : éviter de polluer `main` pendant le refactoring majeur, garder un historique propre et pouvoir revenir en arrière en un `git checkout main`.

**Modifications** :

| Module | Action | Détail |
|---|---|---|
| `repo` | `CMD` | `git checkout -b refactoring/unify-db-and-pipeline` |
| `repo` | `CMD` | `git push -u origin refactoring/unify-db-and-pipeline` |

**Plan de vérification** :
- [ ] `git branch` affiche la nouvelle branche active.
- [ ] `git status` est propre.

---

## T0.2 — Sauvegarder l'état actuel

**Description & objectif** : disposer d'un point de restauration en cas de régression.

**Modifications** :

| Module | Action | Détail |
|---|---|---|
| `repo` | `CMD` | `cp ged.db ged.db.bak` |
| `repo` | `CMD` | `mkdir -p _archive && git ls-files \| xargs -I{} cp --parents {} _archive/ 2>/dev/null \|\| true` |
| `repo` | `CMD` | `echo "_archive/" >> .gitignore && echo "*.bak" >> .gitignore` |

**Plan de vérification** :
- [ ] Le fichier `ged.db.bak` existe et a la même taille que `ged.db` (±32 Ko).
- [ ] `cat .gitignore` contient `_archive/` et `*.bak`.

---

## T0.3 — Documenter l'audit dans le repo

**Description & objectif** : l'audit technique produit est la **référence** pour toutes les phases suivantes. Il doit vivre dans le repo, pas dans une conversation.

**Modifications** :

| Module | Action | Détail |
|---|---|---|
| `docs` | `NEW` | `docs/AUDIT_TECHNIQUE.md` (déjà créé via le rapport d'analyse : `docs/ANALYSE_ET_PLAN_ACTION.md`) |
| `docs` | `NEW` | `docs/CHANGELOG.md` avec en-tête : `# Changelog — Projet GED Intelligente` et tableau `\| Date \| Phase \| Ticket \| Description \|` |

**Plan de vérification** :
- [ ] `docs/AUDIT_TECHNIQUE.md` est commité.
- [ ] `docs/CHANGELOG.md` est créé avec au moins une ligne pour la Phase 0.

---

## T0.4 — Formaliser la décision d'architecture BDD

**Description & objectif** : la double architecture SQLite/PostgreSQL est bloquante. Trancher **par écrit** avant de coder.

**Modifications** :

| Module | Action | Détail |
|---|---|---|
| `docs` | `MODIFY` | `docs/Note_Decision_V1.md` : ajouter une section `## Décision Phase 1 — Choix du moteur BDD` qui tranche (recommandation : SQLAlchemy avec bascule auto SQLite/PostgreSQL via `DATABASE_URL`). |
| `docs` | `MODIFY` | `docs/Note_Decision.md` : mettre à jour le statut. |

**Plan de vérification** :
- [ ] La note de décision est signée (date + auteur) et la décision est sans ambiguïté.

---

## T0.5 — Initialiser la structure de tests

**Description & objectif** : avoir un filet de sécurité dès la première modification. Sans tests, on refactore à l'aveugle.

**Modifications** :

| Module | Action | Détail |
|---|---|---|
| `tests` | `NEW` | `tests/__init__.py` (vide) |
| `tests` | `NEW` | `tests/conftest.py` avec fixture `client` (TestClient FastAPI) et `db_session` (SQLAlchemy Session) |
| `tests` | `NEW` | `tests/test_smoke.py` : 2 tests : `GET /` et `GET /api/v1/analytics/kpis` |
| `repo` | `MODIFY` | `requirements.txt` (UTF-16) : ajouter `pytest==8.3.3`, `pytest-cov==5.0.0`, `httpx==0.27.2` |
| `repo` | `CMD` | `pip install pytest==8.3.3 pytest-cov==5.0.0 httpx==0.27.2` |

**Plan de vérification** :
- [ ] `pytest tests/test_smoke.py -v` → **2 passed**.
- [ ] `pytest --co` (collect-only) liste les tests sans erreur d'import.

---

## T0.6 — Compléter `.gitignore`

**Description & objectif** : éviter de versionner des fichiers temporaires ou des secrets.

**Modifications** :

| Module | Action | Détail |
|---|---|---|
| `repo` | `MODIFY` | `.gitignore` : ajouter `.env`, `*.db-journal`, `*.db-wal`, `*.db-shm`, `__pycache__/` (racine), `.pytest_cache/`, `node_modules/`, `dist/`, `build/`, `.venv/`, `venv/` |

**Plan de vérification** :
- [ ] `cat .gitignore` contient les nouvelles entrées.
- [ ] `git status` ne montre pas de fichiers parasites (`.db-journal`, `__pycache__/`, etc.).

---

## T0.7 — Compléter `requirements.txt`

**Description & objectif** : `playwright` est utilisé par `playwright_scraper_batch.py` mais absent des dépendances. Alembic doit aussi être déclaré.

**Modifications** :

| Module | Action | Détail |
|---|---|---|
| `repo` | `MODIFY` | `requirements.txt` :<br>- Convertir en UTF-8 (lire puis réécrire)<br>- Ajouter `playwright==1.47.0`<br>- Ajouter `alembic==1.13.2`<br>- Ajouter `pytest-asyncio==0.24.0`<br>- Ajouter `python-dateutil==2.9.0.post0` (déjà présent, vérifier)<br>- Ajouter `fr-core-news-sm @ https://github.com/explosion/spacy-models/releases/download/fr_core_news_sm-3.7.0/fr_core_news_sm-3.7.0-py3-none-any.whl` |
| `repo` | `CMD` | `python -c "import re; txt=open('requirements.txt','rb').read().decode('utf-16'); open('requirements.txt','w',encoding='utf-8').write(txt)"` |
| `repo` | `CMD` | `pip install -r requirements.txt` |
| `repo` | `CMD` | `playwright install chromium` |

**Plan de vérification** :
- [ ] `file requirements.txt` → `UTF-8 Unicode text`.
- [ ] `grep -c "playwright" requirements.txt` → 1.
- [ ] `grep -c "alembic" requirements.txt` → 1.
- [ ] `python -c "import playwright; print(playwright.__version__)"` → `1.47.0`.
- [ ] `python -c "import alembic; print(alembic.__version__)"` → `1.13.2`.

---

## T0.8 — Nettoyer les fichiers orphelins

**Description & objectif** : certains fichiers sont à 0 octet et prêtent à confusion. Les supprimer pour ne pas les maintenir.

**Modifications** :

| Module | Action | Détail |
|---|---|---|
| `ingestion` | `CMD` | `rm -f ingestion/downloader.py ingestion/utils.py` |
| `scripts` | `CMD` | `rm -f scripts/init_db.py scripts/run_ocr_batch.py scripts/seed_demo.py` |
| `repo` | `CMD` | `git add -A && git status` (vérifier que seules les suppressions apparaissent) |

**Plan de vérification** :
- [ ] `ls ingestion/` ne contient plus `downloader.py` ni `utils.py`.
- [ ] `git status` ne montre pas de modifications non intentionnelles.

---

## ✅ Critères de sortie de la Phase 0

- [ ] Branche `refactoring/unify-db-and-pipeline` créée et pushed.
- [ ] `pytest tests/test_smoke.py` passe (2/2).
- [ ] `requirements.txt` en UTF-8, contient `playwright` et `alembic`.
- [ ] `docs/CHANGELOG.md` existe avec entrée Phase 0.
- [ ] `Note_Decision_V1.md` tranche la question BDD.
- [ ] `.gitignore` complet, `git status` propre.

**Effort total** : 3–4 heures.
