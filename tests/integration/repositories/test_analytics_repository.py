from datetime import UTC, datetime, timedelta

from study_tracker.domain.entities.study_session import StudySession
from study_tracker.domain.entities.subject import Subject
from study_tracker.domain.enums.group_by import GroupBy
from study_tracker.infrastructure.repositories.SQLAlchemy_analytics_repository import (
    SQLAlchemyAnalyticsRepository,
)
from study_tracker.infrastructure.repositories.SQLAlchemy_study_session_repository import (
    SQLAlchemyStudySessionRepository,
)
from study_tracker.infrastructure.repositories.SQLAlchemy_subject_repository import (
    SQLAlchemySubjectRepository,
)


def create_finished_session(
    session_repository,
    subject_id: int,
    started_at: datetime,
    duration_seconds: int,
):
    study_session = StudySession.start(
        subject_id=subject_id,
        started_at=started_at,
    )
    study_session.finish(started_at + timedelta(seconds=duration_seconds))

    return session_repository.create(study_session)


def test_get_total_filters_by_date_range_and_subject(db_session):
    subjects = SQLAlchemySubjectRepository(db_session)
    sessions = SQLAlchemyStudySessionRepository(db_session)
    analytics = SQLAlchemyAnalyticsRepository(db_session)
    python = subjects.create(Subject(name="Python"))
    math = subjects.create(Subject(name="Math"))

    create_finished_session(
        sessions,
        python.id,
        datetime(2026, 10, 8, 10, 0, tzinfo=UTC),
        1800,
    )
    create_finished_session(
        sessions,
        python.id,
        datetime(2026, 10, 9, 0, 0, tzinfo=UTC),
        3600,
    )
    create_finished_session(
        sessions,
        math.id,
        datetime(2026, 10, 8, 11, 0, tzinfo=UTC),
        7200,
    )

    total = analytics.get_total(
        start_date=datetime(2026, 10, 8, tzinfo=UTC),
        end_date=datetime(2026, 10, 9, tzinfo=UTC),
        subject_id=python.id,
    )

    assert total == 1800


def test_get_top_subjects_sorts_by_total_duration(db_session):
    subjects = SQLAlchemySubjectRepository(db_session)
    sessions = SQLAlchemyStudySessionRepository(db_session)
    analytics = SQLAlchemyAnalyticsRepository(db_session)
    python = subjects.create(Subject(name="Python"))
    math = subjects.create(Subject(name="Math"))

    create_finished_session(
        sessions,
        python.id,
        datetime(2026, 10, 8, 10, 0, tzinfo=UTC),
        3600,
    )
    create_finished_session(
        sessions,
        python.id,
        datetime(2026, 10, 8, 12, 0, tzinfo=UTC),
        1800,
    )
    create_finished_session(
        sessions,
        math.id,
        datetime(2026, 10, 8, 11, 0, tzinfo=UTC),
        2400,
    )

    top_subjects = analytics.get_top_subjects(limit=1)

    assert top_subjects == [("Python", 5400)]


def test_get_recent_activity_returns_latest_sessions_with_subject_names(db_session):
    subjects = SQLAlchemySubjectRepository(db_session)
    sessions = SQLAlchemyStudySessionRepository(db_session)
    analytics = SQLAlchemyAnalyticsRepository(db_session)
    python = subjects.create(Subject(name="Python"))

    create_finished_session(
        sessions,
        python.id,
        datetime(2026, 10, 8, 10, 0, tzinfo=UTC),
        1800,
    )
    create_finished_session(
        sessions,
        python.id,
        datetime(2026, 10, 8, 12, 0, tzinfo=UTC),
        2400,
    )

    recent = analytics.get_recent_activity(limit=1)

    assert len(recent) == 1
    assert recent[0].subject_name == "Python"
    assert recent[0].started_at == datetime(2026, 10, 8, 12, 0, tzinfo=UTC)
    assert recent[0].duration_seconds == 2400


def test_get_sessions_and_count_apply_same_filters_and_stable_pagination(
    db_session,
):
    subjects = SQLAlchemySubjectRepository(db_session)
    sessions = SQLAlchemyStudySessionRepository(db_session)
    analytics = SQLAlchemyAnalyticsRepository(db_session)
    python = subjects.create(Subject(name="Python"))
    math = subjects.create(Subject(name="Math"))
    repeated_start = datetime(2026, 10, 8, 10, 0, tzinfo=UTC)

    first = create_finished_session(sessions, python.id, repeated_start, 1800)
    second = create_finished_session(sessions, python.id, repeated_start, 2400)
    create_finished_session(
        sessions,
        math.id,
        datetime(2026, 10, 8, 11, 0, tzinfo=UTC),
        3600,
    )

    filters = {
        "subject_id": python.id,
        "start_date": datetime(2026, 10, 8, tzinfo=UTC),
        "end_date": datetime(2026, 10, 9, tzinfo=UTC),
    }
    page = analytics.get_sessions(**filters, offset=0, limit=1)

    assert analytics.count_sessions(**filters) == 2
    assert len(page) == 1
    assert page[0].id == max(first.id, second.id)


def test_get_grouped_sessions_aggregates_by_local_calendar_day(db_session):
    subjects = SQLAlchemySubjectRepository(db_session)
    sessions = SQLAlchemyStudySessionRepository(db_session)
    analytics = SQLAlchemyAnalyticsRepository(db_session)
    python = subjects.create(Subject(name="Python"))

    create_finished_session(
        sessions,
        python.id,
        datetime(2026, 1, 1, 2, 0, tzinfo=UTC),
        1800,
    )
    create_finished_session(
        sessions,
        python.id,
        datetime(2026, 1, 1, 23, 0, tzinfo=UTC),
        2400,
    )
    create_finished_session(
        sessions,
        python.id,
        datetime(2026, 1, 2, 1, 0, tzinfo=UTC),
        600,
    )

    groups = analytics.get_grouped_sessions(
        timezone="America/New_York",
        group_by=GroupBy.DAY,
    )

    assert len(groups) == 2
    assert groups[0].period_start.date().isoformat() == "2026-01-01"
    assert groups[0].period_end.date().isoformat() == "2026-01-02"
    assert groups[0].duration_seconds == 3000
    assert groups[0].session_count == 2
    assert groups[1].period_start.date().isoformat() == "2025-12-31"
    assert groups[1].duration_seconds == 1800
    assert groups[1].session_count == 1
