# Architecture Backend & Base de Données

## 1. API Restful avec FastAPI
L'infrastructure serveur est propulsée par **FastAPI** (Python), choisi pour sa rapidité (Asynchrone) et sa génération automatique de documentation (Swagger UI).

- **Architecture 3-Tiers** : Séparation stricte entre les Routes (`main.py`), les Modèles de Données (`models.py`) et la Logique Métier.
- **Endpoints Clés** :
  - `/api/v1/ged/documents/upload` : Ingestion des documents.
  - `/api/v1/analytics/*` : Fourniture des KPIs et données statistiques pour le Dashboard.
  - `/api/v1/ged/search` : Recherche sémantique FTS.

## 2. Modélisation de la Base de Données
Le projet utilise **SQLAlchemy** comme ORM pour gérer la base de données. L'architecture supporte un **Mode Hybride** :

### A. Mode Production (PostgreSQL + Docker)
- Utilisation de colonnes natives PostgreSQL comme `ARRAY` et `TSVECTOR`.
- Création d'index **GIN (Generalized Inverted Index)** pour des recherches plein texte (Full Text Search) ultrarapides.
- Triggers SQL gérant la vectorisation des mots automatiquement lors des `INSERT`.

### B. Mode Dégradé / POC (SQLite)
- Pour simplifier le déploiement local sans Docker, le système bascule intelligemment sur `ged.db` (SQLite).
- L'API utilise des requêtes SQL natives adaptées pour continuer à fournir de la donnée au Frontend sans planter.
