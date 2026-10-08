from datetime import UTC, datetime, timedelta

import pytest
from study_tracker.domain.entities.study_session import StudySession
from study_tracker.domain.entities.sub_subject import SubSubject
from study_tracker.domain.entities.subject import Subject
from study_tracker.domain.exceptions import (
    SubSubjectAlreadyExistsError,
    SubSubjectHasDependentsError,
)
from study_tracker.infrastructure.repositories.SQLAlchemy_study_session_repository import (
    SQLAlchemyStudySessionRepository,
)
from study_tracker.infrastructure.repositories.SQLAlchemy_sub_subject_repository import (
    SQLAlchemySubSubjectRepository,
)
from study_tracker.infrastructure.repositories.SQLAlchemy_subject_repository import (
    SQLAlchemySubjectRepository,
)


def test_create_and_get_sub_subject(db_session):
    subject_repository = SQLAlchemySubjectRepository(db_session)
    sub_subject_repository = SQLAlchemySubSubjectRepository(db_session)
    subject = subject_repository.create(Subject(name="Python"))

    created = sub_subject_repository.create(
        SubSubject(
            subject_id=subject.id,
            name="Data structures",
            description="Lists, trees, and graphs",
        )
    )
    retrieved = sub_subject_repository.get_by_id(created.id)

    assert retrieved is not None
    assert retrieved.id == created.id
    assert retrieved.subject_id == subject.id
    assert retrieved.name == "Data structures"
    assert retrieved.description == "Lists, trees, and graphs"
    assert retrieved.created_at is not None


def test_get_all_sub_subjects(db_session):
    subject_repository = SQLAlchemySubjectRepository(db_session)
    sub_subject_repository = SQLAlchemySubSubjectRepository(db_session)
    subject = subject_repository.create(Subject(name="Python"))

    sub_subject_repository.create(
        SubSubject(subject_id=subject.id, name="Data structures")
    )
    sub_subject_repository.create(
        SubSubject(subject_id=subject.id, name="Algorithms")
    )

    results = sub_subject_repository.get_all()

    assert len(results) == 2
    assert {item.name for item in results} == {"Data structures", "Algorithms"}


def test_same_name_is_allowed_for_different_subjects(db_session):
    subject_repository = SQLAlchemySubjectRepository(db_session)
    sub_subject_repository = SQLAlchemySubSubjectRepository(db_session)
    python = subject_repository.create(Subject(name="Python"))
    math = subject_repository.create(Subject(name="Math"))

    python_sub_subject = sub_subject_repository.create(
        SubSubject(subject_id=python.id, name="Basics")
    )
    math_sub_subject = sub_subject_repository.create(
        SubSubject(subject_id=math.id, name="Basics")
    )

    assert python_sub_subject.id != math_sub_subject.id
    assert python_sub_subject.subject_id != math_sub_subject.subject_id


def test_duplicate_name_for_same_subject_raises_domain_error(db_session):
    subject_repository = SQLAlchemySubjectRepository(db_session)
    sub_subject_repository = SQLAlchemySubSubjectRepository(db_session)
    subject = subject_repository.create(Subject(name="Python"))
    sub_subject_repository.create(
        SubSubject(subject_id=subject.id, name="Basics")
    )

    with pytest.raises(SubSubjectAlreadyExistsError):
        sub_subject_repository.create(
            SubSubject(subject_id=subject.id, name="Basics")
        )


def test_update_sub_subject_persists_name_and_description(db_session):
    subject_repository = SQLAlchemySubjectRepository(db_session)
    sub_subject_repository = SQLAlchemySubSubjectRepository(db_session)
    subject = subject_repository.create(Subject(name="Python"))
    created = sub_subject_repository.create(
        SubSubject(subject_id=subject.id, name="Basics")
    )

    updated = sub_subject_repository.update(
        SubSubject(
            id=created.id,
            subject_id=subject.id,
            name="Advanced",
            description="Advanced topics",
        )
    )

    assert updated is not None
    assert updated.id == created.id
    assert updated.name == "Advanced"
    assert updated.description == "Advanced topics"


def test_update_to_duplicate_name_raises_domain_error(db_session):
    subject_repository = SQLAlchemySubjectRepository(db_session)
    sub_subject_repository = SQLAlchemySubSubjectRepository(db_session)
    subject = subject_repository.create(Subject(name="Python"))
    first = sub_subject_repository.create(
        SubSubject(subject_id=subject.id, name="Basics")
    )
    second = sub_subject_repository.create(
        SubSubject(subject_id=subject.id, name="Advanced")
    )

    with pytest.raises(SubSubjectAlreadyExistsError):
        sub_subject_repository.update(
            SubSubject(
                id=second.id,
                subject_id=subject.id,
                name=first.name,
            )
        )


def test_get_and_update_return_none_for_missing_sub_subject(db_session):
    repository = SQLAlchemySubSubjectRepository(db_session)

    assert repository.get_by_id(999999) is None
    assert (
        repository.update(
            SubSubject(
                id=999999,
                subject_id=1,
                name="Missing",
            )
        )
        is None
    )


def test_delete_sub_subject(db_session):
    subject_repository = SQLAlchemySubjectRepository(db_session)
    sub_subject_repository = SQLAlchemySubSubjectRepository(db_session)
    subject = subject_repository.create(Subject(name="Python"))
    created = sub_subject_repository.create(
        SubSubject(subject_id=subject.id, name="Basics")
    )

    assert sub_subject_repository.delete(created.id) is True
    assert sub_subject_repository.get_by_id(created.id) is None


def test_delete_returns_false_for_missing_sub_subject(db_session):
    repository = SQLAlchemySubSubjectRepository(db_session)

    assert repository.delete(999999) is False


def test_delete_sub_subject_with_study_session_raises_domain_error(db_session):
    subject_repository = SQLAlchemySubjectRepository(db_session)
    sub_subject_repository = SQLAlchemySubSubjectRepository(db_session)
    study_session_repository = SQLAlchemyStudySessionRepository(db_session)
    subject = subject_repository.create(Subject(name="Python"))
    sub_subject = sub_subject_repository.create(
        SubSubject(subject_id=subject.id, name="Basics")
    )
    study_session = StudySession.start(
        subject_id=subject.id,
        sub_subject_id=sub_subject.id,
        started_at=datetime(2026, 1, 1, 10, 0, tzinfo=UTC),
    )
    study_session.finish(study_session.started_at + timedelta(hours=1))
    study_session_repository.create(study_session)

    with pytest.raises(SubSubjectHasDependentsError):
        sub_subject_repository.delete(sub_subject.id)
