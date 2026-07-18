# Tickets d'implémentation — GED Intelligente

> Ce dossier contient, **phase par phase**, les tickets d'implémentation détaillés.
> Chaque ticket suit le format :
>
> - **Description & objectif** — ce qu'il faut faire et pourquoi
> - **Modifications à apporter** — classées par **module** et par **action** :
>   - `NEW` = nouveau fichier
>   - `MODIFY` = modification d'un fichier existant
>   - `CMD` = commande shell à exécuter
> - **Plan de vérification** — commandes + assertions à passer pour valider

## Sommaire

| Phase | Fichier | Titre | Effort |
|---|---|---|---|
| 0 | [phase-00-fondations.md](./phase-00-fondations.md) | Fondations & alignement | ½ j |
| 1 | [phase-01-unification-bdd.md](./phase-01-unification-bdd.md) | Unification de la couche données | 1,5 j |
| 2 | [phase-02-pipeline-ingestion.md](./phase-02-pipeline-ingestion.md) | Pipeline d'ingestion bout-en-bout | 1,5 j |
| 3 | [phase-03-dataset-demo.md](./phase-03-dataset-demo.md) | Données réelles & dataset de démo | 1 j |
| 4 | [phase-04-dashboard-kpis.md](./phase-04-dashboard-kpis.md) | Dashboard décisionnel | 1,5 j |
| 5 | [phase-05-page-detail-recherche.md](./phase-05-page-detail-recherche.md) | Page détail document & recherche | 1 j |
| 6 | [phase-06-ml-baseline.md](./phase-06-ml-baseline.md) | ML baseline | 1,5 j |
| 7 | [phase-07-tests-qualite.md](./phase-07-tests-qualite.md) | Tests & qualité | 1 j |
| 8 | [phase-08-documentation-livrables.md](./phase-08-documentation-livrables.md) | Documentation & livrables | 1,5 j |
| 9 | [phase-09-polish-soutenance.md](./phase-09-polish-soutenance.md) | Polish final & soutenance | ½ j |

## Légende des actions

| Code | Signification |
|---|---|
| `NEW` | Création d'un nouveau fichier |
| `MODIFY` | Modification d'un fichier existant |
| `CMD` | Commande shell (installation, exécution, lint, etc.) |

## Légende des modules

| Module | Chemin racine |
|---|---|
| `backend` | `backend/` |
| `ingestion` | `ingestion/` |
| `ocr` | `ocr/` |
| `nlp` | `nlp/` |
| `ml` | `ml/` |
| `search` | `search/` |
| `frontend` | `frontend-react/` (vanilla `frontend/` est à supprimer) |
| `scripts` | `scripts/` |
| `tests` | `tests/` |
| `alembic` | `alembic/` |
| `data` | `data/` |
| `docs` | `docs/` |
| `repo` | racine du dépôt (`.gitignore`, `requirements.txt`, etc.) |
