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
