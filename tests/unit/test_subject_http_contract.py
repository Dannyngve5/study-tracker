from datetime import UTC, datetime

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from study_tracker.application.exceptions import SubjectNotFoundError
from study_tracker.domain.entities.subject import Subject
from study_tracker.domain.exceptions import (
    SubjectAlreadyExistsError,
    SubjectHasDependentsError,
)
from study_tracker.presentation.api.dependencies import get_subject_service
from study_tracker.presentation.api.exception_handlers import (
    register_exception_handlers,
)
from study_tracker.presentation.api.routes.subjects import router


class StubSubjectService:
    def create(self, dto):
        if dto.name == "Duplicate":
            raise SubjectAlreadyExistsError(dto.name)
        return Subject(
            id=1,
            name=dto.name,
            description=dto.description,
            created_at=datetime(2026, 1, 1, tzinfo=UTC),
        )

    def get_all(self):
        return [subject()]

    def get_by_id(self, subject_id):
        if subject_id == 404:
            raise SubjectNotFoundError(subject_id)
        return subject()

    def update(self, subject_id, dto):
        if subject_id == 404:
            raise SubjectNotFoundError(subject_id)
        return Subject(
            id=1,
            name=dto.name,
            description=dto.description,
            created_at=datetime(2026, 1, 1, tzinfo=UTC),
        )

    def delete(self, subject_id):
        if subject_id == 404:
            raise SubjectNotFoundError(subject_id)
        if subject_id == 409:
            raise SubjectHasDependentsError(subject_id)


def subject() -> Subject:
    return Subject(
        id=1,
        name="Mathematics",
        description=None,
        created_at=datetime(2026, 1, 1, tzinfo=UTC),
    )


@pytest.fixture
def client():
    app = FastAPI()
    register_exception_handlers(app)
    app.include_router(router)
    app.dependency_overrides[get_subject_service] = StubSubjectService
    with TestClient(app) as test_client:
        yield test_client


def test_subject_routes_return_explicit_response_schema(client):
    response = client.get("/subjects/")

    assert response.status_code == 200
    assert response.json() == [
        {
            "id": 1,
            "name": "Mathematics",
            "description": None,
            "created_at": "2026-01-01T00:00:00Z",
        }
    ]


def test_missing_subject_is_returned_as_not_found(client):
    response = client.get("/subjects/404")

    assert response.status_code == 404
    assert response.json() == {"detail": "Subject with id 404 not found"}


def test_update_subject_returns_the_updated_schema(client):
    response = client.put(
        "/subjects/1",
        json={"name": "Physics", "description": "Mechanics"},
    )

    assert response.status_code == 200
    assert response.json()["name"] == "Physics"
    assert response.json()["description"] == "Mechanics"


def test_duplicate_subject_is_returned_as_conflict(client):
    response = client.post("/subjects/", json={"name": "Duplicate"})

    assert response.status_code == 409
    assert response.json() == {"detail": "Subject with name 'Duplicate' already exists"}


def test_subject_with_dependents_is_not_deleted(client):
    response = client.delete("/subjects/409")

    assert response.status_code == 409
    assert response.json() == {
        "detail": "Subject with id 409 cannot be deleted while it has related records"
    }


def test_subject_name_is_trimmed_and_cannot_be_blank(client):
    response = client.post("/subjects/", json={"name": "   "})

    assert response.status_code == 422


def test_subject_name_is_trimmed_before_service_receives_it(client):
    response = client.post("/subjects/", json={"name": " Python "})

    assert response.status_code == 201
    assert response.json()["name"] == "Python"


@pytest.mark.parametrize("subject_id", [0, -1])
def test_non_positive_subject_id_is_rejected(client, subject_id):
    response = client.get(f"/subjects/{subject_id}")

    assert response.status_code == 422
