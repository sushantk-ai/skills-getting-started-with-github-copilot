import pytest
from fastapi.testclient import TestClient

from src import app as app_module

client = TestClient(app_module.app)


def test_get_activities():
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert "Chess Club" in data
    assert isinstance(data["Chess Club"]["participants"], list)


def test_signup_and_unregister_flow():
    activity = "Chess Club"
    email = "pytest_user@example.com"

    # Ensure clean state
    if email in app_module.activities[activity]["participants"]:
        app_module.activities[activity]["participants"].remove(email)

    # Signup
    signup = client.post(f"/activities/{activity}/signup?email={email}")
    assert signup.status_code == 200
    assert email in app_module.activities[activity]["participants"]

    # Duplicate signup should fail
    dup = client.post(f"/activities/{activity}/signup?email={email}")
    assert dup.status_code == 400

    # Unregister
    delete = client.delete(f"/activities/{activity}/participant?email={email}")
    assert delete.status_code == 200
    assert email not in app_module.activities[activity]["participants"]

    # Removing again should return 404
    delete2 = client.delete(f"/activities/{activity}/participant?email={email}")
    assert delete2.status_code == 404


def test_activity_not_found_errors():
    resp = client.post("/activities/NoSuchActivity/signup?email=a@b.com")
    assert resp.status_code == 404

    resp2 = client.delete("/activities/NoSuchActivity/participant?email=a@b.com")
    assert resp2.status_code == 404
