from fastapi.testclient import TestClient
from src import app as app_module


client = TestClient(app_module.app)


def get_participants(activity_name: str):
    resp = client.get("/activities")
    resp.raise_for_status()
    activities = resp.json()
    return activities[activity_name]["participants"]


def safe_unregister(activity: str, email: str):
    # attempt to unregister, ignore 404
    resp = client.delete(f"/activities/{activity}/unregister", params={"email": email})
    return resp


def test_signup_and_unregister_flow():
    activity = "Chess Club"
    email = "test_user@example.com"

    # ensure clean state
    safe_unregister(activity, email)

    # sign up
    resp = client.post(f"/activities/{activity}/signup", params={"email": email})
    assert resp.status_code == 200
    assert f"Signed up {email}" in resp.json().get("message", "")

    # verify present
    participants = get_participants(activity)
    assert email in participants

    # unregister
    resp = client.delete(f"/activities/{activity}/unregister", params={"email": email})
    assert resp.status_code == 200
    assert f"Removed {email}" in resp.json().get("message", "")

    # verify removed
    participants = get_participants(activity)
    assert email not in participants


def test_duplicate_signup_returns_400():
    activity = "Programming Class"
    email = "dup_user@example.com"

    # ensure clean state
    safe_unregister(activity, email)

    # first signup should succeed
    resp = client.post(f"/activities/{activity}/signup", params={"email": email})
    assert resp.status_code == 200

    # second signup should fail
    resp = client.post(f"/activities/{activity}/signup", params={"email": email})
    assert resp.status_code == 400
    assert "already signed up" in resp.json().get("detail", "").lower() or "already signed up" in resp.json().get("message", "").lower()

    # cleanup
    safe_unregister(activity, email)


def test_unregister_nonexistent_returns_404():
    activity = "Tennis Club"
    email = "noone@example.com"

    # ensure not present
    safe_unregister(activity, email)

    resp = client.delete(f"/activities/{activity}/unregister", params={"email": email})
    assert resp.status_code == 404
    assert "not found" in resp.json().get("detail", "").lower()
