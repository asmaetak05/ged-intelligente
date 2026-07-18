# GED Intelligente — Plateforme de Marchés Publics

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![Python](https://img.shields.io/badge/python-3.11-blue)
![React](https://img.shields.io/badge/React-19-cyan)
![Machine Learning](https://img.shields.io/badge/ML-Scikit_Learn-orange)
![Coverage](https://img.shields.io/badge/Coverage-70%25-green)

Plateforme automatisée de **Gestion Électronique des Documents (GED)** intégrant des pipelines d'Intelligence Artificielle (Scraping, OCR, NLP, ML) conçue spécifiquement pour analyser les Appels d'Offres du Ministère de l'Équipement au Maroc.

## Fonctionnalités Clés

- 🤖 **Bot de Scraping Asynchrone** (Playwright) pour la collecte automatique des archives.
- 👁️ **Pipeline d'Extraction OCR Hybride** (PyMuPDF / Tesseract) supportant les PDF natifs et numérisés.
- 🧠 **Moteur NLP et ML** : Reconnaissance sémantique des montants (Regex/spaCy) et classification automatisée des catégories (SVM).
- 📊 **Tableau de Bord Décisionnel (BI)** : Interface moderne en React JS (Tailwind, Recharts).
- 🔎 **Recherche Sémantique (FTS)** : Indexation puissante des mots contenus dans les dizaines de pages des DCE.

## Architecture

Le projet est conçu en 4 couches indépendantes :
- `ingestion/` (L1) : Scraping et orchestration des traitements.
- `ocr/` & `nlp/` (L2) : Conversion d'image vers texte et reconnaissance des entités nommées.
- `backend/` & `ml/` (L3) : Serveur API FastAPI performant, BDD unifiée (SQLite / PostgreSQL), Algorithmes d'anomalies financières.
- `frontend-react/` (L4) : Interface Web métier.

👉 [Consulter l'architecture détaillée](docs/architecture.md).

## Démarrage Rapide

```bash
# Cloner le projet
git clone https://github.com/votre-organisation/ged-intelligente.git
cd ged-intelligente

# Activer l'environnement Python
python -m venv .venv
.venv\Scripts\Activate.ps1   # (Sous Windows)
source .venv/bin/activate    # (Sous Linux/macOS)

# Installer les dépendances backend
pip install -r requirements.txt
playwright install --with-deps chromium
python -m spacy download fr_core_news_sm

# Lancer l'API Backend
alembic upgrade head
uvicorn backend.main:app --reload

# Ouvrir un second terminal pour le frontend
cd frontend-react
npm install
npm run dev
```

👉 [Voir le Guide d'Installation complet](docs/installation.md) et le [Guide Utilisateur](docs/user_guide.md).

## Documentation et Livrables de Projet

La documentation se trouve dans le dossier `docs/` :
- `docs/Rapport_Stage.md` : Rapport complet pour soutenance.
- `docs/Slides_Soutenance.md` : Présentation détaillée par slide.
- `docs/Scenario_Demo.md` : Déroulé chronométré pour la démonstration au jury.
- `docs/realisations/` : Le détail technique, étape par étape, des différentes phases implémentées.
