import pytest
import os
from app import create_app

TEST_DB = "test.db"

@pytest.fixture
def client():
    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)

    app = create_app(TEST_DB)
    app.config["TESTING"] = True

    return app.test_client()


def test_home(client):
    assert client.get("/").status_code == 200


def test_save_client(client):
    res = client.post("/", data={
        "name": "TestUser",
        "weight": "70",
        "program": "Fat Loss (FL) – 3 day",
        "action": "save_client"
    })
    assert res.status_code == 200


def test_load_client(client):
    client.post("/", data={
        "name": "TestUser",
        "weight": "70",
        "program": "Fat Loss (FL) – 3 day",
        "action": "save_client"
    })

    res = client.post("/", data={
        "name": "TestUser",
        "action": "load_client"
    })

    assert b"CLIENT PROFILE" in res.data