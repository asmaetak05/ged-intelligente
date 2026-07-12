# Phase 6 — ML baseline (TF-IDF + SVM)

> **Effort** : 1,5 journée · **Risque** : moyen · **Pré-requis** : Phases 1–3 (≥ 30 AO en BDD)

---

## T6.1 — Module features

**Description & objectif** : centraliser la vectorisation TF-IDF.

**Modifications** :

| Module | Action | Détail |
|---|---|---|
| `ml` | `MODIFY` | `ml/features.py` :<br>1. `build_text(marche) -> str` : concatène `objet`, `methode_notation`, `maitre_ouvrage`, première ligne de `profils_exiges`.<br>2. `vectorize(corpus: List[str]) -> Tuple[TfidfVectorizer, scipy.sparse]` :<br>   - `TfidfVectorizer(max_features=5000, ngram_range=(1,2), stop_words=stopwords.words('french'))`<br>3. `class FeatureExtractor` : encapsule fit/transform, `save(path)`, `load(path)`. |

**Plan de vérification** :
- [ ] `python -c "from ml.features import FeatureExtractor; fe = FeatureExtractor(); fe.fit_transform(['route nationale', 'fournitures informatiques']); print(fe.vectorizer.get_feature_names_out()[:5])"` ne lève pas d'exception.

---

## T6.2 — Script d'entraînement

**Description & objectif** : produire un modèle sérialisé + métriques.

**Modifications** :

| Module | Action | Détail |
|---|---|---|
| `ml` | `MODIFY` | `ml/train_classifier.py` :<br>1. Charge les AO depuis la BDD (via `backend.repository.MarcheRepository.list()`).<br>2. Filtre les AO avec `categorie_marche` non nul.<br>3. Split 80/20 stratifié.<br>4. `TfidfVectorizer` + `LinearSVC()` (ou `SVC(probability=True, kernel='linear')`).<br>5. Métriques : accuracy, F1 macro, classification report.<br>6. Sérialise : `joblib.dump((vectorizer, model), 'ml/models/classifier.joblib')`.<br>7. Sérialise aussi la liste des classes dans `ml/models/classes.json`.<br>8. Si < 10 exemples par classe, lève une erreur claire. |
| `ml` | `MODIFY` | `ml/models/.gitkeep` (déjà vide, vérifier que `classifier.joblib` est gitignoré). |
| `repo` | `MODIFY` | `.gitignore` : ajouter `ml/models/*.joblib` et `ml/models/*.pkl`. |

**Plan de vérification** :
- [ ] `python -m ml.train_classifier` affiche accuracy + F1 et crée `ml/models/classifier.joblib`.
- [ ] `ls -lh ml/models/classifier.joblib` → taille > 1 Ko.
- [ ] Sans assez de données, affiche un message clair d'erreur.

---

## T6.3 — Script d'inférence

**Description & objectif** : charger le modèle et prédire.

**Modifications** :

| Module | Action | Détail |
|---|---|---|
| `ml` | `MODIFY` | `ml/predict.py` :<br>1. `class Classifier` :<br>   - `__init__(model_path='ml/models/classifier.joblib')`<br>   - `predict(text: str) -> Tuple[str, float]` (catégorie + confidence)<br>2. Singleton : `get_classifier()` charge paresseusement. |
| `ml` | `MODIFY` | `ml/predict.py` : ajouter `predict_for_marche(marche: Marche) -> dict` qui appelle `build_text` puis `predict`. |

**Plan de vérification** :
- [ ] `python -c "from ml.predict import get_classifier; c = get_classifier(); print(c.predict('Construction d\\'une route'))"` retourne une catégorie.

---

## T6.4 — Brancher l'inférence sur l'API

**Description & objectif** : à chaque création d'AO, générer automatiquement un `MlInsight`.

**Modifications** :

