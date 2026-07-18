import re
from datetime import date
try:
    import dateparser
except ImportError:
    dateparser = None

def normalize_date(fr_text: str) -> date:
    if not fr_text:
        return None
    if dateparser:
        dt = dateparser.parse(fr_text, languages=['fr'])
        if dt:
            return dt.date()
    # Basic fallback
    return None

def normalize_money(fr_text: str) -> float:
    if not fr_text:
        return None
    clean = re.sub(r'[^\d,\.]', '', fr_text.replace(' ', ''))
    clean = clean.replace(',', '.')
    try:
        return float(clean)
    except:
        return None

def normalize_mois(text: str) -> int:
    if not text:
        return None
    match = re.search(r'(\d+)', text)
    if not match:
        return None
    val = int(match.group(1))
    if 'jour' in text.lower():
        return max(1, val // 30)
    if 'semaine' in text.lower():
        return max(1, val // 4)
    return val
