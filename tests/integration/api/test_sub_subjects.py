from fastapi.testclient import TestClient


def create_subject(client: TestClient, name: str = "Python") -> dict:
    response = client.post(
        "/subjects/",
        json={"name": name},
    )

    assert response.status_code == 201
    return response.json()


def create_sub_subject(
    client: TestClient,
    subject_id: int,
    name: str = "Data structures",
    description: str | None = None,
):
    return client.post(
        "/sub-subjects/",
        json={
            "subject_id": subject_id,
            "name": name,
            "description": description,
        },
    )


def test_create_sub_subject(client: TestClient):
    subject = create_subject(client)

    response = create_sub_subject(
        client,
        subject["id"],
        description="Lists, trees, and graphs",
    )

    assert response.status_code == 201
    data = response.json()
    assert data["id"] > 0
    assert data["subject_id"] == subject["id"]
    assert data["name"] == "Data structures"
    assert data["description"] == "Lists, trees, and graphs"
    assert "created_at" in data


def test_create_sub_subject_without_description(client: TestClient):
    subject = create_subject(client)

    response = create_sub_subject(client, subject["id"])

    assert response.status_code == 201
    assert response.json()["description"] is None


def test_create_sub_subject_rejects_invalid_payload(client: TestClient):
    subject = create_subject(client)

    response = client.post(
        "/sub-subjects/",
        json={
            "subject_id": subject["id"],
            "name": "",
        },
    )

    assert response.status_code == 422


def test_create_sub_subject_rejects_non_positive_subject_id(
    client: TestClient,
):
    response = client.post(
        "/sub-subjects/",
        json={"subject_id": 0, "name": "Data structures"},
    )

    assert response.status_code == 422


def test_create_sub_subject_for_missing_subject_returns_not_found(
    client: TestClient,
):
    response = create_sub_subject(client, 999999)

    assert response.status_code == 404
    assert response.json()["code"] == "SUBJECT_NOT_FOUND"


def test_duplicate_sub_subject_name_is_rejected_for_same_subject(
    client: TestClient,
):
    subject = create_subject(client)
    first = create_sub_subject(client, subject["id"])
    assert first.status_code == 201

    response = create_sub_subject(client, subject["id"])

    assert response.status_code == 409


def test_same_sub_subject_name_is_allowed_for_different_subjects(
    client: TestClient,
):
    first_subject = create_subject(client, "Python")
    second_subject = create_subject(client, "Math")

    first = create_sub_subject(client, first_subject["id"], "Basics")
    second = create_sub_subject(client, second_subject["id"], "Basics")

    assert first.status_code == 201
    assert second.status_code == 201


def test_get_sub_subjects(client: TestClient):
    subject = create_subject(client)
    create_sub_subject(client, subject["id"], "Data structures")
    create_sub_subject(client, subject["id"], "Algorithms")

    response = client.get("/sub-subjects/")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert {item["name"] for item in data} == {
        "Data structures",
        "Algorithms",
    }
    assert {item["subject_id"] for item in data} == {subject["id"]}


def test_get_sub_subject(client: TestClient):
    subject = create_subject(client)
    created = create_sub_subject(client, subject["id"])
    sub_subject_id = created.json()["id"]

    response = client.get(f"/sub-subjects/{sub_subject_id}")

    assert response.status_code == 200
    assert response.json()["id"] == sub_subject_id
    assert response.json()["subject_id"] == subject["id"]


def test_get_missing_sub_subject_returns_not_found(client: TestClient):
    response = client.get("/sub-subjects/999999")

    assert response.status_code == 404
    assert response.json()["code"] == "SUB_SUBJECT_NOT_FOUND"


def test_update_sub_subject(client: TestClient):
    subject = create_subject(client)
    created = create_sub_subject(client, subject["id"])
    sub_subject_id = created.json()["id"]

    response = client.put(
        f"/sub-subjects/{sub_subject_id}",
        json={
            "name": "Advanced data structures",
            "description": "Balanced trees and graph algorithms",
        },
    )

    assert response.status_code == 200
    assert response.json()["id"] == sub_subject_id
    assert response.json()["subject_id"] == subject["id"]
    assert response.json()["name"] == "Advanced data structures"
    assert response.json()["description"] == "Balanced trees and graph algorithms"


def test_update_sub_subject_rejects_invalid_payload(client: TestClient):
    response = client.put(
        "/sub-subjects/1",
        json={"name": ""},
    )

    assert response.status_code == 422


def test_update_missing_sub_subject_returns_not_found(client: TestClient):
    response = client.put(
        "/sub-subjects/999999",
        json={"name": "Data structures"},
    )

    assert response.status_code == 404
    assert response.json()["code"] == "SUB_SUBJECT_NOT_FOUND"


def test_delete_sub_subject(client: TestClient):
    subject = create_subject(client)
    created = create_sub_subject(client, subject["id"])
    sub_subject_id = created.json()["id"]

    response = client.delete(f"/sub-subjects/{sub_subject_id}")

    assert response.status_code == 204
    assert client.get(f"/sub-subjects/{sub_subject_id}").status_code == 404


def test_delete_missing_sub_subject_returns_not_found(client: TestClient):
    response = client.delete("/sub-subjects/999999")

    assert response.status_code == 404
    assert response.json()["code"] == "SUB_SUBJECT_NOT_FOUND"


def test_delete_sub_subject_with_sessions_returns_conflict(
    client: TestClient,
):
    subject = create_subject(client)
    created = create_sub_subject(client, subject["id"])
    sub_subject_id = created.json()["id"]

    session_response = client.post(
        "/study-sessions/start",
        json={
            "subject_id": subject["id"],
            "sub_subject_id": sub_subject_id,
        },
    )
    assert session_response.status_code == 201
    client.post(f"/study-sessions/{session_response.json()['id']}/stop")

    response = client.delete(f"/sub-subjects/{sub_subject_id}")

    assert response.status_code == 409
