from nlp.extract_entities import extract

def test_extract_new_entities():
    sample_text = (
        "Appel d'offres ouvert pour travaux routiers. "
        "Acheteur public: Direction Régionale de l'Équipement. "
        "Qualifications exigées: classe 2, qualification Q3. "
        "Agréments requis: agrément D9 de classe supérieure."
    )
    res = extract(sample_text)
    fields = res["fields"]
    
    assert "type_avis" in fields
    assert "qualification" in fields
    assert "agrement" in fields
    assert "maitre_ouvrage" in fields
    
    assert fields["type_avis"]["value"] == "Appel d'offres ouvert"
    assert fields["qualification"]["value"] == "Q3"
    assert fields["agrement"]["value"] == "D9"
    assert "Direction" in fields["maitre_ouvrage"]["value"]


def test_extract_quality_and_bilingual():
    # Document bilingue riche avec tous les champs obligatoires
    rich_text = (
        "المملكة المغربية - وزارة التجهيز والماء "
        "Avis d'appel d'offres ouvert N° 12/2026/DGR. "
        "Objet: Travaux de renforcement de la route nationale RN1. "
        "Acheteur public: Direction Générale des Routes. "
        "Estimation du coût des prestations: 12 500 000,00 DHS. "
        "Caution provisoire fixée à la somme de 250 000,00 DH. "
        "Date limite de réception des offres: 15/09/2026. "
        "Délai d'exécution: 12 mois. "
        "Séance d'ouverture des plis le 15/09/2026 à 10h00."
    )
    res = extract(rich_text)
    fields = res["fields"]

    assert fields["langue_detectee"]["value"] == "BI"
    assert "objet" in fields
    assert "estimation_mad" in fields
    assert "caution_mad" in fields
    assert "date_limite" in fields
    assert res["low_quality"] is False
    assert res["confidence_score"] >= 0.80


def test_extract_low_quality_degraded():
    # Document dégradé avec quasiment aucune entité identifiable
    poor_text = "Page 1 scanner document illisible flou 12345."
    res = extract(poor_text)
    assert res["low_quality"] is True
    assert res["confidence_score"] < 0.40
