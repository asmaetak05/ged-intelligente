# 🎫 Lot 5 : Intelligence Artificielle & Machine Learning (Machine Learning)

## 📌 Présentation du Lot
Ce lot optimise les modèles prédictifs et les algorithmes de détection d'anomalies de la plateforme, et introduit des outils d'industrialisation (versioning de modèles, suivi des métriques).

* **Complexité globale** : Medium
* **Composants impactés** : `ml/`, `tests/test_ml.py`
* **Indépendance git** : Excellente. Tous les fichiers de modélisation sont situés dans le sous-dossier `ml/` et s'exécutent de façon modulaire.

---

## 📋 Liste des Tickets Associés

### 1. ML-01 — Réglage des Hyperparamètres du Classifieur SVM 🟠
* **Priorité** : 🟠 P1
* **Effort** : M (2 j)
* **Composant** : `ml/train_classifier.py`
* **Scénarios de test liés** : `ST-ML-001`, `ST-ML-002`
* **Description** : Le modèle actuel de classification (SVM) utilise des paramètres par défaut. Il convient de tester différentes combinaisons (C, kernel, gamma) via une validation croisée `GridSearchCV` pour maximiser la précision globale (Accuracy/F1-score) sur le jeu de données d'entraînement.

### 2. ML-02 — Optimisation de l'Isolation Forest pour la détection d'anomalies 🟠
* **Priorité** : 🟠 P1
* **Effort** : M (2 j)
* **Composant** : `ml/anomaly.py`
* **Scénarios de test liés** : `ST-ML-004`, `ST-ML-005`
* **Description** : Affiner le seuil de contamination de l'Isolation Forest pour réduire les faux positifs (marchés normaux marqués à tort comme anormaux) et calibrer les caractéristiques financières (ratio caution / montant estimé, délai d'exécution par rapport à la moyenne sectorielle).

### 3. ML-09 — Versioning des modèles ML 🟡
* **Priorité** : 🟡 P2
* **Effort** : S (1 j)
* **Composant** : `ml/predict.py`, `ml/train_classifier.py`
* **Scénarios de test liés** : `ST-ML-015`
* **Description** : Assurer la traçabilité des modèles entraînés.
* **Travail** :
  - Ajouter un numéro de version ou un horodatage dans le nom des fichiers de modèles sérialisés (ex. `svm_classifier_v1.0.0.joblib`).
  - Charger dynamiquement la dernière version active du modèle lors des prédictions en production.

---

## 🛠️ Description des Travaux
1. **Implémentation de `GridSearchCV`** :
   - Modifier `ml/train_classifier.py` pour intégrer la recherche par grille de scikit-learn.
   - Logger les meilleures métriques (Précision, Rappel, F1-score) dans un fichier de logs ML dédié.
2. **Calibration de l'Isolation Forest** :
   - Écrire un script d'évaluation de la détection d'anomalies en injectant des anomalies connues (ex. caution supérieure à 50% du montant du projet) pour valider le taux de rappel de la détection.

---

## 🧪 Critères de Validation et Non-régression
- **Taux d'erreur SVM** : S'assurer que le modèle entraîné maintient un taux d'exactitude (Accuracy) supérieur ou égal à 80% sur le jeu de test.
- **Vérification Isolation Forest** : Insérer un marché de test contenant une caution de 10 000 000 MAD pour un budget de 10 000 MAD et s'assurer qu'il est marqué comme `anomalie = True` par le script `ml/predict.py`.
- **Validation unitaire** : Exécuter `pytest tests/test_ml.py` et s'assurer que les modifications n'altèrent pas les tests unitaires existants.
