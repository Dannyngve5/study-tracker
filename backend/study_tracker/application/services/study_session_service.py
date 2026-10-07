from datetime import datetime, timezone

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
from study_tracker.domain.entities.study_session import (
    StudySession,
    StudySessionStatus,
)
from study_tracker.domain.exceptions import InvalidStudySessionStateError
from study_tracker.domain.repositories.unit_of_work import UnitOfWork


class StudySessionService:

    def __init__(self, unit_of_work: UnitOfWork):
        self.unit_of_work = unit_of_work

    def start_session(self, dto: StartSessionDTO) -> StudySession:
        now = datetime.now(timezone.utc)

        with self.unit_of_work as uow:
            self._validate_subject_and_sub_subject(
                uow,
                dto.subject_id,
                dto.sub_subject_id,
            )

            self._ensure_no_active_session(uow)

            study_session = StudySession(
                subject_id=dto.subject_id,
                sub_subject_id=dto.sub_subject_id,
                started_at=now,
                status=StudySessionStatus.RUNNING,
                duration_seconds=0,
            )

            return uow.study_sessions.create(study_session)

    def create_session(self, dto: CreateStudySessionDTO) -> StudySession:
        duration_seconds = self._calculate_duration(
            dto.started_at,
            dto.ended_at,
        )

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
                ended_at=dto.ended_at,
                duration_seconds=duration_seconds,
                status=StudySessionStatus.FINISHED,
            )

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
        duration_seconds = self._calculate_duration(
            dto.started_at,
            dto.ended_at,
        )

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

            study_session.subject_id = dto.subject_id
            study_session.sub_subject_id = dto.sub_subject_id
            study_session.started_at = dto.started_at
            study_session.ended_at = dto.ended_at
            study_session.duration_seconds = duration_seconds

            updated_session = uow.study_sessions.update(study_session)

            if updated_session is None:
                raise StudySessionNotFoundError(study_session_id)

            return updated_session

    def pause_session(self, study_session_id: int) -> StudySession:
        now = datetime.now(timezone.utc)

        with self.unit_of_work as uow:
            study_session = uow.study_sessions.get_by_id(study_session_id)

            if study_session is None:
                raise StudySessionNotFoundError(study_session_id)

            if study_session.status is not StudySessionStatus.RUNNING:
                raise InvalidStudySessionStateError(
                    "Only a running study session can be paused"
                )

            study_session.status = StudySessionStatus.PAUSED
            study_session.paused_at = now

            updated_session = uow.study_sessions.update(study_session)

            if updated_session is None:
                raise StudySessionNotFoundError(study_session_id)

            return updated_session

    def resume_session(self, study_session_id: int) -> StudySession:
        now = datetime.now(timezone.utc)

        with self.unit_of_work as uow:
            study_session = uow.study_sessions.get_by_id(study_session_id)

            if study_session is None:
                raise StudySessionNotFoundError(study_session_id)

            if study_session.status is not StudySessionStatus.PAUSED:
                raise InvalidStudySessionStateError(
                    "Only a paused study session can be resumed"
                )

            if study_session.paused_at is None:
                raise InvalidStudySessionStateError(
                    "Paused study session does not have a pause timestamp"
                )

            elapsed_pause_seconds = int((now - study_session.paused_at).total_seconds())

            study_session.paused_duration_seconds += elapsed_pause_seconds
            study_session.paused_at = None
            study_session.status = StudySessionStatus.RUNNING

            updated_session = uow.study_sessions.update(study_session)

            if updated_session is None:
                raise StudySessionNotFoundError(study_session_id)

            return updated_session

    def stop_session(
        self,
        study_session_id: int,
        ended_at: datetime | None = None,
    ) -> StudySession:
        finish_time = ended_at or datetime.now(timezone.utc)

        with self.unit_of_work as uow:
            study_session = uow.study_sessions.get_by_id(study_session_id)

            if study_session is None:
                raise StudySessionNotFoundError(study_session_id)

            if study_session.status is StudySessionStatus.FINISHED:
                raise InvalidStudySessionStateError(
                    "This study session is already finished"
                )

            if finish_time < study_session.started_at:
                raise InvalidStudySessionStateError(
                    "Finished time cannot be earlier than the session start time"
                )

            if (
                study_session.status is StudySessionStatus.PAUSED
                and study_session.paused_at is not None
                and finish_time < study_session.paused_at
            ):
                raise InvalidStudySessionStateError(
                    "Finished time cannot be earlier than the pause time"
                )

            paused_duration_seconds = study_session.paused_duration_seconds

            if (
                study_session.status is StudySessionStatus.PAUSED
                and study_session.paused_at is not None
            ):
                paused_duration_seconds += int(
                    (finish_time - study_session.paused_at).total_seconds()
                )

            elapsed_total_seconds = max(
                0,
                int((finish_time - study_session.started_at).total_seconds())
                - paused_duration_seconds,
            )

            study_session.ended_at = finish_time
            study_session.duration_seconds = elapsed_total_seconds
            study_session.paused_duration_seconds = paused_duration_seconds
            study_session.status = StudySessionStatus.FINISHED
            study_session.paused_at = None

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
    def _calculate_duration(
        started_at: datetime,
        ended_at: datetime,
    ) -> int:
        if ended_at < started_at:
            raise InvalidStudySessionStateError(
                "The end date cannot be earlier than the start date"
            )

        return int((ended_at - started_at).total_seconds())

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
