from datetime import datetime, timezone

from study_tracker.domain.entities.study_session import (
    StudySession,
    StudySessionStatus,
)

import pytest

from study_tracker.domain.exceptions import InvalidStudySessionStateError


def test_new_study_session_starts_as_running():
    session = StudySession.start(
        subject_id=1,
        started_at=datetime.now(timezone.utc),
    )

    assert session.status is StudySessionStatus.RUNNING


def test_running_study_session_can_be_paused():
    started_at = datetime(2026, 10, 7, 10, 0, tzinfo=timezone.utc)
    paused_at = datetime(2026, 10, 7, 10, 30, tzinfo=timezone.utc)

    session = StudySession.start(
        subject_id=1,
        started_at=started_at,
    )

    session.pause(paused_at)

    assert session.status is StudySessionStatus.PAUSED
    assert session.paused_at == paused_at


def test_paused_study_session_can_be_resumed():
    started_at = datetime(2026, 10, 7, 10, 0, tzinfo=timezone.utc)
    paused_at = datetime(2026, 10, 7, 10, 30, tzinfo=timezone.utc)
    resumed_at = datetime(2026, 10, 7, 10, 40, tzinfo=timezone.utc)

    session = StudySession.start(
        subject_id=1,
        started_at=started_at,
    )

    session.pause(paused_at)
    session.resume(resumed_at)

    assert session.status is StudySessionStatus.RUNNING
    assert session.paused_at is None
    assert session.paused_duration_seconds == 600


def test_running_study_session_can_be_finished():
    started_at = datetime(2026, 10, 7, 10, 0, tzinfo=timezone.utc)
    finished_at = datetime(2026, 10, 7, 10, 30, tzinfo=timezone.utc)

    session = StudySession.start(
        subject_id=1,
        started_at=started_at,
    )

    session.finish(finished_at)

    assert session.status is StudySessionStatus.FINISHED
    assert session.ended_at == finished_at
    assert session.duration_seconds == 1800


def test_paused_study_session_can_be_finished():
    started_at = datetime(2026, 10, 7, 10, 0, tzinfo=timezone.utc)
    paused_at = datetime(2026, 10, 7, 10, 30, tzinfo=timezone.utc)
    finished_at = datetime(2026, 10, 7, 11, 0, tzinfo=timezone.utc)

    session = StudySession.start(
        subject_id=1,
        started_at=started_at,
    )

    session.pause(paused_at)
    session.finish(finished_at)

    assert session.status is StudySessionStatus.FINISHED
    assert session.ended_at == finished_at
    assert session.duration_seconds == 1800
    assert session.paused_duration_seconds == 1800


def test_finished_study_session_rejects_invalid_state_transitions():
    started_at = datetime(2026, 10, 7, 10, 0, tzinfo=timezone.utc)
    finished_at = datetime(2026, 10, 7, 10, 30, tzinfo=timezone.utc)

    session = StudySession.start(
        subject_id=1,
        started_at=started_at,
    )

    session.finish(finished_at)

    with pytest.raises(InvalidStudySessionStateError):
        session.pause(finished_at)

    with pytest.raises(InvalidStudySessionStateError):
        session.resume(finished_at)

    with pytest.raises(InvalidStudySessionStateError):
        session.finish(finished_at)


def test_study_session_rejects_finish_before_start():
    started_at = datetime(2026, 10, 7, 10, 0, tzinfo=timezone.utc)
    finished_at = datetime(2026, 10, 7, 9, 0, tzinfo=timezone.utc)

    session = StudySession.start(
        subject_id=1,
        started_at=started_at,
    )

    with pytest.raises(InvalidStudySessionStateError):
        session.finish(finished_at)


def test_study_session_rejects_negative_duration():
    started_at = datetime(2026, 10, 7, 10, 0, tzinfo=timezone.utc)

    with pytest.raises(InvalidStudySessionStateError):
        StudySession(
            subject_id=1,
            started_at=started_at,
            duration_seconds=-1,
        )


def test_study_session_rejects_naive_started_at():
    started_at = datetime(2026, 10, 7, 10, 0)

    with pytest.raises(InvalidStudySessionStateError):
        StudySession.start(
            subject_id=1,
            started_at=started_at,
        )
