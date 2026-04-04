import pytest
from app import create_app

@pytest.fixture
def client():
    app = create_app("test.db")
    app.config["TESTING"] = True
    return app.test_client()

def test_home(client):
    res = client.get("/")
    assert res.status_code == 200

def test_save_client(client):
    res = client.post("/", data={
        "name": "Test",
        "weight": "70",
        "program": "Fat Loss (FL)",
        "action": "save_client"
    })
    assert res.status_code == 200

def test_progress(client):
    res = client.post("/", data={
        "name": "Test",
        "adherence": "80",
        "action": "save_progress"
    })
    assert res.status_code == 200