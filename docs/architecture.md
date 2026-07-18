# Architecture du Système — GED Intelligente

Ce document décrit l'architecture technique mise en œuvre pour la plateforme GED Intelligente, respectant une conception modulaire en 4 couches (L1 à L4).

## Diagramme d'Architecture Simplifié

```mermaid
graph TD
    %% Couches externes
    Portail[Portail Marchés Publics] --> |Playwright Scraper| Ingestion
    
    %% L1: Ingestion
    subgraph L1 [L1: Collecte & Extraction]
        Ingestion[API Upload / Scraper Batch]
        Extractor[Orchestrateur OCR]
        PyMuPDF[Extraction Native]
        Tesseract[Tesseract OCR Fallback]
        
        Ingestion --> Extractor
        Extractor --> PyMuPDF
        Extractor --> Tesseract
    End

    %% L2: NLP
    subgraph L2 [L2: NLP & Structuration]
        RegexEngine[Expressions Régulières]
        SpacyNLP[Modèle spaCy - fr_core_news_sm]
        
        Extractor --> RegexEngine
        Extractor --> SpacyNLP
    End

    %% L3: Backend & ML
    subgraph L3 [L3: Backend, BDD & ML]
        FastAPI[FastAPI Router]
        SQLAlchemy[ORM / Repository]
        DB[(SQLite / PostgreSQL)]
        FTS[Moteur Recherche FTS]
        SVM[Modèle ML - SVM / joblib]
        Anomaly[IsolationForest]
        
        RegexEngine --> FastAPI
        SpacyNLP --> FastAPI
        FastAPI --> SQLAlchemy
        SQLAlchemy --> DB
        DB --> FTS
        FastAPI --> SVM
        FastAPI --> Anomaly
    End

    %% L4: Frontend
    subgraph L4 [L4: BI & Interface Utilisateur]
        React[React 19 Vite]
        Tailwind[TailwindCSS / Recharts]
        
        FastAPI --> |REST JSON| React
        React --> Tailwind
    End
```

## Description des Couches

### 1. L1 - Collecte (Ingestion)
Le code responsable de l'acquisition des données brutes se trouve dans `ingestion/`. 
- Un scraper asynchrone développé en `playwright` est capable de contourner les contraintes ASP.NET du portail public et de télécharger les DCE (`.zip`).
- L'orchestrateur de l'API lit ensuite ces fichiers et passe le relai au dossier `ocr/`.
- **Double moteur d'extraction** : Si le texte du PDF n'est pas sélectionnable (document scanné), le module `PyMuPDF` échoue silencieusement et active `Tesseract` via OpenCV.

### 2. L2 - NLP (Structuration)
Le code responsable de l'analyse sémantique est dans `nlp/`.
- Un moteur Regex extrait les éléments financiers et les dates rigoureuses.
- `spaCy` est sollicité via une approche de reconnaissance d'entités (NER) pour isoler des organismes ou des villes.

### 3. L3 - BDD et Intelligence Artificielle
- **Backend** : FastAPI assure des performances asynchrones idéales pour les requêtes non bloquantes. SQLAlchemy permet une compatibilité SQLite (pour démo) et PostgreSQL (pour la production).
- **Machine Learning** : Hébergé dans `ml/`. À l'issue de l'ingestion d'un AO, le module extrait des features (TF-IDF), effectue une classification automatique (Catégorie de prestation) via un modèle Support Vector Machine (SVM) sérialisé, et une détection d'anomalies (IsolationForest) sur les données financières. 

### 4. L4 - Interface Utilisateur (Frontend)
Développée en **React**, l'interface sollicite de multiples routes API. Les KPIs sont propulsés par la librairie de visualisation graphique `Recharts`. Une logique de Polling est utilisée pour le rafraichissement du statut des tâches asynchrones d'upload.
