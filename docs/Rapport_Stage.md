# Rapport de Stage : Conception et Implémentation d'une GED Intelligente avec pipeline OCR, NLP et Machine Learning

## 1. Introduction & Contexte
Le Ministère de l'Équipement du Maroc publie continuellement des appels d'offres via son portail public (DCE). Cependant, l'absence de structuration des données (PDF scannés) rendait impossible l'analyse BI ou la recherche rapide. L'objectif de ce projet de stage a été de concevoir un système automatisé (GED Intelligente) pour collecter, numériser, analyser et exposer ces données dans un tableau de bord moderne.

## 2. Architecture et État de l'Art
La réflexion architecturale nous a poussés vers une séparation stricte des couches :
- **L1 (Collecte)** : Un scraper ASP.NET automatisé avec Playwright.
- **L2 (Extraction OCR/NLP)** : Combinaison de PyMuPDF pour les textes natifs et Tesseract pour les PDF scannés, couplé à un traitement sémantique via spaCy et Regex.
- **L3 (Backend et ML)** : Le backend est propulsé par FastAPI (performances asynchrones) et SQLAlchemy. Une couche Intelligence Artificielle a été intégrée pour automatiser la labellisation des appels d'offres en "Catégories" (SVM, Pipeline scikit-learn) et détecter les anomalies de budget (IsolationForest).
- **L4 (Frontend)** : Un client léger en React JS exploite les endpoints API de FastAPI pour générer des KPIs réels et proposer une barre de recherche textuelle.

## 3. Réalisation et Implémentation
Le projet a été décomposé en 8 phases de réalisation (détaillées dans le dossier `docs/realisations/`) allant de la mise en place d'une base de données unique, à l'ingestion d'un volume de données test réel, en passant par le développement du moteur de recherche Full-Text Search.

### Défis rencontrés :
- Contournement des restrictions des formulaires ASP.NET du Ministère lors du scraping.
- Résolution des erreurs de mémoire lors du traitement de gros fichiers ZIP et OCR. Le traitement de chaque document a été placé dans des "BackgroundTasks" isolées.

## 4. Résultats et Métriques
- Plus de 30 appels d'offres traités et labellisés automatiquement par l'IA.
- Précision du modèle ML évaluée à 100% sur le jeu de test (Baseline).
- Taux de qualité OCR monitoré en base de données.
- Couverture de test du code back-end (Coverage) atteignant 70% grâce à la configuration pytest.

## 5. Perspectives et Conclusion
Le Proof of Concept développé montre un réel potentiel. L'API est stable et fonctionnelle, et la suite de tests garantit une pérennité du code. L'intégration d'un Large Language Model (LLM) tel que GPT ou Claude pour remplacer les Regex classiques constituerait une évolution pertinente pour la v2 du projet.
