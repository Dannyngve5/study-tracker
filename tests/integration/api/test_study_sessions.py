from datetime import datetime, timedelta, timezone

from fastapi.testclient import TestClient


def create_subject(client: TestClient, name: str = "Python") -> dict:
    response = client.post(
        "/subjects/",
        json={
            "name": name,
            "description": "Test subject",
        },
    )

    assert response.status_code == 201
    return response.json()


def start_session(
    client: TestClient,
    subject_id: int,
    sub_subject_id: int | None = None,
) -> dict:
    payload = {
        "subject_id": subject_id,
    }

    if sub_subject_id is not None:
        payload["sub_subject_id"] = sub_subject_id

    response = client.post(
        "/study-sessions/start",
        json=payload,
    )

    assert response.status_code == 201
    return response.json()


def test_start_study_session(client: TestClient):
    subject = create_subject(client)

    response = client.post(
        "/study-sessions/start",
        json={
            "subject_id": subject["id"],
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["id"] is not None
    assert data["subject_id"] == subject["id"]
    assert data["sub_subject_id"] is None
    assert data["status"] == "running"
    assert data["ended_at"] is None
    assert data["duration_seconds"] is None


def test_start_study_session_with_nonexistent_subject(client: TestClient):
    response = client.post(
        "/study-sessions/start",
        json={
            "subject_id": 999999,
        },
    )

    assert response.status_code == 404


def test_start_study_session_twice_is_rejected(client: TestClient):
    subject = create_subject(client)

    start_session(client, subject["id"])

    response = client.post(
        "/study-sessions/start",
        json={
            "subject_id": subject["id"],
        },
    )

    assert response.status_code == 409


def test_get_active_session_when_one_exists(client: TestClient):
    subject = create_subject(client)

    session = start_session(client, subject["id"])

    response = client.get("/study-sessions/active")

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == session["id"]
    assert data["subject_id"] == subject["id"]
    assert data["status"] == "running"


def test_get_active_session_when_none_exists(client: TestClient):
    response = client.get("/study-sessions/active")

    assert response.status_code == 200
    assert response.json() is None


def test_get_study_session(client: TestClient):
    subject = create_subject(client)

    session = start_session(client, subject["id"])

    response = client.get(
        f"/study-sessions/{session['id']}",
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == session["id"]
    assert data["subject_id"] == subject["id"]
    assert data["status"] == "running"


def test_get_nonexistent_study_session(client: TestClient):
    response = client.get("/study-sessions/999999")

    assert response.status_code == 404


def test_get_study_sessions(client: TestClient):
    subject = create_subject(client)

    session = start_session(client, subject["id"])

    response = client.post(
        f"/study-sessions/{session['id']}/stop",
    )

    assert response.status_code == 200

    response = client.get("/study-sessions/")

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["id"] == session["id"]


def test_get_study_sessions_returns_empty_list(client: TestClient):
    response = client.get("/study-sessions/")

    assert response.status_code == 200
    assert response.json() == []


def test_pause_running_session(client: TestClient):
    subject = create_subject(client)

    session = start_session(client, subject["id"])

    response = client.post(
        f"/study-sessions/{session['id']}/pause",
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == session["id"]
    assert data["status"] == "paused"
    assert data["paused_at"] is not None
    assert data["ended_at"] is None


def test_pause_nonexistent_session(client: TestClient):
    response = client.post(
        "/study-sessions/999999/pause",
    )

    assert response.status_code == 404


def test_pause_already_paused_session(client: TestClient):
    subject = create_subject(client)

    session = start_session(client, subject["id"])

    response = client.post(
        f"/study-sessions/{session['id']}/pause",
    )

    assert response.status_code == 200

    response = client.post(
        f"/study-sessions/{session['id']}/pause",
    )

    assert response.status_code == 400


def test_resume_paused_session(client: TestClient):
    subject = create_subject(client)

    session = start_session(client, subject["id"])

    response = client.post(
        f"/study-sessions/{session['id']}/pause",
    )

    assert response.status_code == 200

    response = client.post(
        f"/study-sessions/{session['id']}/resume",
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == session["id"]
    assert data["status"] == "running"
    assert data["paused_at"] is None


def test_resume_nonexistent_session(client: TestClient):
    response = client.post(
        "/study-sessions/999999/resume",
    )

    assert response.status_code == 404


def test_resume_running_session_is_rejected(client: TestClient):
    subject = create_subject(client)

    session = start_session(client, subject["id"])

    response = client.post(
        f"/study-sessions/{session['id']}/resume",
    )

    assert response.status_code == 400


def test_stop_running_session(client: TestClient):
    subject = create_subject(client)

    session = start_session(client, subject["id"])

    response = client.post(
        f"/study-sessions/{session['id']}/stop",
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == session["id"]
    assert data["status"] == "finished"
    assert data["ended_at"] is not None
    assert data["duration_seconds"] is not None
    assert data["duration_seconds"] >= 0


def test_stop_paused_session(client: TestClient):
    subject = create_subject(client)

    session = start_session(client, subject["id"])

    response = client.post(
        f"/study-sessions/{session['id']}/pause",
    )

    assert response.status_code == 200

    response = client.post(
        f"/study-sessions/{session['id']}/stop",
    )

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "finished"
    assert data["ended_at"] is not None
    assert data["duration_seconds"] is not None


def test_stop_nonexistent_session(client: TestClient):
    response = client.post(
        "/study-sessions/999999/stop",
    )

    assert response.status_code == 404


def test_stop_finished_session_is_rejected(client: TestClient):
    subject = create_subject(client)

    session = start_session(client, subject["id"])

    response = client.post(
        f"/study-sessions/{session['id']}/stop",
    )

    assert response.status_code == 200

    response = client.post(
        f"/study-sessions/{session['id']}/stop",
    )

    assert response.status_code == 400


def test_create_finished_session_manually(client: TestClient):
    subject = create_subject(client)

    started_at = datetime.now(timezone.utc) - timedelta(hours=1)
    ended_at = datetime.now(timezone.utc)

    response = client.post(
        "/study-sessions/",
        json={
            "subject_id": subject["id"],
            "started_at": started_at.isoformat(),
            "ended_at": ended_at.isoformat(),
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["subject_id"] == subject["id"]
    assert data["status"] == "finished"
    assert data["ended_at"] is not None
    assert data["duration_seconds"] == 3600


def test_create_manual_session_with_invalid_dates(client: TestClient):
    subject = create_subject(client)

    started_at = datetime.now(timezone.utc)
    ended_at = started_at - timedelta(hours=1)

    response = client.post(
        "/study-sessions/",
        json={
            "subject_id": subject["id"],
            "started_at": started_at.isoformat(),
            "ended_at": ended_at.isoformat(),
        },
    )

    assert response.status_code == 422


def test_create_manual_session_with_nonexistent_subject(client: TestClient):
    started_at = datetime.now(timezone.utc) - timedelta(hours=1)
    ended_at = datetime.now(timezone.utc)

    response = client.post(
        "/study-sessions/",
        json={
            "subject_id": 999999,
            "started_at": started_at.isoformat(),
            "ended_at": ended_at.isoformat(),
        },
    )

    assert response.status_code == 404


def test_update_finished_session(client: TestClient):
    subject = create_subject(client)

    session = start_session(client, subject["id"])

    response = client.post(
        f"/study-sessions/{session['id']}/stop",
    )

    assert response.status_code == 200

    started_at = datetime.now(timezone.utc) - timedelta(hours=2)
    ended_at = datetime.now(timezone.utc)

    response = client.put(
        f"/study-sessions/{session['id']}",
        json={
            "subject_id": subject["id"],
            "sub_subject_id": None,
            "started_at": started_at.isoformat(),
            "ended_at": ended_at.isoformat(),
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == session["id"]
    assert data["status"] == "finished"
    assert data["duration_seconds"] == 7200


def test_update_running_session_is_rejected(client: TestClient):
    subject = create_subject(client)

    session = start_session(client, subject["id"])

    started_at = datetime.now(timezone.utc) - timedelta(hours=1)
    ended_at = datetime.now(timezone.utc)

    response = client.put(
        f"/study-sessions/{session['id']}",
        json={
            "subject_id": subject["id"],
            "sub_subject_id": None,
            "started_at": started_at.isoformat(),
            "ended_at": ended_at.isoformat(),
        },
    )

    assert response.status_code == 400


def test_update_nonexistent_session(client: TestClient):
    started_at = datetime.now(timezone.utc) - timedelta(hours=1)
    ended_at = datetime.now(timezone.utc)

    response = client.put(
        "/study-sessions/999999",
        json={
            "subject_id": 1,
            "sub_subject_id": None,
            "started_at": started_at.isoformat(),
            "ended_at": ended_at.isoformat(),
        },
    )

    assert response.status_code == 404


def test_update_session_with_invalid_dates(client: TestClient):
    subject = create_subject(client)

    session = start_session(client, subject["id"])

    response = client.post(
        f"/study-sessions/{session['id']}/stop",
    )

    assert response.status_code == 200

    started_at = datetime.now(timezone.utc)
    ended_at = started_at - timedelta(hours=1)

    response = client.put(
        f"/study-sessions/{session['id']}",
        json={
            "subject_id": subject["id"],
            "sub_subject_id": None,
            "started_at": started_at.isoformat(),
            "ended_at": ended_at.isoformat(),
        },
    )

    assert response.status_code == 422


def test_delete_study_session(client: TestClient):
    subject = create_subject(client)

    session = start_session(client, subject["id"])

    response = client.post(
        f"/study-sessions/{session['id']}/stop",
    )

    assert response.status_code == 200

    response = client.delete(
        f"/study-sessions/{session['id']}",
    )

    assert response.status_code == 204

    response = client.get(
        f"/study-sessions/{session['id']}",
    )

    assert response.status_code == 404


def test_delete_nonexistent_study_session(client: TestClient):
    response = client.delete(
        "/study-sessions/999999",
    )

    assert response.status_code == 404


def test_delete_running_session(client: TestClient):
    subject = create_subject(client)

    session = start_session(client, subject["id"])

    response = client.delete(
        f"/study-sessions/{session['id']}",
    )

    assert response.status_code == 204

    response = client.get(
        f"/study-sessions/{session['id']}",
    )

    assert response.status_code == 404


def test_delete_paused_session(client: TestClient):
    subject = create_subject(client)

    session = start_session(client, subject["id"])

    response = client.post(
        f"/study-sessions/{session['id']}/pause",
    )

    assert response.status_code == 200

    response = client.delete(
        f"/study-sessions/{session['id']}",
    )

    assert response.status_code == 204

    response = client.get(
        f"/study-sessions/{session['id']}",
    )

    assert response.status_code == 404
