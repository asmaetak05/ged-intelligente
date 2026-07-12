import re
from nlp.normalize import normalize_date, normalize_money, normalize_mois
from nlp.villes_maroc import VILLES_MAROC

nlp = None

def load_spacy():
    global nlp
    if nlp is None:
        try:
            import spacy
            nlp = spacy.load('fr_core_news_sm')
        except:
            nlp = False

def extract(text: str) -> dict:
    load_spacy()
    info = {"fields": {}}
    text_clean = re.sub(r'\s+', ' ', text)
    
    def add_field(name, value, source, score, snippet):
        if value:
            # Need to format date properly if it is a datetime.date
            from datetime import date
            if isinstance(value, date):
                value = value.isoformat()
            
            info["fields"][name] = {
                "value": value,
                "source": source,
                "score": score,
                "snippet": snippet
            }

    # Objet
    objet_match = re.search(r"objet\s*(?:de\s*l['’]?appel\s*d['’]?offres)?\s*[\:\-]\s*(.*?)(?=\. |Caution|Estimation|Date)", text_clean, re.IGNORECASE)
    if objet_match:
        add_field("objet", objet_match.group(1).strip(), "regex", 0.9, objet_match.group(0))

    # Estimation
    est_match = re.search(r"estimation[^0-9]*?([\d\s\.,]+)\s*(?:dhs|mad|dirhams?)", text_clean, re.IGNORECASE)
    if est_match:
        add_field("estimation_mad", normalize_money(est_match.group(1)), "regex", 0.9, est_match.group(0))

    # Caution
    caution_match = re.search(r"caution\s+provisoire[^0-9]*?([\d\s\.,]+)\s*(?:dhs|mad|dirhams?)", text_clean, re.IGNORECASE)
    if caution_match:
        add_field("caution_mad", normalize_money(caution_match.group(1)), "regex", 0.9, caution_match.group(0))
        
    # Delai
    delai_match = re.search(r"d[ée]lai d['’]ex[ée]cution[^0-9]*?([\d]+)\s*(mois|jours|semaines)", text_clean, re.IGNORECASE)
    if delai_match:
        add_field("delai_execution_mois", normalize_mois(f"{delai_match.group(1)} {delai_match.group(2)}"), "regex", 0.9, delai_match.group(0))

    # Penalite
    penalite_match = re.search(r"p[ée]nalit[ée][^0-9]*?([\d\.,]+)\s*(?:pour\s*mille|‰|%)", text_clean, re.IGNORECASE)
    if penalite_match:
        add_field("penalite_retard_mille", normalize_money(penalite_match.group(1)), "regex", 0.8, penalite_match.group(0))

    # Date parution
    date_parution_match = re.search(r"(\d{1,2}\s+(?:janvier|février|mars|avril|mai|juin|juillet|août|septembre|octobre|novembre|décembre)\s+\d{4})", text_clean, re.IGNORECASE)
    if date_parution_match:
        add_field("date_parution", normalize_date(date_parution_match.group(1)), "regex", 0.8, date_parution_match.group(0))

    # Date limite
    date_limite_match = re.search(r"date limite.*?(\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\d{1,2}\s+\w+\s+\d{4})", text_clean, re.IGNORECASE)
    if date_limite_match:
        add_field("date_limite", normalize_date(date_limite_match.group(1)), "regex", 0.8, date_limite_match.group(0))

    # Reference
    ref_match = re.search(r"R[éé]f[éerence]*\s*:\s*(\S+)", text_clean, re.IGNORECASE)
    if ref_match:
        add_field("reference", ref_match.group(1).strip(), "regex", 0.9, ref_match.group(0))
        
    # Region / Ville
    ville_trouvee = None
    for ville in VILLES_MAROC:
        if re.search(r'\b' + ville + r'\b', text_clean, re.IGNORECASE):
            ville_trouvee = ville.capitalize()
            break
    if ville_trouvee:
        add_field("region", ville_trouvee, "lookup", 0.7, ville_trouvee)

    # Maitre ouvrage (via Spacy ORG ou regex fallback)
    mo_match = re.search(r"(?:royaume du maroc|maitre d['’]?ouvrage)\s*[:\-]?\s*(.*?)(?=\. |Objet|Le)", text_clean, re.IGNORECASE)
    if nlp:
        doc = nlp(text_clean[:2000])
        orgs = [ent.text for ent in doc.ents if ent.label_ == "ORG"]
        if orgs:
            add_field("maitre_ouvrage", orgs[0], "spacy", 0.8, orgs[0])
        elif mo_match:
            add_field("maitre_ouvrage", mo_match.group(1).strip(), "regex", 0.6, mo_match.group(0))
    elif mo_match:
        add_field("maitre_ouvrage", mo_match.group(1).strip(), "regex", 0.6, mo_match.group(0))

    # Categorie
    cat_mots = {"travaux": 0, "fournitures": 0, "services": 0, "etudes": 0}
    for cat in cat_mots.keys():
        cat_mots[cat] = len(re.findall(r'\b' + cat + r'\b', text_clean, re.IGNORECASE))
    
    best_cat = max(cat_mots, key=cat_mots.get)
    if cat_mots[best_cat] > 0:
        add_field("categorie_marche", best_cat.capitalize(), "keyword", 0.7, f"Mots clés: {cat_mots}")

    return info
