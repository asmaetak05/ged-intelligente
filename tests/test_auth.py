import pytest
from backend.models import User, Role
from backend.auth.auth_handler import get_password_hash

@pytest.fixture
def admin_user(db_session):
    admin_role = db_session.query(Role).filter(Role.name == "admin").first()
    if not admin_role:
        admin_role = Role(name="admin")
        db_session.add(admin_role)
        db_session.commit()

    user = User(
        username="testadmin",
        email="admin@test.com",
        hashed_password=get_password_hash("testpass"),
        roles=[admin_role]
    )
    db_session.add(user)
    db_session.commit()
    return user

@pytest.fixture
def reader_user(db_session):
    reader_role = db_session.query(Role).filter(Role.name == "reader").first()
    if not reader_role:
        reader_role = Role(name="reader")
        db_session.add(reader_role)
        db_session.commit()

    user = User(
        username="testreader",
        email="reader@test.com",
        hashed_password=get_password_hash("testpass"),
        roles=[reader_role]
    )
    db_session.add(user)
    db_session.commit()
    return user

def test_login_success(client, admin_user):
    response = client.post(
        "/api/v1/auth/login",
        data={"username": "testadmin", "password": "testpass"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["role"] == "admin"

def test_login_failure(client, admin_user):
    response = client.post(
        "/api/v1/auth/login",
        data={"username": "testadmin", "password": "wrongpass"}
    )
    assert response.status_code == 401

def test_protected_route_without_token(client):
    response = client.post("/api/v1/ged/documents/upload")
    assert response.status_code == 401

def test_protected_route_with_insufficient_role(client, reader_user):
    login_resp = client.post(
        "/api/v1/auth/login",
        data={"username": "testreader", "password": "testpass"}
    )
    token = login_resp.json()["access_token"]
    
    # Needs analyst or admin, reader should fail
    response = client.post(
        "/api/v1/ged/documents/upload",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 403

def test_security_headers(client):
    response = client.get("/api/v1/system/monitoring")
    assert response.status_code == 200
    assert response.headers.get("X-Content-Type-Options") == "nosniff"
    assert response.headers.get("X-Frame-Options") == "DENY"
    assert response.headers.get("Strict-Transport-Security") == "max-age=31536000; includeSubDomains"
