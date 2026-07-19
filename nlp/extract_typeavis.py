import re

def extract_type_avis(text_clean):
    """
    NLP-01: Extrait le type d'avis de marché (ex. Appel d'offres ouvert, restreint, concours).
    """
    type_avis_match = re.search(
        r"appel\s+d['’]?offres?\s+(ouvert|restreint|simplifié|négocié)|concours|bon\s+de\s+commande", 
        text_clean, 
        re.IGNORECASE
    )
    if type_avis_match:
        return {
            "value": type_avis_match.group(0).strip().capitalize(),
            "source": "regex",
            "score": 0.9,
            "snippet": type_avis_match.group(0)
        }
    return None
