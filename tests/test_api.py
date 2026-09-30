"""Basic tests for the API and profile functions."""
from fastapi.testclient import TestClient

from backend.api import app
from backend.functions import profile, reset_profile

client = TestClient(app)


def test_home_page_loads():
    res = client.get("/")
    assert res.status_code == 200


def test_profile_endpoint_returns_dict():
    res = client.get("/profile")
    assert res.status_code == 200
    assert isinstance(res.json(), dict)


def test_reset_endpoint_clears_profile():
    res = client.post("/reset")
    assert res.status_code == 200
    assert "cleared" in res.json()["message"].lower()
    assert not any(profile.values())


def test_reset_profile_function():
    reset_profile()
    assert not any(profile.values())


def test_chat_rejects_empty_body():
    res = client.post("/chat", json={})
    assert res.status_code == 422