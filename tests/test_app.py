from app import create_app

def test_home():
    app = create_app()
    client = app.test_client()

    response = client.get("/")
    assert response.status_code == 200
    assert b"Welcome" in response.data


def test_get_programs():
    app = create_app()
    client = app.test_client()

    response = client.get("/programs")
    assert response.status_code == 200
    assert isinstance(response.json, dict)


def test_invalid_program():
    app = create_app()
    client = app.test_client()

    response = client.get("/programs/invalid")
    assert response.status_code == 404