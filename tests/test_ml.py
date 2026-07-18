import pytest
from ml.features import extract_text_feature
from backend.models import Marche, CategorieMarche

def test_extract_text_feature():
    m = Marche(titre_projet="Construction", organisme_acheteur="Ministère")
    feat = extract_text_feature(m)
    assert feat == "construction ministère"
    
def test_ml_predict(monkeypatch):
    import ml.predict
    import numpy as np
    
    # Mock load_model to return a dummy model
    class DummyModel:
        classes_ = ["Travaux", "Services"]
        def predict_proba(self, X):
            return np.array([[0.8, 0.2]])
            
    monkeypatch.setattr(ml.predict, "load_model", lambda: DummyModel())
    
    cat, prob = ml.predict.predict_category("Test texte")
    assert cat == "Travaux"
    assert prob == 0.8

def test_ml_anomaly():
    from ml.anomaly import detect_anomalies
    from backend.database import Base
    from sqlalchemy import create_engine
    import os
    
    db_path = "test_ml_anomaly.db"
    db_url = f"sqlite:///{db_path}"
    eng = create_engine(db_url)
    Base.metadata.create_all(eng)
    
    try:
        # Assuming the db contains nothing in tests by default, or < 5 items
        anomalies = detect_anomalies(db_url)
        assert anomalies == []
    finally:
        eng.dispose()
        if os.path.exists(db_path):
            try:
                os.remove(db_path)
            except Exception:
                pass
