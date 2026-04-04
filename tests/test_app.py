import pytest
import os
from app import create_app

TEST_DB = "test_aceest.db"


# ---------- FIXTURE ----------
@pytest.fixture
def client():
    app = create_app()

    app.config["TESTING"] = True

    # Override DB for testing
    global DB_NAME
    DB_NAME = TEST_DB

    # Create test client
    with app.test_client() as client:
        yield client

    # Cleanup test DB
    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)


# ---------- TEST HOME ----------
def test_home_page(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"ACEest FITNESS SYSTEM" in response.data


# ---------- TEST SAVE CLIENT ----------
def test_save_client(client):
    response = client.post("/", data={
        "name": "John",
        "age": "25",
        "weight": "70",
        "program": "Fat Loss (FL)",
        "action": "save_client"
    }, follow_redirects=True)

    assert response.status_code == 200


# ---------- TEST LOAD CLIENT ----------
def test_load_client(client):
    # First save
    client.post("/", data={
        "name": "Mike",
        "age": "30",
        "weight": "80",
        "program": "Muscle Gain (MG)",
        "action": "save_client"
    })

    # Then load
    response = client.post("/", data={
        "name": "Mike",
        "action": "load_client"
    })

    assert b"CLIENT PROFILE" in response.data


# ---------- TEST SAVE PROGRESS ----------
def test_save_progress(client):
    response = client.post("/", data={
        "name": "John",
        "adherence": "85",
        "action": "save_progress"
    })

    assert response.status_code == 200