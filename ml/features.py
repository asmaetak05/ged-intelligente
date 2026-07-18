import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer

def extract_text_feature(marche) -> str:
    """Combine text fields for NLP classification."""
    parts = []
    if marche.titre_projet:
        parts.append(marche.titre_projet)
    if marche.organisme_acheteur:
        parts.append(marche.organisme_acheteur)
    return " ".join(parts).lower()

def get_tfidf_vectorizer():
    return TfidfVectorizer(
        stop_words=['le', 'la', 'les', 'de', 'des', 'du', 'et', 'a', 'à', 'pour', 'en', 'un', 'une'],
        max_features=1000,
        ngram_range=(1, 2)
    )
