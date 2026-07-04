# GED Intelligente avec Analyse Prédictive des Marchés Publics
## Guide de Stage — Plan d'Exécution sur 8 Semaines

**Contexte :** Stage PFA (2 mois) — DSI du Ministère de l'Équipement et de l'Eau du Maroc  
**Profil :** Étudiante en Génie Informatique (Data Science)  
**Source de données :** [appels-offres.equipement.gov.ma](http://appels-offres.equipement.gov.ma/recherche/criteres.aspx) — Archives à partir de 2025  
**Date de rédaction :** Juillet 2026

---

## 1. Résumé du Projet

### 1.1 Problématique
Les appels d'offres et marchés publics du Ministère de l'Équipement et de l'Eau sont publiés sous forme de documents PDF (souvent scannés) sur un portail web. Ces données sont **non structurées**, **non indexées** et **difficilement exploitables** pour l'analyse décisionnelle.

### 1.2 Objectif
Construire une **plateforme GED (Gestion Électronique des Documents) intelligente** capable de :
1. **Collecter** automatiquement les archives d'appels d'offres (à partir de 2025)
2. **Extraire** le texte des PDF via OCR (Tesseract/PaddleOCR)
3. **Structurer** les informations clés (référence, objet, montant, dates, organisme, etc.)
4. **Stocker** dans une base de données relationnelle (PostgreSQL)
5. **Rechercher** via une API REST (FastAPI) et une interface web (React)
6. **Visualiser** via des dashboards BI (KPIs, tendances, cartographie)
7. **Expérimenter** des modèles ML (classification, estimation indicative)

### 1.3 Philosophie clé : MVP avant tout
> **Le succès du stage ne dépend pas du nombre de modules, mais de la démonstration d'une chaîne complète et fonctionnelle.**

Le périmètre initial est volontairement réduit pour 8 semaines. Le ML reste **expérimental** et **indicatif** — jamais présenté comme un système de décision automatique.

---

## 2. Architecture Cible (MVP)

```
┌─────────────────────────────────────────────────────────────────────┐
│  SOURCE : Portail appels-offres.equipement.gov.ma                   │
│  └── Archives ZIP (PDF scannés + natifs) depuis 2025                │
└──────────────────┬──────────────────────────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────────────────────────┐
│  LAYER 1 — COLLECTE & OCR                                         │
│  ├── Scraping Python (requests + BeautifulSoup)                     │
│  ├── Téléchargement des archives ZIP                                │
│  ├── Extraction ZIP → PDF                                           │
│  ├── Extraction texte directe (PyMuPDF / pdfplumber)                │
│  └── OCR Tesseract (français + arabe) pour les PDF scannés          │
└──────────────────┬──────────────────────────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────────────────────────┐
│  LAYER 2 — STRUCTURATION & ETL                                    │
│  ├── Nettoyage et normalisation du texte OCR                        │
│  ├── Extraction des entités (regex + spaCy)                       │
│  └── Insertion structurée en PostgreSQL                           │
└──────────────────┬──────────────────────────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────────────────────────┐
│  LAYER 3 — API & RECHERCHE                                        │
│  ├── FastAPI + SQLAlchemy + Pydantic                              │
│  ├── Recherche full-text PostgreSQL (FTS)                         │
│  └── Documentation Swagger auto-générée                           │
└──────────────────┬──────────────────────────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────────────────────────┐
│  LAYER 4 — FRONTEND / BI / ML                                     │
│  ├── Interface GED : React + Vite + Tailwind                      │
│  ├── Dashboard BI : Recharts + indicateurs clés                   │
│  └── ML expérimental : scikit-learn (classification / estimation)   │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 3. Stack Technique Recommandée

| Couche | Technologie | Justification |
|--------|-------------|---------------|
| **Langage** | Python 3.11+ | Standard data science, riche écosystème |
| **Scraping** | requests, BeautifulSoup, Scrapy | Pages statiques ASP.NET du portail |
| **OCR** | Tesseract 5.x (fra, ara, eng) | Gratuit, robuste, support bilingue fr/ar |
| **PDF natif** | PyMuPDF, pdfplumber | Extraction rapide des PDF textuels |
| **NLP** | spaCy (fr_core_news_md), regex, dateparser | Extraction d'entités et normalisation |
| **Base de données** | PostgreSQL 16 | Structuré, FTS intégré, JSONB flexible |
| **API** | FastAPI, SQLAlchemy, Alembic | Auto-documentation, typage, migrations |
| **Frontend** | React, Vite, Tailwind, Axios | Interface moderne et démontrable |
| **BI** | Recharts, Plotly | Graphiques interactifs intégrés au frontend |
| **ML** | scikit-learn, XGBoost, pandas, joblib | Baseline robuste et interprétable |
| **DevOps** | Docker Compose, Git, pytest, black | Reproductibilité et qualité du code |

---

## 4. Planning Détaillé sur 8 Semaines

### Semaine 1 — Cadrage, Environnement & Dataset Pilote
**Objectif :** Valider les données avant de coder. Prouver que l'extraction est possible.

| Jour | Tâche | Livrable |
|------|-------|----------|
| **J1** | Explorer manuellement le portail. Identifier les types de documents, les filtres, la pagination. Télécharger 5-10 archives ZIP manuellement. | Notes d'exploration + échantillon de ZIP |
| **J2** | Installer l'environnement : Python 3.11, Node.js 20, Docker Desktop, Git, Tesseract (fra+ara), Poppler. | Environnement validé (checklist) |
| **J3** | Créer le repo Git et la structure du projet (monorepo). Initialiser Docker Compose (PostgreSQL). | Repo Git + `docker-compose.yml` fonctionnel |
| **J4** | Tester l'extraction : dézipper les archives, tester PyMuPDF sur les PDF natifs, tester Tesseract sur les PDF scannés. | Rapport qualité OCR (natif vs scanné) |
| **J5** | Définir le dictionnaire de données V1. Rédiger la note de décision. Réunion de validation avec l'encadrant. | Dictionnaire de données + note de décision signée |

**Livrables clés de la semaine :**
- Repo Git structuré
- Environnement technique validé
- 30-50 documents collectés (même manuellement)
- Décision sur la méthode d'extraction (OCR ou texte direct)

---

### Semaine 2 — Collecte Automatique & Pipeline OCR V1
**Objectif :** Automatiser le téléchargement et traiter le premier batch de documents.

| Jour | Tâche | Livrable |
|------|-------|----------|
| **J1-J2** | Développer le scraper Python : navigation du formulaire de recherche, pagination, récupération des liens ZIP. | Script `scraper.py` fonctionnel |
| **J3** | Pipeline de téléchargement : télécharger les archives ZIP, les stocker dans `data/raw/`, logger les métadonnées. | Dataset brut de 50+ documents |
| **J4** | Pipeline OCR V1 : dézipper → détecter natif/scanné → extraire texte (PyMuPDF ou Tesseract) → stocker dans `data/processed/text/`. | Pipeline OCR V1 + rapport qualité |
| **J5** | Comparer Tesseract vs PaddleOCR (si temps disponible). Documenter les taux de réussite. | Rapport comparatif OCR |

**Points d'attention identifiés :**
- Les fichiers du portail sont des **archives ZIP** (pas des PDF directement)
- Une majorité de PDF sont **scannés** (image) → OCR obligatoire
- Certains PDF sont **natifs** (texte sélectionnable) → extraction directe plus rapide
- Le site utilise probablement des postbacks ASP.NET → analyser le HTML avec F12/Network

---

### Semaine 3 — Structuration NLP & Stockage
**Objectif :** Transformer le texte brut en données structurées et les stocker proprement.

| Jour | Tâche | Livrable |
|------|-------|----------|
| **J1** | Définir le schéma SQL final (tables `documents`, `marches`, `ocr_results`, `extraction_results`). Créer les tables avec Alembic. | Schéma SQL versionné |
| **J2** | Développer les extracteurs NLP : regex pour montants, dates, références ; spaCy pour objets et organismes. | Module `nlp/extractor.py` |
| **J3** | Structurer les données en JSON normalisé (un fichier par document). Valider avec Pydantic. | 50+ fichiers JSON structurés |
| **J4** | Pipeline ETL : insertion en PostgreSQL avec gestion des doublons, des NULL et des erreurs. | Base de données peuplée |
| **J5** | Créer les index PostgreSQL (FTS, trigrammes) pour la recherche. | Index de recherche opérationnels |

**Champs obligatoires à extraire :**
| Champ | Priorité | Méthode |
|-------|----------|---------|
| Référence / N° d'ordre | Obligatoire | Regex + scraping |
| Objet du marché | Obligatoire | NLP + regex |
| Organisme acheteur | Obligatoire | Règles + spaCy |
| Catégorie / Type | Obligatoire | Scraping + classification simple |
| Date de publication | Obligatoire | Scraping + dateparser |
| Date limite | Obligatoire | Scraping + dateparser |
| Montant estimé | Important | Regex + normalisation MAD |
| Lieu / Région | Important | Règles + normalisation |
| Caution | Si disponible | Regex |

---

### Semaine 4 — Backend API & Recherche
**Objectif :** Rendre les données accessibles via une API REST documentée.

| Jour | Tâche | Livrable |
|------|-------|----------|
| **J1** | Initialiser FastAPI, SQLAlchemy, Pydantic. Créer les modèles et schémas. | Projet FastAPI structuré |
| **J2** | Endpoints CRUD : documents, marchés, recherche par filtres (date, ville, organisme, montant). | API CRUD fonctionnelle |
| **J3** | Recherche full-text PostgreSQL : endpoint `/search?q=...` avec classement par pertinence. | Recherche textuelle opérationnelle |
| **J4** | Endpoint `/stats` pour les agrégations BI (comptes, sommes, moyennes). | API analytique |
| **J5** | Tests API avec pytest. Documentation Swagger. | Suite de tests + Swagger UI |

---

### Semaine 5 — Interface GED (Frontend)
**Objectif :** Construire l'interface utilisateur pour consulter et rechercher les documents.

| Jour | Tâche | Livrable |
|------|-------|----------|
| **J1** | Initialiser React + Vite + Tailwind. Configurer Axios pour l'API. | Projet React fonctionnel |
| **J2** | Page liste des documents : tableau avec pagination, filtres (date, ville, organisme, type). | Liste des marchés fonctionnelle |
| **J3** | Page détail d'un document : affichage des métadonnées + texte OCR brut. | Vue détail complète |
| **J4** | Barre de recherche full-text avec auto-complétion et surlignage. | Recherche intégrée à l'UI |
| **J5** | Tests utilisateur, corrections UI/UX. | Interface stable et démontrable |

---

### Semaine 6 — Dashboard BI & ML Baseline
**Objectif :** Valoriser les données avec des indicateurs et un premier modèle ML.

| Jour | Tâche | Livrable |
|------|-------|----------|
| **J1** | Concevoir les 6 KPIs minimum (voir liste ci-dessous). | Spécifications BI validées |
| **J2** | Développer le dashboard React avec Recharts : graphiques temporels, répartition par catégorie, top organismes. | Dashboard BI interactif |
| **J3** | Feature engineering pour le ML : préparation du dataset (type, domaine, montant, délais). | Dataset ML propre |
| **J4** | Modèle baseline : classification du type de marché (Travaux/Fournitures/Services/Études) avec TF-IDF + SVM. | Modèle de classification + métriques |
| **J5** | Modèle optionnel : estimation indicative du montant (régression) ou détection de valeurs atypiques. | Notebook ML + limitations documentées |

**KPIs obligatoires du dashboard :**
1. Volume de marchés par période (mois/trimestre)
2. Montant total estimé par période et par catégorie
3. Répartition par type de marché (Travaux, Fournitures, Services, Études)
4. Top 10 organismes acheteurs
5. Délai moyen entre publication et date limite
6. Taux de qualité OCR (documents réussis vs échoués)

**Règle d'or pour le ML :**
- Présenter les résultats comme **"aide à l'analyse"**, jamais comme "prédiction fiable"
- Documenter les limites : taille du dataset, qualité des PDF, biais potentiels
- Éviter toute formulation suggérant une détection de fraude

---

### Semaine 7 — Intégration, Tests & Pipeline Complet
**Objectif :** Faire fonctionner la chaîne de bout en bout et stabiliser.

| Jour | Tâche | Livrable |
|------|-------|----------|
| **J1** | Intégration OCR → NLP → DB → API → Frontend. Détection et correction des bugs. | Pipeline bout-en-bout fonctionnel |
| **J2** | Tests d'intégration : upload d'un nouveau PDF → extraction → visualisation en temps réel. | Scénario de démo stable |
| **J3** | Préparation du jeu de démo : 5-10 documents bien choisis pour la soutenance. | Dataset de démo validé |
| **J4** | Rédaction du guide d'installation (`README.md`, `docs/installation.md`). | Documentation technique |
| **J5** | Revue de code, nettoyage, optimisation des requêtes SQL. | Code propre et documenté |

---

### Semaine 8 — Rapport, Soutenance & Livrables
**Objectif :** Produire les documents finaux et préparer une démonstration convaincante.

| Jour | Tâche | Livrable |
|------|-------|----------|
| **J1-J2** | Rédaction du rapport de stage (30-50 pages) : contexte, architecture, méthodologie, résultats, limites. | Rapport de stage complet |
| **J3** | Préparation des slides de soutenance (15-20 slides). | Présentation PowerPoint |
| **J4** | Répétition de la démo : scénario "PDF → Texte → JSON → Dashboard → ML" en 5 minutes. | Scénario de démo maîtrisé |
| **J5** | Remise des livrables : code, rapport, manuel utilisateur, documentation technique. | Livrables finaux remis |

---

## 5. Modèle de Données (Simplifié)

```sql
-- Table principale : tracabilité du document original
CREATE TABLE documents (
    id SERIAL PRIMARY KEY,
    source_url TEXT NOT NULL,
    file_path TEXT NOT NULL,
    document_type VARCHAR(100),      -- AAO, Résultat, PV, Rectificatif
    archive_name VARCHAR(255),        -- Nom du ZIP source
    status VARCHAR(30) DEFAULT 'new', -- new, ocr_done, extracted, validated
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table métier : données structurées du marché
CREATE TABLE marches (
    id SERIAL PRIMARY KEY,
    document_id INTEGER REFERENCES documents(id),
    numero_ordre VARCHAR(50),
    reference VARCHAR(100),
    titre TEXT NOT NULL,
    objet TEXT,
    organisme VARCHAR(200),
    categorie VARCHAR(100),           -- Travaux, Fournitures, Services, Études
    type_marche VARCHAR(50),          -- AO, AOR, AON, MC, MP, CONC
    activite VARCHAR(10),             -- I, II, III
    ville VARCHAR(100),
    region VARCHAR(100),
    domaine VARCHAR(200),
    qualification VARCHAR(200),
    classe VARCHAR(50),
    date_parution DATE,
    date_limite DATE,
    heure_limite TIME,
    caution_provisoire NUMERIC(15,2),
    estimation NUMERIC(15,2),
    devise VARCHAR(10) DEFAULT 'MAD',
    fournisseur_attributaire VARCHAR(200),
    statut VARCHAR(50) DEFAULT 'En cours',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table OCR : audit et comparaison des moteurs
CREATE TABLE ocr_results (
    id SERIAL PRIMARY KEY,
    document_id INTEGER REFERENCES documents(id),
    engine VARCHAR(50),               -- PyMuPDF, Tesseract, PaddleOCR
    extracted_text TEXT,
    confidence_avg NUMERIC(5,2),
    processing_time_seconds NUMERIC(6,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table extraction : traçabilité champ par champ
CREATE TABLE extraction_results (
    id SERIAL PRIMARY KEY,
    document_id INTEGER REFERENCES documents(id),
    field_name VARCHAR(100),        -- reference, objet, montant, date...
    field_value TEXT,
    confidence NUMERIC(5,2),
    method VARCHAR(50),               -- regex, spaCy, scraping, rule
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table ML : traçabilité des prédictions
CREATE TABLE ml_predictions (
    id SERIAL PRIMARY KEY,
    marche_id INTEGER REFERENCES marches(id),
    model_name VARCHAR(100),
    task VARCHAR(50),                 -- classification, estimation, anomaly
    prediction TEXT,
    score NUMERIC(5,4),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## 6. Structure du Projet (Monorepo)

```
ged-intelligente/
├── README.md
├── docker-compose.yml
├── .env.example
├── requirements.txt
│
├── docs/                          # Cahier des charges, architecture, guides
│   ├── analyse_fonctionnelle.md
│   ├── dictionnaire_donnees.md
│   ├── installation.md
│   └── rapport/
│
├── data/
│   ├── raw/                       # Archives ZIP téléchargées
│   ├── processed/
│   │   ├── text/                  # Textes OCR extraits
│   │   └── json/                  # Données structurées
│   └── samples/                   # PDF légers pour les tests
│
├── backend/
│   ├── app/
│   │   ├── api/                   # Endpoints FastAPI
│   │   ├── models/                # SQLAlchemy models
│   │   ├── schemas/               # Pydantic schemas
│   │   ├── services/              # Logique métier
│   │   └── db/                    # Connexion + migrations Alembic
│   └── Dockerfile
│
├── ingestion/
│   ├── scraper.py                 # Collecte depuis le portail
│   ├── downloader.py              # Téléchargement des ZIP
│   └── utils.py
│
├── ocr/
│   ├── extract_native.py          # PyMuPDF / pdfplumber
│   ├── extract_ocr.py             # Tesseract pipeline
│   └── preprocess.py              # Prétraitement image
│
├── nlp/
│   ├── extract_entities.py        # Extraction champs clés
│   ├── normalize.py               # Normalisation montants, dates
│   └── rules/                     # Regex et patterns
│
├── search/
│   └── postgres_fts.py            # Configuration Full-Text Search
│
├── ml/
│   ├── notebooks/                 # Exploration + baseline
│   ├── models/                    # Modèles sérialisés (joblib)
│   └── features/                  # Feature engineering
│
├── frontend/
│   ├── src/
│   │   ├── pages/                 # Liste, Détail, Dashboard
│   │   ├── components/            # Tableaux, graphiques, filtres
│   │   └── api/                   # Client Axios
│   └── Dockerfile
│
└── scripts/
    ├── init_db.py
    ├── run_ocr_batch.py
    └── seed_demo.py
```

---

## 7. Checklist de Démarrage Immédiat

### Pré-requis système
- [ ] OS : Windows + WSL2 Ubuntu **ou** Linux natif
- [ ] Python 3.11+
- [ ] Node.js 20+
- [ ] Docker Desktop
- [ ] Git

### Outils OCR
- [ ] Tesseract 5.x installé
- [ ] Langues Tesseract : `fra`, `eng`, `ara` disponibles (`tesseract --list-langs`)
- [ ] Poppler (`pdftoppm`) disponible

### Vérification rapide (à exécuter dans le terminal)
```bash
git --version
docker --version
docker compose version
python --version
node --version
npm --version
tesseract --version
tesseract --list-langs
```

### Première action (Jour 1)
1. **Explorer le site** : [appels-offres.equipement.gov.ma](http://appels-offres.equipement.gov.ma/recherche/criteres.aspx)
2. **Faire une recherche** : Date parution entre 01/01/2025 et 31/12/2025
3. **Analyser avec F12** : Onglet Network → voir les requêtes POST/GET, la pagination, les liens ZIP
4. **Télécharger 5-10 archives** manuellement pour analyse
5. **Tester l'OCR** : dézipper, tester PyMuPDF (texte direct) et Tesseract (scanné)
6. **Noter les observations** : type de PDF, langue, qualité, structure du ZIP

---

## 8. Risques Principaux et Mitigation

| Risque | Probabilité | Impact | Mitigation |
|--------|-------------|--------|------------|
| **Périmètre trop large** | Critique | Critique | **MVP obligatoire** + extensions facultatives. Ne pas commencer par le ML. |
| **Dataset insuffisant** | Fort | Fort | Commencer avec 30-50 docs. Annoncer les limites dans le rapport. |
| **OCR faible sur scans** | Fort | Fort | Prétraitement image + fallback PyMuPDF. Comparer Tesseract/PaddleOCR. |
| **Scraping instable** | Moyen | Moyen | Collecte manuelle possible pour le dataset de démo. |
| **Champs non disponibles** | Moyen | Moyen | Adapter les KPIs aux données réellement présentes. |
| **Interprétation ML sensible** | Moyen | Fort | Présenter le ML comme "aide à l'analyse", jamais décision automatique. |

---

## 9. Positionnement pour la Soutenance

### L'angle à défendre
> **La valeur du projet n'est pas uniquement dans le modèle ML.** Elle est surtout dans la **transformation d'un flux documentaire public non structuré en base de données exploitable, recherchable et visualisable**. Le ML vient enrichir cette base sous forme de **preuve de concept**.

### Scénario de démo recommandé (5 minutes)
1. **Montrer le site source** : "Voici les données brutes, non structurées"
2. **Lancer le scraper** : téléchargement automatique d'une archive ZIP
3. **Montrer l'OCR** : "Ce PDF scanné devient du texte exploitable"
4. **Montrer le JSON structuré** : champs extraits (montant, date, objet)
5. **Montrer la base de données** : les données sont propres et indexées
6. **Faire une recherche** : "Tous les marchés de Casablanca en 2025"
7. **Montrer le dashboard** : KPIs et tendances
8. **Montrer le ML** : "Classification indicative du type de marché"

---

## 10. Conclusion

Ce projet est **faisable et valorisant** pour un stage de 2 mois, à condition de respecter rigoureusement l'ordre de priorité :

```
DONNÉE → EXTRACTION → STOCKAGE → RECHERCHE → DASHBOARD → ML (expérimental)
```

**La démonstration d'une chaîne complète et stable vaut mieux qu'une collection de modules incomplètes.**

Bon courage pour votre stage ! 🚀
