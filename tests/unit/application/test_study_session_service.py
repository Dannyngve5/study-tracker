from datetime import UTC, datetime

import pytest
from study_tracker.application.dto.study_session import (
    CreateStudySessionDTO,
    StartSessionDTO,
    UpdateStudySessionDTO,
)
from study_tracker.application.exceptions import (
    StudySessionAlreadyActiveError,
    StudySessionNotFoundError,
    SubjectNotFoundError,
    SubSubjectDoesNotBelongToSubjectError,
    SubSubjectNotFoundError,
)
from study_tracker.application.services.study_session_service import (
    StudySessionService,
)
from study_tracker.domain.entities.study_session import StudySession
from study_tracker.domain.entities.subject import Subject
from study_tracker.domain.enums.study_session_status import StudySessionStatus
from study_tracker.domain.exceptions import InvalidStudySessionStateError


class FakeSubjectRepository:
    def __init__(self, subjects=None):
        self.subjects = subjects or {
            1: Subject(id=1, name="Programming"),
        }

    def get_by_id(self, subject_id: int):
        return self.subjects.get(subject_id)


class FakeSubSubjectRepository:
    def __init__(self, sub_subjects=None):
        self.sub_subjects = sub_subjects or {}

    def get_by_id(self, sub_subject_id: int):
        return self.sub_subjects.get(sub_subject_id)


class FakeStudySessionRepository:
    def __init__(self, active_session=None, sessions=None):
        self.active_session = active_session
        self.sessions = sessions or []

    def get_active(self):
        return self.active_session

    def get_by_id(self, study_session_id: int):
        for session in self.sessions:
            if session.id == study_session_id:
                return session

        return None

    def get_all(self):
        return self.sessions

    def create(self, study_session):
        self.sessions.append(study_session)
        return study_session

    def update(self, study_session):
        return study_session

    def delete(self, study_session_id: int):
        for session in self.sessions:
            if session.id == study_session_id:
                self.sessions.remove(session)
                return True

        return False


class FakeUnitOfWork:
    def __init__(
        self,
        active_session=None,
        subjects=None,
        sub_subjects=None,
        sessions=None,
    ):
        self.active_session = active_session
        self.subjects_data = subjects
        self.sub_subjects_data = sub_subjects
        self.sessions = sessions or []

    def __enter__(self):
        self.subjects = FakeSubjectRepository(self.subjects_data)
        self.sub_subjects = FakeSubSubjectRepository(self.sub_subjects_data)
        self.study_sessions = FakeStudySessionRepository(
            active_session=self.active_session,
            sessions=self.sessions,
        )

        return self

    def __exit__(self, exc_type, exc_value, traceback):
        pass


def test_start_session_creates_running_session():
    service = StudySessionService(FakeUnitOfWork())

    dto = StartSessionDTO(subject_id=1)

    session = service.start_session(dto)

    assert session.subject_id == 1
    assert session.status is StudySessionStatus.RUNNING
    assert session.started_at.tzinfo is not None


def test_start_session_rejects_when_session_is_already_active():
    active_session = StudySession.start(
        subject_id=1,
        started_at=datetime.now(UTC),
    )

    service = StudySessionService(FakeUnitOfWork(active_session=active_session))

    dto = StartSessionDTO(subject_id=1)

    with pytest.raises(StudySessionAlreadyActiveError):
        service.start_session(dto)


def test_start_session_rejects_when_subject_does_not_exist():
    service = StudySessionService(FakeUnitOfWork(subjects={}))

    dto = StartSessionDTO(subject_id=999)

    with pytest.raises(SubjectNotFoundError):
        service.start_session(dto)


def test_start_session_rejects_when_sub_subject_does_not_exist():
    service = StudySessionService(FakeUnitOfWork(sub_subjects={}))

    dto = StartSessionDTO(
        subject_id=1,
        sub_subject_id=999,
    )

    with pytest.raises(SubSubjectNotFoundError):
        service.start_session(dto)


def test_start_session_rejects_sub_subject_from_different_subject():
    sub_subject = type(
        "FakeSubSubject",
        (),
        {
            "id": 2,
            "subject_id": 2,
        },
    )()

    service = StudySessionService(FakeUnitOfWork(sub_subjects={2: sub_subject}))

    dto = StartSessionDTO(
        subject_id=1,
        sub_subject_id=2,
    )

    with pytest.raises(SubSubjectDoesNotBelongToSubjectError):
        service.start_session(dto)


def test_pause_session_pauses_running_session():
    session = StudySession.start(
        subject_id=1,
        started_at=datetime.now(UTC),
    )
    session.id = 1

    service = StudySessionService(FakeUnitOfWork(sessions=[session]))

    result = service.pause_session(1)

    assert result.status is StudySessionStatus.PAUSED
    assert result.paused_at is not None


