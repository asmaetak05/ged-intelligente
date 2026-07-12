def test_get_kpis(client):
    response = client.get("/api/v1/analytics/kpis")
    assert response.status_code == 200
    data = response.json()
    assert "total_appels_offres" in data

def test_get_trends(client):
    response = client.get("/api/v1/analytics/trends")
    assert response.status_code == 200
    data = response.json()
    assert "months" in data

def test_get_trends_by_category(client):
    response = client.get("/api/v1/analytics/trends/by-category")
    assert response.status_code == 200

def test_get_delai_moyen(client):
    response = client.get("/api/v1/analytics/delai-moyen")
    assert response.status_code == 200

def test_get_categories_distribution(client):
    response = client.get("/api/v1/analytics/distribution/categories")
    assert response.status_code == 200

def test_get_top_buyers(client):
    response = client.get("/api/v1/analytics/top-buyers")
    assert response.status_code == 200

def test_create_appel_offre(client):
    payload = {
        "numero_ordre": "API-TEST-01",
        "objet": "Test API",
        "maitre_ouvrage": "API Org"
    }
    response = client.post("/api/v1/ged/appels-offres", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["numero_ordre"] == "API-TEST-01"

def test_get_appel_offre(client):
    payload = {
        "numero_ordre": "API-TEST-02",
        "objet": "Test API 2",
        "maitre_ouvrage": "API Org 2"
    }
    client.post("/api/v1/ged/appels-offres", json=payload)
    response = client.get("/api/v1/ged/appels-offres/API-TEST-02")
    assert response.status_code == 200
    data = response.json()
    assert data["numero_ordre"] == "API-TEST-02"

def test_list_appels_offres(client):
    response = client.get("/api/v1/ged/appels-offres")
    assert response.status_code == 200
    data = response.json()
    assert "total" in data

def test_search_documents(client):
    response = client.get("/api/v1/ged/search?q=test")
    assert response.status_code == 200
    data = response.json()
    assert "results" in data
