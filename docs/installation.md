# Guide d'Installation & Déploiement

Ce document vous guidera à travers le processus d'installation de la GED Intelligente en environnement local. L'application comprend un backend Python (FastAPI), un frontend JavaScript (React/Vite) et nécessite quelques dépendances spécifiques pour le Machine Learning et le Web Scraping.

## 1. Prérequis

Avant de commencer, assurez-vous d'avoir installé les éléments suivants sur votre machine :
- **Python 3.10+**
- **Node.js 18+** et **npm**
- **Git**
- *Optionnel* : **Docker Desktop** (si vous souhaitez utiliser PostgreSQL au lieu de SQLite)

## 2. Récupération du projet

Clonez le dépôt sur votre poste de travail :
```bash
git clone https://github.com/votre-organisation/ged-intelligente.git
cd ged-intelligente
```

## 3. Configuration du Backend (Python)

Le backend gère l'API, le pipeline OCR/NLP, et les prédictions Machine Learning.

**1. Création de l'environnement virtuel**
```bash
python -m venv .venv
# Sur Windows :
.venv\Scripts\Activate.ps1
# Sur macOS / Linux :
source .venv/bin/activate
```

**2. Installation des dépendances**
```bash
pip install -r requirements.txt
# Installation de Playwright pour le scraper
playwright install --with-deps chromium
# Téléchargement du modèle linguistique français (spaCy)
python -m spacy download fr_core_news_sm
```

**3. Base de données & Migrations**
Par défaut, le système utilise **SQLite**. Si vous souhaitez utiliser **PostgreSQL**, démarrez les conteneurs Docker (`docker-compose up -d`) et modifiez la variable `DATABASE_URL` dans un fichier `.env`.

Pour initialiser ou mettre à jour la base de données :
```bash
alembic upgrade head
```

**4. Démarrage du serveur**
```bash
uvicorn backend.main:app --reload
```
Le backend sera accessible à l'adresse : [http://localhost:8000](http://localhost:8000). Vous pouvez consulter la documentation de l'API sur [http://localhost:8000/docs](http://localhost:8000/docs).

## 4. Configuration du Frontend (React)

Ouvrez un nouveau terminal et naviguez vers le dossier frontend :

```bash
cd frontend-react
# Installer les dépendances
npm install
# Démarrer le serveur de développement
npm run dev
```
Le frontend sera accessible à l'adresse : [http://localhost:5173](http://localhost:5173).

## 5. Dépannage fréquent

- **Erreur `ModuleNotFoundError: No module named 'joblib'`** : Assurez-vous d'avoir activé votre environnement virtuel et installé `scikit-learn`, `pandas` et `joblib`.
- **Tesseract non trouvé** : Si l'OCR par Tesseract échoue, assurez-vous que Tesseract-OCR est installé sur votre OS (ex: `apt-get install tesseract-ocr` sous Linux, ou le binaire sous Windows).
