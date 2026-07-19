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

    # Refactored Maitre ouvrage extraction (NLP-16)
    mo_candidate = None
    mo_source = "none"
    mo_score = 0.0
    mo_snippet = ""
    
    mo_match = re.search(
        r"(?:maitre\s+d['’]?ouvrage|acheteur\s+public|organisme\s+acheteur)\s*[:\-]?\s*([^.]+?)(?=\. |Objet|Le|Caution|Estimation|Date|Avis|Appel|\bdu\b|\bau\b)",
        text_clean,
        re.IGNORECASE
    )
    if mo_match:
        cand = mo_match.group(1).strip()
        cand_clean = re.sub(r'^(royaume du maroc\s*|ministère de\s*)', '', cand, flags=re.IGNORECASE).strip()
        if 5 < len(cand_clean) < 150:
            mo_candidate = cand
            mo_source = "regex"
            mo_score = 0.85
            mo_snippet = mo_match.group(0)

    if nlp:
        doc = nlp(text_clean[:2000])
        orgs = []
        for ent in doc.ents:
            if ent.label_ == "ORG":
                t = ent.text.strip()
                if 5 < len(t) < 100 and not any(junk in t.lower() for junk in ["royaume", "maroc", "objet", "cps", "règlement"]):
                    orgs.append((t, ent.text))
        
        if orgs:
            if mo_candidate:
                for org_t, snippet in orgs:
                    if org_t.lower() in mo_candidate.lower() or mo_candidate.lower() in org_t.lower():
                        mo_score = 0.95
                        mo_source = "regex+spacy"
                        break
            else:
                mo_candidate = orgs[0][0]
                mo_source = "spacy"
                mo_score = 0.75
                mo_snippet = orgs[0][1]
                
    if not mo_candidate and mo_match:
        mo_candidate = mo_match.group(1).strip()
        mo_source = "regex"
        mo_score = 0.6
        mo_snippet = mo_match.group(0)
        
    if mo_candidate:
        mo_candidate = re.sub(r'\s+', ' ', mo_candidate).strip()
        add_field("maitre_ouvrage", mo_candidate, mo_source, mo_score, mo_snippet)

    # Type d'avis (NLP-01)
    type_avis_match = re.search(
        r"appel\s+d['’]?offres?\s+(ouvert|restreint|simplifié|négocié)|concours|bon\s+de\s+commande", 
        text_clean, 
        re.IGNORECASE
    )
    if type_avis_match:
        add_field("type_avis", type_avis_match.group(0).strip().capitalize(), "regex", 0.9, type_avis_match.group(0))

    # Qualifications requises (NLP-02)
    qualif_match = re.search(
        r"(?:qualifications?\s+(?:et\s+classifications?\s+)?(?:exig[ée]es?\s+)?)(?:de\s+)?(?:classe|cat[ée]gorie)?\s*\b([Qq][1-6]|[A-S])\b", 
        text_clean, 
        re.IGNORECASE
    )
    if qualif_match:
        add_field("qualification", qualif_match.group(1).upper(), "regex", 0.8, qualif_match.group(0))

    # Agréments requis (NLP-03)
    agrement_match = re.search(
        r"agr[ée]ments?\s+(?:exig[ée]s?\s+)?(?:de\s+classe\s+)?\b([A-Z][0-9]{1,2})\b", 
        text_clean, 
        re.IGNORECASE
    )
    if agrement_match:
        add_field("agrement", agrement_match.group(1).upper(), "regex", 0.8, agrement_match.group(0))

    # Categorie
    cat_mots = {"travaux": 0, "fournitures": 0, "services": 0, "etudes": 0}
    for cat in cat_mots.keys():
        cat_mots[cat] = len(re.findall(r'\b' + cat + r'\b', text_clean, re.IGNORECASE))
    
    best_cat = max(cat_mots, key=cat_mots.get)
    if cat_mots[best_cat] > 0:
        add_field("categorie_marche", best_cat.capitalize(), "keyword", 0.7, f"Mots clés: {cat_mots}")

    return info
