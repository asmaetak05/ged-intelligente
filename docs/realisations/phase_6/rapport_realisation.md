# Rapport de Réalisation - Phase 6 (Machine Learning Baseline)

## Objectif
Ajouter une couche d'intelligence artificielle au projet afin de classifier automatiquement les appels d'offres en différentes catégories et détecter les valeurs potentiellement anormales.

## Actions Réalisées

1. **Classification Automatique NLP (SVM) :**
   - Création de `ml/features.py` : Extraction des caractéristiques textuelles en utilisant `TfidfVectorizer` (français).
   - Création de `ml/train_classifier.py` : Algorithme `SVC` (Support Vector Classifier) qui entraîne un modèle probabiliste sur la base de données.
   - Sérialisation du modèle avec `joblib` dans le dossier `ml/models/`.
   - Création de `ml/predict.py` : Infère une catégorie pour un appel d'offres entrant.

2. **Détection d'Anomalies Financières :**
   - Création de `ml/anomaly.py` utilisant `IsolationForest` de scikit-learn.
   - L'algorithme prend en compte le `montant`, le `delai_execution_mois` et la `caution_provisoire_mad` pour lever une alerte sur des appels d'offres atypiques.

3. **Intégration API & Backend :**
   - Modification de la route POST `/api/v1/ged/appels-offres` : Une prédiction de catégorie est générée de façon synchrone au moment où l'ingestion d'un nouveau document est complétée.
   - La prédiction est stockée dans la table `MlInsight` (modèle SQLAlchemy).
   - Ajout d'une route d'arrière-plan `POST /api/v1/ml/retrain` qui lance la détection d'anomalies et le ré-entraînement du SVM, utile à mesure que de nouveaux documents arrivent.

4. **Notebook Jupyter & Tests :**
   - Création d'un notebook interactif de démonstration `ml/notebook_demo.ipynb`.
   - Couverture par des tests unitaires fonctionnels dans `tests/test_ml.py`.

## Bilan
Le système bénéficie d'une composante ML "Baseline" rapide, robuste et directement intégrée au flux de données. La **Phase 6** est terminée avec succès.