def test_resume_session_resumes_paused_session():
    started_at = datetime.now(UTC)

    session = StudySession.start(
        subject_id=1,
        started_at=started_at,
    )
    session.id = 1
    session.pause(started_at.replace(microsecond=0))

    service = StudySessionService(FakeUnitOfWork(sessions=[session]))

    result = service.resume_session(1)

    assert result.status is StudySessionStatus.RUNNING
    assert result.paused_at is None


def test_stop_session_finishes_running_session():
    started_at = datetime.now(UTC)

    session = StudySession.start(
        subject_id=1,
        started_at=started_at,
    )
    session.id = 1

    service = StudySessionService(FakeUnitOfWork(sessions=[session]))

    result = service.stop_session(1)

    assert result.status is StudySessionStatus.FINISHED
    assert result.ended_at is not None
    assert result.duration_seconds is not None


def test_create_session_creates_finished_session():
    started_at = datetime(2026, 1, 1, 10, 0, tzinfo=UTC)
    ended_at = datetime(2026, 1, 1, 11, 0, tzinfo=UTC)

    service = StudySessionService(FakeUnitOfWork())

    dto = CreateStudySessionDTO(
        subject_id=1,
        started_at=started_at,
        ended_at=ended_at,
    )

    session = service.create_session(dto)

    assert session.status is StudySessionStatus.FINISHED
    assert session.ended_at == ended_at
    assert session.duration_seconds == 3600


def test_get_session_returns_existing_session():
    session = StudySession.start(
        subject_id=1,
        started_at=datetime.now(UTC),
    )
    session.id = 1

    service = StudySessionService(FakeUnitOfWork(sessions=[session]))

    result = service.get_session(1)

    assert result is session


def test_get_session_rejects_when_session_does_not_exist():
    service = StudySessionService(FakeUnitOfWork())

    with pytest.raises(StudySessionNotFoundError):
        service.get_session(999)


def test_get_sessions_returns_all_sessions():
    session_1 = StudySession.start(
        subject_id=1,
        started_at=datetime.now(UTC),
    )
    session_1.id = 1

    session_2 = StudySession.start(
        subject_id=1,
        started_at=datetime.now(UTC),
    )
    session_2.id = 2

    service = StudySessionService(FakeUnitOfWork(sessions=[session_1, session_2]))

    result = service.get_sessions()

    assert result == [session_1, session_2]


def test_get_active_session_returns_active_session():
    active_session = StudySession.start(
        subject_id=1,
        started_at=datetime.now(UTC),
    )

    service = StudySessionService(FakeUnitOfWork(active_session=active_session))

    result = service.get_active_session()

    assert result is active_session


def test_get_active_session_returns_none_when_there_is_no_active_session():
    service = StudySessionService(FakeUnitOfWork())

    result = service.get_active_session()

    assert result is None


def test_update_session_updates_finished_session():
    original_started_at = datetime(
        2026,
        1,
        1,
        10,
        0,
        tzinfo=UTC,
    )
    original_ended_at = datetime(
        2026,
        1,
        1,
        11,
        0,
        tzinfo=UTC,
    )

    session = StudySession(
        subject_id=1,
        started_at=original_started_at,
    )
    session.id = 1
    session.finish_manually(original_ended_at)

    new_started_at = datetime(
        2026,
        1,
        2,
        14,
        0,
        tzinfo=UTC,
    )
    new_ended_at = datetime(
        2026,
        1,
        2,
        16,
        0,
        tzinfo=UTC,
    )

    service = StudySessionService(FakeUnitOfWork(sessions=[session]))

    dto = UpdateStudySessionDTO(
        subject_id=1,
        started_at=new_started_at,
        ended_at=new_ended_at,
    )

    result = service.update_session(1, dto)

    assert result.started_at == new_started_at
    assert result.ended_at == new_ended_at
    assert result.duration_seconds == 7200
    assert result.status is StudySessionStatus.FINISHED


def test_update_session_rejects_non_finished_session():
    session = StudySession.start(
        subject_id=1,
        started_at=datetime.now(UTC),
    )
    session.id = 1

    service = StudySessionService(FakeUnitOfWork(sessions=[session]))

    dto = UpdateStudySessionDTO(
        subject_id=1,
        started_at=datetime(2026, 1, 1, 10, 0, tzinfo=UTC),
        ended_at=datetime(2026, 1, 1, 11, 0, tzinfo=UTC),
    )

    with pytest.raises(InvalidStudySessionStateError):
        service.update_session(1, dto)


def test_delete_session_deletes_existing_session():
    session = StudySession.start(
        subject_id=1,
        started_at=datetime.now(UTC),
    )
    session.id = 1

    service = StudySessionService(FakeUnitOfWork(sessions=[session]))

    service.delete(1)


def test_delete_session_rejects_when_session_does_not_exist():
    service = StudySessionService(FakeUnitOfWork())

    with pytest.raises(StudySessionNotFoundError):
        service.delete(999)
