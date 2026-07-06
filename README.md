# Projet PFA : GED Intelligente pour les Marchés Publics

Bienvenue dans le dépôt du Projet de Fin d'Année (PFA) : une plateforme de Gestion Électronique des Documents dopée à l'Intelligence Artificielle et à l'OCR.

Ce guide décrit la procédure exacte pour configurer et lancer le projet (Backend & Frontend) sur un **nouveau poste de travail Windows, Mac ou Linux**.

---

## 🛠️ Prérequis Système

Avant de commencer, assurez-vous d'avoir installé les logiciels suivants sur votre machine :

1. **Python 3.10 ou supérieur** (Cocher "Add to PATH" lors de l'installation).
2. **Node.js (LTS - 18.x ou 20.x)** (Inclut `npm`).
3. **Tesseract OCR** (Moteur de reconnaissance de caractères) :
   - *Windows* : Télécharger depuis [UB-Mannheim](https://github.com/UB-Mannheim/tesseract/wiki). Noter le chemin d'installation (ex: `C:\Program Files\Tesseract-OCR\tesseract.exe`).
   - *Mac* : `brew install tesseract tesseract-lang`
   - *Linux* : `sudo apt-get install tesseract-ocr tesseract-ocr-fra tesseract-ocr-ara`
4. **Poppler** (Nécessaire pour convertir les PDF en images) :
   - *Windows* : Télécharger [Poppler for Windows](https://github.com/oschwartz10612/poppler-windows/releases/), extraire et ajouter le dossier `bin` aux variables d'environnement PATH.
   - *Mac* : `brew install poppler`
   - *Linux* : `sudo apt-get install poppler-utils`

---

## ⚙️ Étape 1 : Configuration du Backend (Python / FastAPI)

Le backend gère l'extraction NLP, la base de données SQLite/PostgreSQL et l'API.

1. **Ouvrir un Terminal** à la racine du projet (`ged-intelligente`).
2. **Créer un environnement virtuel Python** :
   ```bash
   python -m venv .venv
   ```
3. **Activer l'environnement virtuel** :
   - *Windows (PowerShell)* : `.\.venv\Scripts\Activate.ps1`
   - *Windows (CMD)* : `.\.venv\Scripts\activate.bat`
   - *Mac / Linux* : `source .venv/bin/activate`
4. **Installer les dépendances requises** :
   ```bash
   pip install -r requirements.txt
   ```
5. **Configuration Environnement** :
   - Copiez le fichier `.env.example` en le renommant `.env`.
   - Modifiez le chemin Tesseract dans le code (si Windows) si nécessaire dans les scripts OCR. La base de données utilisera automatiquement le fichier local `ged.db` (Mode Mock).
6. **Lancer le serveur FastAPI** :
   ```bash
   uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
   ```
   *Le serveur API est maintenant actif sur `http://127.0.0.1:8000`. Vous pouvez consulter la documentation technique de l'API sur `http://127.0.0.1:8000/docs`.*

---

## 🎨 Étape 2 : Configuration du Frontend (React / Vite)

Le frontend est l'interface utilisateur minimaliste propulsée par React et Tailwind CSS.

1. **Ouvrir un nouveau Terminal** (gardez le backend actif dans le premier terminal).
2. **Naviguer dans le dossier Frontend** :
   ```bash
   cd frontend-react
   ```
3. **Installer les dépendances Node.js** :
   ```bash
   npm install
   ```
4. **Lancer le serveur de développement Vite** :
   ```bash
   npm run dev
   ```
5. **Accéder à l'application** :
   Le terminal vous affichera une URL, généralement `http://localhost:5173/`. Cliquez dessus pour ouvrir l'interface.

---

## 📁 Architecture des Dossiers

- `backend/` : Cœur de l'API FastAPI et Modèles ORM.
- `docs/realisations/` : Documentation détaillée des modules (Ingestion, Frontend, Backend, IA).
- `frontend-react/` : Code source de l'interface utilisateur.
- `ged.db` : Base de données SQLite locale contenant les données extraites lors des tests NLP.
- `nlp/` & `ocr/` : Scripts d'intelligence artificielle et d'extraction de texte.

---

## 🚀 Fonctionnalités Opérationnelles
- **Ingestion ZIP** via Drag & Drop.
- **Tableau de Bord** analytique branché sur la donnée SQLite réelle.
- **Moteur de Recherche** des marchés publics extraits.
- **Monitoring** temps réel.

*Projet développé dans le cadre du Projet de Fin d'Année (PFA).*
