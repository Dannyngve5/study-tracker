import pytest
from sqlalchemy.exc import IntegrityError
from study_tracker.domain.enums.study_session_status import StudySessionStatus
from study_tracker.infrastructure.database.models.study_session import (
    StudySession as StudySessionModel,
)
from study_tracker.infrastructure.database.models.subject import (
    Subject as SubjectModel,
)


def test_database_rejects_negative_duration(db_session):
    subject = SubjectModel(name="Programming")

    db_session.add(subject)
    db_session.flush()

    session = StudySessionModel(
        subject_id=subject.id,
        started_at="2026-01-01T10:00:00+00:00",
        status=StudySessionStatus.RUNNING,
        duration_seconds=-1,
        paused_duration_seconds=0,
    )

    db_session.add(session)

    with pytest.raises(IntegrityError):
        db_session.flush()


def test_database_rejects_negative_paused_duration(db_session):
    subject = SubjectModel(name="Programming")

    db_session.add(subject)
    db_session.flush()

    session = StudySessionModel(
        subject_id=subject.id,
        started_at="2026-01-01T10:00:00+00:00",
        status=StudySessionStatus.RUNNING,
        duration_seconds=0,
        paused_duration_seconds=-1,
    )

    db_session.add(session)

    with pytest.raises(IntegrityError):
        db_session.flush()


def test_database_rejects_finished_session_without_ended_at(db_session):
    subject = SubjectModel(name="Programming")

    db_session.add(subject)
    db_session.flush()

    session = StudySessionModel(
        subject_id=subject.id,
        started_at="2026-01-01T10:00:00+00:00",
        status=StudySessionStatus.FINISHED,
        duration_seconds=3600,
        ended_at=None,
        paused_duration_seconds=0,
    )

    db_session.add(session)

    with pytest.raises(IntegrityError):
        db_session.flush()


def test_database_rejects_finished_session_without_duration(db_session):
    subject = SubjectModel(name="Programming")

    db_session.add(subject)
    db_session.flush()

    session = StudySessionModel(
        subject_id=subject.id,
        started_at="2026-01-01T10:00:00+00:00",
        status=StudySessionStatus.FINISHED,
        duration_seconds=None,
        ended_at="2026-01-01T11:00:00+00:00",
        paused_duration_seconds=0,
    )

    db_session.add(session)

    with pytest.raises(IntegrityError):
        db_session.flush()


def test_database_rejects_paused_session_without_paused_at(db_session):
    subject = SubjectModel(name="Programming")

    db_session.add(subject)
    db_session.flush()

    session = StudySessionModel(
        subject_id=subject.id,
        started_at="2026-01-01T10:00:00+00:00",
        status=StudySessionStatus.PAUSED,
        duration_seconds=0,
        paused_at=None,
        paused_duration_seconds=0,
    )

    db_session.add(session)

    with pytest.raises(IntegrityError):
        db_session.flush()
