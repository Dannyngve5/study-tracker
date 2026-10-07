def test_create_subject(client):
    response = client.post(
        "/subjects/",
        json={
            "name": "Python",
            "description": "Python programming",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["id"] > 0
    assert data["name"] == "Python"
    assert data["description"] == "Python programming"
    assert "created_at" in data


def test_create_subject_without_description(client):
    response = client.post(
        "/subjects/",
        json={
            "name": "English",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["name"] == "English"
    assert data["description"] is None


def test_create_subject_duplicate_name(client):
    client.post(
        "/subjects/",
        json={
            "name": "Python",
            "description": "Python programming",
        },
    )

    response = client.post(
        "/subjects/",
        json={
            "name": "Python",
            "description": "Another description",
        },
    )

    assert response.status_code == 409


def test_create_subject_invalid_data(client):
    response = client.post(
        "/subjects/",
        json={
            "name": "",
        },
    )

    assert response.status_code == 422


def test_get_subjects(client):
    client.post(
        "/subjects/",
        json={"name": "Python"},
    )
    client.post(
        "/subjects/",
        json={"name": "English"},
    )

    response = client.get("/subjects/")

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 2
    assert {subject["name"] for subject in data} == {
        "Python",
        "English",
    }


def test_get_subject(client):
    create_response = client.post(
        "/subjects/",
        json={"name": "Python"},
    )

    subject_id = create_response.json()["id"]

    response = client.get(f"/subjects/{subject_id}")

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == subject_id
    assert data["name"] == "Python"


def test_get_subject_not_found(client):
    response = client.get("/subjects/999999")

    assert response.status_code == 404


def test_get_subject_invalid_id(client):
    response = client.get("/subjects/0")

    assert response.status_code == 422


def test_update_subject(client):
    create_response = client.post(
        "/subjects/",
        json={
            "name": "Python",
            "description": "Programming",
        },
    )

    subject_id = create_response.json()["id"]

    response = client.put(
        f"/subjects/{subject_id}",
        json={
            "name": "Python Advanced",
            "description": "Advanced programming",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == subject_id
    assert data["name"] == "Python Advanced"
    assert data["description"] == "Advanced programming"


def test_update_subject_not_found(client):
    response = client.put(
        "/subjects/999999",
        json={
            "name": "Python",
            "description": "Programming",
        },
    )

    assert response.status_code == 404


def test_update_subject_duplicate_name(client):
    client.post(
        "/subjects/",
        json={"name": "Python"},
    )

    create_response = client.post(
        "/subjects/",
        json={"name": "English"},
    )

    subject_id = create_response.json()["id"]

    response = client.put(
        f"/subjects/{subject_id}",
        json={
            "name": "Python",
            "description": None,
        },
    )

    assert response.status_code == 409


def test_delete_subject(client):
    create_response = client.post(
        "/subjects/",
        json={"name": "Python"},
    )

    subject_id = create_response.json()["id"]

    response = client.delete(f"/subjects/{subject_id}")

    assert response.status_code == 204

    get_response = client.get(f"/subjects/{subject_id}")

    assert get_response.status_code == 404


def test_delete_subject_not_found(client):
    response = client.delete("/subjects/999999")

    assert response.status_code == 404


def test_delete_subject_invalid_id(client):
    response = client.delete("/subjects/0")

    assert response.status_code == 422
