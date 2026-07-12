import pytest
from datetime import date
from backend.models import CategorieMarche, Marche, OcrLog
from backend.repository import MarcheRepository, OcrLogRepository

def test_analytics_kpis(db_session):
    # Setup test data
    repo = MarcheRepository(db_session)
    repo.create({
        "numero_appel_offre": "A1",
        "titre_projet": "Titre 1",
        "organisme_acheteur": "Org 1",
        "montant": 1000000.0,
        "delai_execution_mois": 12,
        "categorie_prestation": CategorieMarche.Services
    })
    repo.create({
        "numero_appel_offre": "A2",
        "titre_projet": "Titre 2",
        "organisme_acheteur": "Org 2",
        "montant": 2500000.0,
        "delai_execution_mois": 24,
        "categorie_prestation": CategorieMarche.Travaux
    })
    
    ocr_repo = OcrLogRepository(db_session)
    ocr_repo.create({"document_id": 1, "confidence_score_avg": 90.0, "engine_name": "test"})
    ocr_repo.create({"document_id": 2, "confidence_score_avg": 70.0, "engine_name": "test"})
    
    # Act
    kpis = repo.kpis()
    
    # Assert
    assert kpis["total_appels_offres"] == 2
    assert kpis["volume_financier_total_mad"] == 3500000.0
    assert kpis["delai_moyen_execution_mois"] == 18.0
    assert kpis["taux_reussite_ocr_pct"] == 80.0

def test_analytics_top_buyers(db_session):
    repo = MarcheRepository(db_session)
    repo.create({"numero_appel_offre": "1", "titre_projet": "1", "organisme_acheteur": "Ministère A", "montant": 50.0})
    repo.create({"numero_appel_offre": "2", "titre_projet": "2", "organisme_acheteur": "Ministère B", "montant": 200.0})
    repo.create({"numero_appel_offre": "3", "titre_projet": "3", "organisme_acheteur": "Ministère A", "montant": 250.0})
    
    buyers = repo.top_buyers(limit=5)
    
    assert len(buyers) == 2
    assert buyers[0]["organisme"] == "Ministère A"
    assert buyers[0]["volume_mad"] == 300.0
    assert buyers[0]["nb_marches"] == 2
    
    assert buyers[1]["organisme"] == "Ministère B"
    assert buyers[1]["volume_mad"] == 200.0
    assert buyers[1]["nb_marches"] == 1
