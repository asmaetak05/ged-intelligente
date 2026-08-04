import re
from nlp.normalize import normalize_date, normalize_money, normalize_mois
from nlp.villes_maroc import VILLES_MAROC
from nlp.extract_typeavis import extract_type_avis
from nlp.extract_qualif import extract_qualif
from nlp.extract_agrement import extract_agrement

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
    objet_match = re.search(r"objet\s*(?:de\s*l['’]?appel\s*d['’]?offres)?\s*[\:\-]\s*(.*?)(?=\. |Caution|Estimation|Date|L['’]estimation|Le dossier)", text_clean, re.IGNORECASE)
    if not objet_match:
        objet_match = re.search(r"pour\s+(la\s+fourniture\s+.*?|l['’]ex[ée]cution\s+.*?|les\s+travaux\s+.*?|la\s+r[ée]alisation\s+.*?|l['’]achat\s+.*?)(?=\. |\(en lot|\(lot|Le dossier|L['’]estimation)", text_clean, re.IGNORECASE)
    if objet_match:
        add_field("objet", objet_match.group(1).strip(), "regex", 0.9, objet_match.group(0))

    # Estimation
    est_match = re.search(
        r"(?:estimation|budget\s+estimatif|co[uû]t\s+estimatif|montant\s+estimatif|co[uû]ts?\s+des\s+prestations).*?[\(\[\s]*([\d\s\.,]{3,})\s*[\)\]\s]*(?:dhs?|mad|dirhams?|dh\b)",
        text_clean,
        re.IGNORECASE
    )
    if not est_match:
        est_match = re.search(
            r"estimation.*?(?:est|somme|\:)?\s*[\(\[\s]*([\d\s\.,]+)\s*(?:dhs?|mad|dirhams?|dh\b)",
            text_clean,
            re.IGNORECASE
        )
    if est_match:
        val_est = normalize_money(est_match.group(1))
        if val_est:
            add_field("estimation_mad", val_est, "regex", 0.9, est_match.group(0))

    # Caution
    caution_match = re.search(
        r"(?:caution(?:nement)?\s+provisoire|caution\s+bancaire|cautionnement).*?[\(\[\s]*([\d\s\.,]{3,})\s*[\)\]\s]*(?:dhs?|mad|dirhams?|dh\b)",
        text_clean,
        re.IGNORECASE
    )
    if not caution_match:
        caution_match = re.search(
            r"caution(?:nement)?\s+provisoire.*?(?:est|somme|\:)?\s*[\(\[\s]*([\d\s\.,]+)\s*(?:dhs?|mad|dirhams?|dh\b)",
            text_clean,
            re.IGNORECASE
        )
    if caution_match:
        val_caut = normalize_money(caution_match.group(1))
        if val_caut:
            add_field("caution_mad", val_caut, "regex", 0.9, caution_match.group(0))
        
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

    # Reference / Numero AO
    ref_match = re.search(r"(?:R[éé]f[éerence]*|n[°o\.\s]|num[ée]ro)\s*[:\-]?\s*([0-9]+/[A-Z0-9\-_/]+)", text_clean, re.IGNORECASE)
    if not ref_match:
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
    
    # 1. Regex ciblée sur les institutions publiques marocaines
    inst_match = re.search(
        r"(?:Haut-?\s*Commissariat\s+au\s+Plan|Direction\s+(?:R[ée]gionale|Provinciale|G[ée]n[ée]rale|des\s+Ressources\s+Humaines|de\s+l['’]?[A-Z][a-zA-Z\s]+)|Agence\s+Nationale\s+[A-Za-z\s]+|Minist[èe]re\s+de\s+[A-Za-z\s]+|Office\s+National\s+[A-Za-z\s]+|Soci[ée]t[ée]\s+Nationale\s+[A-Za-z\s]+|Commune\s+(?:Urbaine\s+|Rurale\s+|de\s+)[A-Z][a-zA-Z]+)",
        text_clean,
        re.IGNORECASE
    )
    if inst_match:
        inst_name = inst_match.group(0).strip()
        if 10 < len(inst_name) < 150:
            mo_candidate = inst_name
            mo_source = "regex_institution"
            mo_score = 0.9
            mo_snippet = inst_match.group(0)

    if not mo_candidate:
        mo_match = re.search(
            r"(?:maitre\s+d['’]?ouvrage|acheteur\s+public|organisme\s+acheteur)\s*[:\-]?\s*([^.]+?)(?=\. |Objet|Le\s+[A-Z]|Caution|Estimation|Date|Avis|Appel|\bdu\b|\bau\b|\best\s+fix|\best\b)",
            text_clean,
            re.IGNORECASE
        )
        if mo_match:
            cand = mo_match.group(1).strip()
            cand_clean = re.sub(r'^(royaume du maroc\s*|ministère de\s*)', '', cand, flags=re.IGNORECASE).strip()
            if 5 < len(cand_clean) < 150 and cand_clean.lower() not in ["le maître d’ouvrage", "le maitre d'ouvrage", "maître d’ouvrage", "maitre d'ouvrage"]:
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
                if 5 < len(t) < 100 and not any(junk in t.lower() for junk in ["royaume", "maroc", "objet", "cps", "règlement", "maître"]):
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
        
    if mo_candidate:
        mo_candidate = re.sub(r'\s+', ' ', mo_candidate).strip()
        add_field("maitre_ouvrage", mo_candidate, mo_source, mo_score, mo_snippet)

    # Type d'avis (NLP-01)
    type_avis_res = extract_type_avis(text_clean)
    if type_avis_res:
        add_field("type_avis", type_avis_res["value"], type_avis_res["source"], type_avis_res["score"], type_avis_res["snippet"])

    # Qualifications requises (NLP-02)
    qualif_res = extract_qualif(text_clean)
    if qualif_res:
        add_field("qualification", qualif_res["value"], qualif_res["source"], qualif_res["score"], qualif_res["snippet"])

    # Agréments requis (NLP-03)
    agrement_res = extract_agrement(text_clean)
    if agrement_res:
        add_field("agrement", agrement_res["value"], agrement_res["source"], agrement_res["score"], agrement_res["snippet"])

    # Categorie
    cat_mots = {"travaux": 0, "fournitures": 0, "services": 0, "etudes": 0}
    for cat in cat_mots.keys():
        cat_mots[cat] = len(re.findall(r'\b' + cat + r'\b', text_clean, re.IGNORECASE))
    
    best_cat = max(cat_mots, key=cat_mots.get)
    if cat_mots[best_cat] > 0:
        add_field("categorie_marche", best_cat.capitalize(), "keyword", 0.7, f"Mots clés: {cat_mots}")

    # Modèle d'avis (NLP-06)
    modele_match = re.search(r"avis\s+(12-10|13-10|standard)", text_clean, re.IGNORECASE)
    if modele_match:
        add_field("modele_avis", modele_match.group(1).strip(), "regex", 0.9, modele_match.group(0))

    # Contacts: Téléphone (NLP-07)
    tel_match = re.search(r"(?:\+212|0)[5-7]\d{8}", text_clean)
    if tel_match:
        add_field("telephone", tel_match.group(0), "regex", 0.9, tel_match.group(0))

    # Contacts: Email (NLP-07)
    email_match = re.search(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", text_clean)
    if email_match:
        add_field("email", email_match.group(0), "regex", 0.9, email_match.group(0))

    # Date d'ouverture des plis (NLP-04)
    ouverture_match = re.search(
        r"(\d{1,2}\s+(?:janvier|f[ée]vrier|mars|avril|mai|juin|juillet|ao[uû]t|septembre|octobre|novembre|d[ée]cembre)\s+\d{4})[^\.\n]*?(?:l[\'’]ouverture\s+des\s+plis|s[ée]ance\s+d[\'’]ouverture)",
        text_clean,
        re.IGNORECASE
    )
    if not ouverture_match:
        ouverture_match = re.search(
            r"(?:s[ée]ance\s+d['’]ouverture|l['’]ouverture\s+des\s+plis).*?(\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\s*(?:à\s*)?\d{1,2}h\d{0,2}|\d{1,2}\s+(?:janvier|f[ée]vrier|mars|avril|mai|juin|juillet|ao[uû]t|septembre|octobre|novembre|d[ée]cembre)\s+\d{4})",
            text_clean,
            re.IGNORECASE
        )
    if ouverture_match:
        raw_date_str = ouverture_match.group(1).split("à")[0].strip()
        add_field("date_ouverture_plis", normalize_date(raw_date_str), "regex", 0.85, ouverture_match.group(0))

    # Références réglementaires (NLP-08)
    reg_match = re.search(r"(article\s+\d+\s+du\s+d[ée]cret\s+n[°º]?\s*[\d-]+)", text_clean, re.IGNORECASE)
    if reg_match:
        add_field("reference_reglementaire", reg_match.group(1), "regex", 0.85, reg_match.group(0))

    # Détection de langue et bilinguisme (NLP-11)
    is_ar = bool(re.search(r"[\u0600-\u06FF]", text_clean))
    is_fr = bool(re.search(r"[a-zA-Z]{3,}", text_clean))
    
    if is_ar and is_fr:
        detected_lang = "BI"
    elif is_ar:
        detected_lang = "AR"
    else:
        detected_lang = "FR"
    add_field("langue_detectee", detected_lang, "charset_heuristics", 0.95, "")

    # Détection de qualité et score de confiance global (NLP-13)
    mandatory_fields = ["objet", "estimation_mad", "maitre_ouvrage", "date_limite", "caution_mad"]
    extracted_fields = [k for k in info["fields"].keys() if k != "langue_detectee"]
    
    found_mandatory = [f for f in mandatory_fields if f in info["fields"]]
    quality_score = round(len(found_mandatory) / len(mandatory_fields), 2)
    
    info["confidence_score"] = quality_score
    info["missing_fields"] = [f for f in mandatory_fields if f not in info["fields"]]
    
    # Flag low_quality si moins de 2 champs obligatoires ou score < 0.4
    if quality_score < 0.40 or len(extracted_fields) < 3:
        info["low_quality"] = True
    else:
        info["low_quality"] = False

    return info
