import re

def extract_qualif(text_clean):
    """
    NLP-02: Extrait les qualifications et classifications exigées (ex: Q1, Q2, Classe 1).
    """
    qualif_match = re.search(
        r"(?:qualifications?\s+(?:et\s+classifications?\s+)?(?:exig[ée]es?\s+)?)(?:de\s+)?(?:classe|cat[ée]gorie)?\s*\b([Qq][1-6]|[A-S])\b", 
        text_clean, 
        re.IGNORECASE
    )
    if qualif_match:
        return {
            "value": qualif_match.group(1).upper(),
            "source": "regex",
            "score": 0.8,
            "snippet": qualif_match.group(0)
        }
    return None
