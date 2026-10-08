from datetime import UTC, datetime

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
from study_tracker.domain.entities.study_session import StudySession
from study_tracker.domain.enums.study_session_status import StudySessionStatus
from study_tracker.domain.exceptions import InvalidStudySessionStateError
from study_tracker.domain.repositories.unit_of_work import UnitOfWork


class StudySessionService:

    def __init__(self, unit_of_work: UnitOfWork):
        self.unit_of_work = unit_of_work

    def start_session(self, dto: StartSessionDTO) -> StudySession:
        now = datetime.now(UTC)

        with self.unit_of_work as uow:
            self._validate_subject_and_sub_subject(
                uow,
                dto.subject_id,
                dto.sub_subject_id,
            )

            self._ensure_no_active_session(uow)

            study_session = StudySession.start(
                subject_id=dto.subject_id,
                sub_subject_id=dto.sub_subject_id,
                started_at=now,
            )

            return uow.study_sessions.create(study_session)

    def create_session(self, dto: CreateStudySessionDTO) -> StudySession:
        with self.unit_of_work as uow:
            self._validate_subject_and_sub_subject(
                uow,
                dto.subject_id,
                dto.sub_subject_id,
            )

            study_session = StudySession(
                subject_id=dto.subject_id,
                sub_subject_id=dto.sub_subject_id,
                started_at=dto.started_at,
            )

            study_session.finish_manually(dto.ended_at)

            return uow.study_sessions.create(study_session)

    def get_session(self, study_session_id: int) -> StudySession:
        with self.unit_of_work as uow:
            study_session = uow.study_sessions.get_by_id(study_session_id)

            if study_session is None:
                raise StudySessionNotFoundError(study_session_id)

            return study_session

    def get_sessions(self) -> list[StudySession]:
        with self.unit_of_work as uow:
            return uow.study_sessions.get_all()

    def get_active_session(self) -> StudySession | None:
        with self.unit_of_work as uow:
            return uow.study_sessions.get_active()

    def update_session(
        self,
        study_session_id: int,
        dto: UpdateStudySessionDTO,
    ) -> StudySession:
        with self.unit_of_work as uow:
            study_session = uow.study_sessions.get_by_id(study_session_id)

            if study_session is None:
                raise StudySessionNotFoundError(study_session_id)

            if study_session.status is not StudySessionStatus.FINISHED:
                raise InvalidStudySessionStateError(
                    "Only finished study sessions can be updated"
                )

            self._validate_subject_and_sub_subject(
                uow,
                dto.subject_id,
                dto.sub_subject_id,
            )

            study_session.update_manually(
                subject_id=dto.subject_id,
                sub_subject_id=dto.sub_subject_id,
                started_at=dto.started_at,
                ended_at=dto.ended_at,
            )

            updated_session = uow.study_sessions.update(study_session)

            if updated_session is None:
                raise StudySessionNotFoundError(study_session_id)

            return updated_session

    def pause_session(self, study_session_id: int) -> StudySession:
        now = datetime.now(UTC)

        with self.unit_of_work as uow:
            study_session = uow.study_sessions.get_by_id(study_session_id)

            if study_session is None:
                raise StudySessionNotFoundError(study_session_id)

            study_session.pause(now)

            updated_session = uow.study_sessions.update(study_session)

            if updated_session is None:
                raise StudySessionNotFoundError(study_session_id)

            return updated_session

    def resume_session(self, study_session_id: int) -> StudySession:
        now = datetime.now(UTC)

        with self.unit_of_work as uow:
            study_session = uow.study_sessions.get_by_id(study_session_id)

            if study_session is None:
                raise StudySessionNotFoundError(study_session_id)

            study_session.resume(now)

            updated_session = uow.study_sessions.update(study_session)

            if updated_session is None:
                raise StudySessionNotFoundError(study_session_id)

            return updated_session

    def stop_session(
        self, study_session_id: int, ended_at: datetime | None = None
    ) -> StudySession:
        finish_time = ended_at or datetime.now(UTC)

        with self.unit_of_work as uow:
            study_session = uow.study_sessions.get_by_id(study_session_id)

            if study_session is None:
                raise StudySessionNotFoundError(study_session_id)

            study_session.finish(finish_time)

            updated_session = uow.study_sessions.update(study_session)

            if updated_session is None:
                raise StudySessionNotFoundError(study_session_id)

            return updated_session

    def delete(self, study_session_id: int) -> None:
        with self.unit_of_work as uow:
            deleted = uow.study_sessions.delete(study_session_id)

            if not deleted:
                raise StudySessionNotFoundError(study_session_id)

    @staticmethod
    def _validate_subject_and_sub_subject(
        uow: UnitOfWork,
        subject_id: int,
        sub_subject_id: int | None,
    ) -> None:
        subject = uow.subjects.get_by_id(subject_id)

        if subject is None:
            raise SubjectNotFoundError(subject_id)

        if sub_subject_id is None:
            return

        sub_subject = uow.sub_subjects.get_by_id(sub_subject_id)

        if sub_subject is None:
            raise SubSubjectNotFoundError(sub_subject_id)

        if sub_subject.subject_id != subject_id:
            raise SubSubjectDoesNotBelongToSubjectError(
                sub_subject_id,
                subject_id,
            )

    @staticmethod
    def _ensure_no_active_session(uow: UnitOfWork) -> None:
        active_session = uow.study_sessions.get_active()

        if active_session is not None:
            raise StudySessionAlreadyActiveError(
                active_session.subject_id,
                active_session.sub_subject_id,
            )
