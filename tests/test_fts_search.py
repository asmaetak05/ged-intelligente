"""Tests unitaires pour le moteur de recherche Full-Text Search (FTS)."""
from datetime import date
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend import models
from backend.repository import MarcheRepository
from search.postgres_fts import PostgresFTS


@pytest.fixture
def fts_db_session():
    """Crée une session SQLite en mémoire pour tester les fonctionnalités FTS."""
    engine = create_engine("sqlite:///:memory:", echo=False)
    models.Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    # Création de marchés de test
    m1 = models.Marche(
        numero_appel_offre="AO-01/2026/DGR",
        titre_projet="Travaux d'aménagement et d'élargissement de la route nationale RN1",
        organisme_acheteur="Direction Générale des Routes",
        ville_execution="Rabat",
        region="Rabat-Salé-Kénitra",
        montant=15000000.0,
        delai_execution_mois=12,
        date_parution=date(2026, 1, 15),
        date_limite=date(2026, 2, 28),
        categorie_prestation=models.CategorieMarche.Travaux,
        tsv_search="route nationale bitume terrassement assainissement",
    )
    m2 = models.Marche(
        numero_appel_offre="AO-02/2026/DGH",
        titre_projet="Étude hydrologique et géotechnique pour la construction d'un barrage collinaire",
        organisme_acheteur="Direction Générale de l'Hydraulique",
        ville_execution="Ouarzazate",
        region="Drâa-Tafilalet",
        montant=3500000.0,
        delai_execution_mois=6,
        date_parution=date(2026, 2, 10),
        date_limite=date(2026, 3, 30),
        categorie_prestation=models.CategorieMarche.Etudes,
        tsv_search="barrage eau retenue topographie calculs",
    )
    m3 = models.Marche(
        numero_appel_offre="AO-03/2026/DRE",
        titre_projet="Fourniture et installation de stations de surveillance météorologique",
        organisme_acheteur="Direction Régionale de l'Équipement",
        ville_execution="Casablanca",
        region="Casablanca-Settat",
        montant=2200000.0,
        delai_execution_mois=4,
        date_parution=date(2026, 3, 5),
        date_limite=date(2026, 4, 15),
        categorie_prestation=models.CategorieMarche.Fournitures,
        tsv_search="capteurs capteur météo pluie télémesure",
    )
    session.add_all([m1, m2, m3])
    session.commit()

    yield session
    session.close()


def test_fts_sanitize_and_build_query():
    raw = "travaux route! & 'RN1'?"
    sanitized = PostgresFTS.sanitize_query(raw)
    assert "travaux" in sanitized
    assert "route" in sanitized
    assert "RN1" in sanitized

    tsquery = PostgresFTS.build_tsquery_string("travaux route")
    assert "travaux:*" in tsquery
    assert "route:*" in tsquery


def test_fts_search_exact_and_partial(fts_db_session):
    fts = PostgresFTS(fts_db_session)
    results, total = fts.search(query="route")
    assert total >= 1
    assert any("RN1" in r.marche.titre_projet for r in results)
    assert "<mark>" in results[0].highlight


def test_fts_search_with_category_filter(fts_db_session):
    fts = PostgresFTS(fts_db_session)
    # Chercher barrage avec filtre Travaux (doit être vide car c'est Etudes)
    results, total = fts.search(
        query="barrage",
        categorie=models.CategorieMarche.Travaux
    )
    assert total == 0

    # Chercher barrage avec filtre Etudes
    results, total = fts.search(
        query="barrage",
        categorie=models.CategorieMarche.Etudes
    )
    assert total == 1
    assert "AO-02/2026/DGH" in results[0].marche.numero_appel_offre


def test_fts_search_sorting(fts_db_session):
    repo = MarcheRepository(fts_db_session)
    
    # Tri par montant décroissant
    results, total = repo.search_fts_advanced(
        query="Direction",
        order_by="montant",
        order_dir="desc"
    )
    assert total == 3
    assert results[0].marche.montant >= results[1].marche.montant
    assert results[1].marche.montant >= results[2].marche.montant


def test_fts_search_in_tsv_body(fts_db_session):
    fts = PostgresFTS(fts_db_session)
    # Mot présent uniquement dans le champ tsv_search (contenu extrait OCR)
    results, total = fts.search(query="télémesure")
    assert total == 1
    assert results[0].marche.numero_appel_offre == "AO-03/2026/DRE"
