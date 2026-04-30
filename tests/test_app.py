import pytest
import os
from app import create_app


@pytest.fixture
def client():
    if os.path.exists("test.db"):
        os.remove("test.db")

    app = create_app("test.db")
    app.config["TESTING"] = True
    return app.test_client()


def test_login(client):
    res = client.post("/", data={
        "username": "admin",
        "password": "admin"
    })
    assert res.status_code in (200, 302)


def test_dashboard(client):
    client.post("/", data={
        "username": "admin",
        "password": "admin"
    })
    res = client.get("/dashboard")
    assert res.status_code == 200


def test_save_client(client):
    client.post("/", data={
        "username": "admin",
        "password": "admin"
    })
    res = client.post("/dashboard", data={
        "new_name": "TestUser",
        "action": "save_client"
    })
    assert res.status_code == 200