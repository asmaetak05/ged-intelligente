import re

def extract_agrement(text_clean):
    """
    NLP-03: Extrait les agréments ministériels exigés (ex: D9, D12).
    """
    agrement_match = re.search(
        r"agr[ée]ments?\s+(?:exig[ée]s?\s+)?(?:de\s+classe\s+)?\b([A-Z][0-9]{1,2})\b", 
        text_clean, 
        re.IGNORECASE
    )
    if agrement_match:
        return {
            "value": agrement_match.group(1).upper(),
            "source": "regex",
            "score": 0.8,
            "snippet": agrement_match.group(0)
        }
    return None
