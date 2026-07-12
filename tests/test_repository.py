import pytest
from backend.models import Marche
from backend.repository import MarcheRepository, MarcheFilter

def test_marche_repository_create(db_session):
    repo = MarcheRepository(db_session)
    data = {
        "numero_appel_offre": "TEST-01",
        "titre_projet": "Test projet",
        "organisme_acheteur": "Test organisme"
    }
    marche, action = repo.upsert(data)
    assert action == "created"
    assert marche.numero_appel_offre == "TEST-01"
    
def test_marche_repository_update(db_session):
    repo = MarcheRepository(db_session)
    data = {
        "numero_appel_offre": "TEST-02",
        "titre_projet": "Test projet 2",
        "organisme_acheteur": "Test organisme 2"
    }
    repo.upsert(data)
    
    data_update = {
        "numero_appel_offre": "TEST-02",
        "titre_projet": "Test projet 2 updated",
        "organisme_acheteur": "Test organisme 2"
    }
    marche, action = repo.upsert(data_update)
    assert action == "updated"
    assert marche.titre_projet == "Test projet 2 updated"

def test_marche_repository_get(db_session):
    repo = MarcheRepository(db_session)
    data = {
        "numero_appel_offre": "TEST-03",
        "titre_projet": "Test projet 3",
        "organisme_acheteur": "Test organisme 3"
    }
    repo.upsert(data)
    marche = repo.get_by_numero("TEST-03")
    assert marche is not None
    assert marche.titre_projet == "Test projet 3"
    
def test_marche_repository_list(db_session):
    repo = MarcheRepository(db_session)
    data1 = {"numero_appel_offre": "TEST-04", "titre_projet": "Test 4", "organisme_acheteur": "Org 4"}
    data2 = {"numero_appel_offre": "TEST-05", "titre_projet": "Test 5", "organisme_acheteur": "Org 5"}
    repo.upsert(data1)
    repo.upsert(data2)
    marches = repo.list(MarcheFilter())
    assert len(marches) >= 2

def test_marche_repository_kpis(db_session):
    repo = MarcheRepository(db_session)
    kpis = repo.kpis()
    assert "total_appels_offres" in kpis
    assert "volume_financier_total_mad" in kpis
