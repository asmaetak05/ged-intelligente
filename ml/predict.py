import os
import joblib

MODELS_DIR = os.path.join(os.path.dirname(__file__), "models")
CLASSIFIER_PATH = os.path.join(MODELS_DIR, "classifier.joblib")

_model = None

def load_model():
    global _model
    if _model is None:
        if os.path.exists(CLASSIFIER_PATH):
            _model = joblib.load(CLASSIFIER_PATH)
    return _model

def predict_category(text: str):
    """Predict category from text and return (category, probability)."""
    model = load_model()
    if model is None:
        return None, 0.0
    
    # model is a Pipeline so we just pass the text wrapped in a list
    probs = model.predict_proba([text])[0]
    best_idx = probs.argmax()
    best_class = model.classes_[best_idx]
    
    return best_class, float(probs[best_idx])
