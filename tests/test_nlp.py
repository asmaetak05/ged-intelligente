from nlp.extract_entities import extract
from nlp.normalize import normalize_date, normalize_money, normalize_mois

def test_extract_objet():
    res = extract("Objet: Achat de fourniture de bureau. Caution provisoire: 5000 DHS.")
    assert "objet" in res["fields"]
    assert res["fields"]["objet"]["value"] == "Achat de fourniture de bureau"

def test_extract_dates_french():
    d = normalize_date("12 janvier 2026")
    assert d is not None
    assert d.year == 2026
    assert d.month == 1

def test_extract_money_with_spaces():
    m = normalize_money("1 500 250,50")
    assert m == 1500250.5

def test_extract_region_from_city():
    res = extract("La ville de Casablanca lance cet appel d'offres.")
    assert "region" in res["fields"]
    assert res["fields"]["region"]["value"] == "Casablanca"

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