| Module | Action | Détail |
|---|---|---|
| `backend` | `MODIFY` | `backend/tasks.py` : dans `process_document_async`, après insertion du `Marche`, appeler `ml.predict.predict_for_marche(marche)` et insérer un `MlInsight` :<br>```python<br>category, confidence = classifier.predict(text)<br>insight = MlInsight(<br>    marche_id=marche.id,<br>    predicted_categorie=category,<br>    classification_confidence=confidence,<br>    is_anomaly=False,<br>    anomaly_score=None<br>)<br>db.add(insight); db.commit()<br>``` |
| `backend` | `MODIFY` | `backend/main.py` : `POST /api/v1/ged/appels-offres` (synchronisé) appelle aussi la prédiction si `ml_classifier` est dispo. |
| `backend` | `MODIFY` | `backend/main.py` : `GET /api/v1/ml/predictions/{marche_id}` retourne le `MlInsight` réel (déjà codé en ligne 270, vérifier qu'il est alimenté). |

**Plan de vérification** :
- [ ] Après création d'un AO, `SELECT count(*) FROM ml_insights` augmente de 1.
- [ ] `GET /api/v1/ml/predictions/{id}` retourne une catégorie et une confidence réelles.

---

## T6.5 — Détection d'anomalies simple

**Description & objectif** : compléter la promesse ML avec un second modèle (anomalies sur les montants).

**Modifications** :

| Module | Action | Détail |
|---|---|---|
| `ml` | `MODIFY` | `ml/anomaly.py` :<br>1. Charge les AO avec `montant` et `delai_execution_mois` non nuls.<br>2. `IsolationForest(contamination=0.1)` (scikit-learn).<br>3. Fit + `predict` + `decision_function`.<br>4. Sérialise `ml/models/anomaly_detector.joblib`.<br>5. `class AnomalyDetector` avec `predict(marche) -> (is_anomaly: bool, score: float)`. |
| `backend` | `MODIFY` | `backend/tasks.py` : après prédiction de catégorie, insérer `(is_anomaly, anomaly_score)` dans `MlInsight`. |
| `backend` | `MODIFY` | `backend/main.py` : `GET /api/v1/ml/anomalies` retourne la liste des `MlInsight` où `is_anomaly=True`. |

**Plan de vérification** :
- [ ] Avec 30+ AO, `IsolationForest` détecte 2–4 anomalies.
- [ ] `GET /api/v1/ml/anomalies` retourne la liste.
- [ ] Le frontend `PredictorML.jsx` affiche les anomalies.

---

## T6.6 — Endpoint de ré-entraînement réel

**Description & objectif** : remplacer le `retrain` mocké par un vrai ré-entraînement.

**Modifications** :

| Module | Action | Détail |
|---|---|---|
| `backend` | `MODIFY` | `backend/main.py` : `POST /api/v1/ml/retrain` lance `subprocess.Popen(['python', '-m', 'ml.train_classifier'])` et stocke le PID dans un fichier `ml/models/_last_training.pid`. |
| `backend` | `MODIFY` | `backend/main.py` : `GET /api/v1/ml/retrain/status` lit le PID et vérifie s'il est encore vivant. |

**Plan de vérification** :
- [ ] `POST /api/v1/ml/retrain` retourne `{"started": true, "pid": 12345}`.
- [ ] 30 s après, `ml/models/classifier.joblib` a un nouveau mtime.
- [ ] `GET /api/v1/ml/retrain/status` retourne `{"running": false, "last_trained_at": "..."}`.

---

## T6.7 — Notebook de démonstration

**Description & objectif** : un notebook lisible par le jury montrant entraînement + évaluation.

**Modifications** :

| Module | Action | Détail |
|---|---|---|
| `ml` | `NEW` | `ml/notebook_demo.ipynb` (5 cellules) :<br>1. **Intro** (markdown) : contexte, choix TF-IDF + LinearSVC<br>2. **Chargement** (code) : `from ml.train_classifier import load_dataset`<br>3. **Vectorisation** (code) : `FeatureExtractor` + visualisation matrice TF-IDF (optionnel)<br>4. **Entraînement** (code) : fit + métriques + confusion matrix (sklearn + seaborn)<br>5. **Inférence** (code) : prédire 3 AO et afficher résultats |

**Plan de vérification** :
- [ ] `jupyter nbconvert --to notebook --execute ml/notebook_demo.ipynb` s'exécute sans erreur.
- [ ] Le notebook HTML/PDF produit est lisible.

---

## T6.8 — Tests ML

**Description & objectif** : valider que le pipeline ML tourne de bout en bout.

**Modifications** :

| Module | Action | Détail |
|---|---|---|
| `tests` | `NEW` | `tests/test_ml.py` (≥ 5 tests) :<br>- `test_feature_extractor_fit_transform`<br>- `test_classifier_train_small_dataset` (10 AO factices)<br>- `test_classifier_predict_returns_category`<br>- `test_anomaly_detector`<br>- `test_insight_created_on_marche_insert` |
| `ml` | `MODIFY` | `ml/train_classifier.py` : exposer `load_dataset()` et `build_model()` pour les tests (factorisation). |

**Plan de vérification** :
- [ ] `pytest tests/test_ml.py -v` → 5 passed.
- [ ] `pytest --cov=ml --cov-report=term-missing` ≥ 60 %.

---

## ✅ Critères de sortie de la Phase 6

- [ ] `python -m ml.train_classifier` produit `ml/models/classifier.joblib` + métriques.
- [ ] `python -m ml.anomaly` (ou fonction équivalente) produit `ml/models/anomaly_detector.joblib`.
- [ ] `MlInsight` est créé automatiquement à chaque ingestion.
- [ ] `GET /api/v1/ml/predictions/{id}` retourne une prédiction réelle.
- [ ] `GET /api/v1/ml/anomalies` retourne une liste non vide.
- [ ] `POST /api/v1/ml/retrain` lance un vrai ré-entraînement.
- [ ] Le notebook `ml/notebook_demo.ipynb` s'exécute sans erreur.
- [ ] `pytest tests/test_ml.py` → 5/5.

**Effort total** : 1,5 jour ouvré.
