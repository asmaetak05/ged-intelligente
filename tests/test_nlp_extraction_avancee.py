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
