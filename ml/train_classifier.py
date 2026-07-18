import os
import joblib
import pandas as pd
from sklearn.svm import SVC
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sqlalchemy.orm import Session
from sqlalchemy import create_engine

# Import local modules
from ml.features import get_tfidf_vectorizer, extract_text_feature
from backend.models import Marche
from backend.database import DATABASE_URL, engine

MODELS_DIR = os.path.join(os.path.dirname(__file__), "models")
CLASSIFIER_PATH = os.path.join(MODELS_DIR, "classifier.joblib")

def train_category_classifier(db_url=DATABASE_URL):
    os.makedirs(MODELS_DIR, exist_ok=True)
    
    # Load data from DB
    eng = create_engine(db_url)
    with Session(eng) as session:
        marches = session.query(Marche).filter(Marche.categorie_prestation.isnot(None)).all()
        
    if len(marches) < 5:
        print("Pas assez de données pour entraîner le modèle (min 5).")
        return False
        
    X = [extract_text_feature(m) for m in marches]
    y = [m.categorie_prestation.value for m in marches]
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42) if len(X) >= 10 else (X, X, y, y)
    
    pipeline = Pipeline([
        ('tfidf', get_tfidf_vectorizer()),
        ('clf', SVC(probability=True, kernel='linear', random_state=42))
    ])
    
    pipeline.fit(X_train, y_train)
    
    score = pipeline.score(X_test, y_test)
    print(f"Modèle entraîné sur {len(X_train)} échantillons. Précision de test : {score:.2f}")
    
    joblib.dump(pipeline, CLASSIFIER_PATH)
    print(f"Modèle sauvegardé dans {CLASSIFIER_PATH}")
    return True

if __name__ == "__main__":
    train_category_classifier()
