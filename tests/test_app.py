import pytest
from app import create_app

TEST_DB = "test.db"

@pytest.fixture
def client():
    app = create_app(TEST_DB)
    app.config["TESTING"] = True

    with app.test_client() as client:
        yield client


def test_home(client):
    res = client.get("/")
    assert res.status_code == 200


def test_save_client(client):
    res = client.post("/", data={
        "name": "John",
        "age": "25",
        "weight": "70",
        "program": "Fat Loss (FL)",
        "action": "save_client"
    })
    assert res.status_code == 200


def test_load_client(client):
    client.post("/", data={
        "name": "Mike",
        "age": "30",
        "weight": "80",
        "program": "Muscle Gain (MG)",
        "action": "save_client"
    })

    res = client.post("/", data={
        "name": "Mike",
        "action": "load_client"
    })

    assert b"CLIENT PROFILE" in res.data


def test_save_progress(client):
    res = client.post("/", data={
        "name": "John",
        "adherence": "90",
        "action": "save_progress"
    })

    assert res.status_code == 200