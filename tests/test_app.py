import pytest
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)


def test_root_redirect():
    response = client.get("/")
    assert response.status_code == 200
    # Since it's a redirect to static, but TestClient follows redirects by default
    # Actually, RedirectResponse redirects to /static/index.html
    # But since static files are mounted, it should serve the file
    # For testing, we can check if it returns HTML content
    assert "text/html" in response.headers.get("content-type", "")


def test_get_activities():
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data
    assert "Programming Class" in data


def test_signup_for_activity():
    # Test successful signup
    response = client.post("/activities/Chess Club/signup", params={"email": "test@example.com"})
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "test@example.com" in data["message"]

    # Verify the participant was added
    response = client.get("/activities")
    activities = response.json()
    assert "test@example.com" in activities["Chess Club"]["participants"]


def test_signup_nonexistent_activity():
    response = client.post("/activities/Nonexistent/signup", params={"email": "test@example.com"})
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "Activity not found" in data["detail"]


def test_unregister_from_activity():
    # First signup
    client.post("/activities/Basketball/signup", params={"email": "test@example.com"})

    # Then unregister
    response = client.delete("/activities/Basketball/unregister", params={"email": "test@example.com"})
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "Unregistered" in data["message"]

    # Verify removed
    response = client.get("/activities")
    activities = response.json()
    assert "test@example.com" not in activities["Basketball"]["participants"]


def test_unregister_nonexistent_activity():
    response = client.delete("/activities/Nonexistent/unregister", params={"email": "test@example.com"})
    assert response.status_code == 404


def test_unregister_not_signed_up():
    response = client.delete("/activities/Chess Club/unregister", params={"email": "notsignedup@example.com"})
    assert response.status_code == 404