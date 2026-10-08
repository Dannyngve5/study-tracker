from datetime import UTC, datetime

from study_tracker.domain.entities.study_session import StudySession
from study_tracker.domain.entities.subject import Subject
from study_tracker.domain.enums.study_session_status import StudySessionStatus
from study_tracker.infrastructure.repositories.SQLAlchemy_study_session_repository import (
    SQLAlchemyStudySessionRepository,
)
from study_tracker.infrastructure.repositories.SQLAlchemy_subject_repository import (
    SQLAlchemySubjectRepository,
)


def test_create_and_get_study_session(db_session):
    subject_repository = SQLAlchemySubjectRepository(db_session)
    study_session_repository = SQLAlchemyStudySessionRepository(db_session)

    subject = subject_repository.create(Subject(name="Programming"))

    study_session = StudySession.start(
        subject_id=subject.id,
        started_at=datetime.now(UTC),
    )

    created_session = study_session_repository.create(study_session)

    retrieved_session = study_session_repository.get_by_id(created_session.id)

    assert retrieved_session is not None
    assert retrieved_session.id == created_session.id
    assert retrieved_session.subject_id == subject.id
    assert retrieved_session.status is StudySessionStatus.RUNNING
    assert retrieved_session.started_at == created_session.started_at


def test_get_all_returns_sessions_ordered_by_started_at_desc(db_session):
    subject_repository = SQLAlchemySubjectRepository(db_session)
    study_session_repository = SQLAlchemyStudySessionRepository(db_session)

    subject = subject_repository.create(Subject(name="Programming"))

    older_session = StudySession.start(
        subject_id=subject.id,
        started_at=datetime(2026, 1, 1, 10, 0, tzinfo=UTC),
    )

    newer_session = StudySession.start(
        subject_id=subject.id,
        started_at=datetime(2026, 1, 2, 10, 0, tzinfo=UTC),
    )

    study_session_repository.create(older_session)
    study_session_repository.create(newer_session)

    sessions = study_session_repository.get_all()

    assert len(sessions) == 2
    assert sessions[0].started_at == newer_session.started_at
    assert sessions[1].started_at == older_session.started_at


def test_get_active_returns_running_session(db_session):
    subject_repository = SQLAlchemySubjectRepository(db_session)
    study_session_repository = SQLAlchemyStudySessionRepository(db_session)

    subject = subject_repository.create(Subject(name="Programming"))

    running_session = StudySession.start(
        subject_id=subject.id,
        started_at=datetime.now(UTC),
    )

    created_session = study_session_repository.create(running_session)

    active_session = study_session_repository.get_active()

    assert active_session is not None
    assert active_session.id == created_session.id
    assert active_session.status is StudySessionStatus.RUNNING


def test_get_active_returns_paused_session(db_session):
    subject_repository = SQLAlchemySubjectRepository(db_session)
    study_session_repository = SQLAlchemyStudySessionRepository(db_session)

    subject = subject_repository.create(Subject(name="Programming"))

    started_at = datetime(2026, 1, 1, 10, 0, tzinfo=UTC)

    paused_session = StudySession.start(
        subject_id=subject.id,
        started_at=started_at,
    )

    paused_session.pause(datetime(2026, 1, 1, 10, 30, tzinfo=UTC))

    created_session = study_session_repository.create(paused_session)

    active_session = study_session_repository.get_active()

    assert active_session is not None
    assert active_session.id == created_session.id
    assert active_session.status is StudySessionStatus.PAUSED


def test_get_active_returns_none_when_only_finished_sessions_exist(
    db_session,
):
    subject_repository = SQLAlchemySubjectRepository(db_session)
    study_session_repository = SQLAlchemyStudySessionRepository(db_session)

    subject = subject_repository.create(Subject(name="Programming"))

    finished_session = StudySession.start(
        subject_id=subject.id,
        started_at=datetime(2026, 1, 1, 10, 0, tzinfo=UTC),
    )

    finished_session.finish(datetime(2026, 1, 1, 11, 0, tzinfo=UTC))

    study_session_repository.create(finished_session)

    active_session = study_session_repository.get_active()

    assert active_session is None


def test_update_persists_study_session_changes(db_session):
    subject_repository = SQLAlchemySubjectRepository(db_session)
    study_session_repository = SQLAlchemyStudySessionRepository(db_session)

    subject = subject_repository.create(Subject(name="Programming"))

    session = StudySession.start(
        subject_id=subject.id,
        started_at=datetime(2026, 1, 1, 10, 0, tzinfo=UTC),
    )

    created_session = study_session_repository.create(session)

    created_session.finish(datetime(2026, 1, 1, 11, 0, tzinfo=UTC))

    updated_session = study_session_repository.update(created_session)

    assert updated_session is not None
    assert updated_session.id == created_session.id
    assert updated_session.status is StudySessionStatus.FINISHED
    assert updated_session.ended_at == datetime(2026, 1, 1, 11, 0, tzinfo=UTC)
    assert updated_session.duration_seconds == 3600

    retrieved_session = study_session_repository.get_by_id(created_session.id)

    assert retrieved_session is not None
    assert retrieved_session.status is StudySessionStatus.FINISHED
    assert retrieved_session.duration_seconds == 3600


def test_delete_removes_study_session(db_session):
    subject_repository = SQLAlchemySubjectRepository(db_session)
    study_session_repository = SQLAlchemyStudySessionRepository(db_session)

    subject = subject_repository.create(Subject(name="Programming"))

    session = StudySession.start(
        subject_id=subject.id,
        started_at=datetime.now(UTC),
    )

    created_session = study_session_repository.create(session)

    deleted = study_session_repository.delete(created_session.id)

    assert deleted is True
    assert study_session_repository.get_by_id(created_session.id) is None


def test_get_by_id_returns_none_when_session_does_not_exist(db_session):
    repository = SQLAlchemyStudySessionRepository(db_session)

    session = repository.get_by_id(999999)

    assert session is None
