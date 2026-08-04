"""Tests unitaires pour la classification ML et la détection d'anomalies financières."""
from ml.predict import predict_category
from ml.anomaly import check_marche_business_rules, detect_anomalies


def test_ml_category_prediction():
    text_travaux = "Travaux d'élargissement et de bitumage de la route nationale RN1 Rabat Direction des Routes"
    category, proba = predict_category(text_travaux)
    assert category is not None
    assert category == "Travaux"
    assert proba > 0.30

    text_fournitures = "Acquisition de matériel informatique, serveurs et baies de stockage pour le centre de données DSI"
    category_f, proba_f = predict_category(text_fournitures)
    assert category_f is not None
    assert category_f == "Fournitures"
    assert proba_f > 0.30


def test_anomaly_business_rules_normal():
    # Marché normal : 10 000 000 MAD, caution 150 000 MAD (1.5%), délai 12 mois, pénalité 1.00 ‰
    res = check_marche_business_rules(
        montant=10_000_000.0,
        caution=150_000.0,
        delai_mois=12,
        penalite_mille=1.0,
    )
    assert res["is_anomaly"] is False
    assert res["score"] == 0.0
    assert len(res["reasons"]) == 0


def test_anomaly_business_rules_excessive_caution():
    # Marché avec caution disproportionnée (15% au lieu de 1-3%)
    res = check_marche_business_rules(
        montant=2_000_000.0,
        caution=300_000.0,  # 15%
        delai_mois=6,
        penalite_mille=1.0,
    )
    assert res["is_anomaly"] is True
    assert any("élevée" in r for r in res["reasons"])


def test_anomaly_business_rules_delai_incoherent():
    # Méga-chantier de 100M MAD en 1 mois
    res = check_marche_business_rules(
        montant=100_000_000.0,
        caution=1_500_000.0,
        delai_mois=1,
        penalite_mille=1.0,
    )
    assert res["is_anomaly"] is True
    assert any("Délai" in r for r in res["reasons"])
