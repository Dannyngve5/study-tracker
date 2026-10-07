from datetime import datetime
from enum import Enum

from study_tracker.domain.exceptions import InvalidStudySessionStateError


class StudySessionStatus(str, Enum):
    RUNNING = "running"
    PAUSED = "paused"
    FINISHED = "finished"


class StudySession:

    def __init__(
        self,
        subject_id: int,
        started_at: datetime,
        sub_subject_id: int | None = None,
        ended_at: datetime | None = None,
        id: int | None = None,
        duration_seconds: int | None = None,
        created_at: datetime | None = None,
        status: StudySessionStatus = StudySessionStatus.RUNNING,
        paused_at: datetime | None = None,
        paused_duration_seconds: int = 0,
    ):
        self.id = id
        self.subject_id = subject_id
        self.sub_subject_id = sub_subject_id
        self.started_at = started_at
        self.ended_at = ended_at
        self.duration_seconds = duration_seconds
        self.created_at = created_at
        self.status = status
        self.paused_at = paused_at
        self.paused_duration_seconds = paused_duration_seconds
        self._validate_state()

    def pause(self, paused_at: datetime) -> None:
        if self.status is not StudySessionStatus.RUNNING:
            raise InvalidStudySessionStateError(
                "Only a running study session can be paused"
            )

        self.status = StudySessionStatus.PAUSED
        self.paused_at = paused_at
        self._validate_state()

    def resume(self, resumed_at: datetime) -> None:
        if self.status is not StudySessionStatus.PAUSED:
            raise InvalidStudySessionStateError(
                "Only a paused study session can be resumed"
            )

        if self.paused_at is None:
            raise InvalidStudySessionStateError(
                "Paused study session does not have a pause timestamp"
            )

        if resumed_at < self.paused_at:
            raise InvalidStudySessionStateError(
                "Resume time cannot be earlier than the pause time"
            )

        self.paused_duration_seconds += int(
            (resumed_at - self.paused_at).total_seconds()
        )

        self.paused_at = None
        self.status = StudySessionStatus.RUNNING

        self._validate_state()

    def finish(self, finish_time: datetime) -> None:
        if self.status is StudySessionStatus.FINISHED:
            raise InvalidStudySessionStateError(
                "This study session is already finished"
            )

        if finish_time < self.started_at:
            raise InvalidStudySessionStateError(
                "Finished time cannot be earlier than the session start time"
            )

        paused_duration_seconds = self.paused_duration_seconds

        if self.status is StudySessionStatus.PAUSED:
            if self.paused_at is None:
                raise InvalidStudySessionStateError(
                    "Paused study session does not have a pause timestamp"
                )

            if finish_time < self.paused_at:
                raise InvalidStudySessionStateError(
                    "Finished time cannot be earlier than the pause time"
                )

            paused_duration_seconds += int(
                (finish_time - self.paused_at).total_seconds()
            )

        self.ended_at = finish_time
        self.paused_duration_seconds = paused_duration_seconds
        self.duration_seconds = max(
            0,
            int((finish_time - self.started_at).total_seconds())
            - paused_duration_seconds,
        )
        self.status = StudySessionStatus.FINISHED
        self.paused_at = None

        self._validate_state()

    def finish_manually(
        self,
        ended_at: datetime,
    ) -> None:
        if ended_at < self.started_at:
            raise InvalidStudySessionStateError(
                "The end date cannot be earlier than the session start date"
            )

        self.ended_at = ended_at
        self.duration_seconds = int((ended_at - self.started_at).total_seconds())
        self.status = StudySessionStatus.FINISHED
        self.paused_at = None
        self.paused_duration_seconds = 0

        self._validate_state()

    def update_manually(
        self,
        subject_id: int,
        started_at: datetime,
        ended_at: datetime,
        sub_subject_id: int | None = None,
    ) -> None:
        if ended_at < started_at:
            raise InvalidStudySessionStateError(
                "The end date cannot be earlier than the session start date"
            )

        self.subject_id = subject_id
        self.sub_subject_id = sub_subject_id
        self.started_at = started_at
        self.ended_at = ended_at
        self.duration_seconds = int((ended_at - started_at).total_seconds())
        self.status = StudySessionStatus.FINISHED
        self.paused_at = None
        self.paused_duration_seconds = 0

        self._validate_state()

    def _validate_state(self) -> None:

        self._validate_timezone(self.started_at, "started_at")

        if self.ended_at is not None:
            self._validate_timezone(self.ended_at, "ended_at")

        if self.paused_at is not None:
            self._validate_timezone(self.paused_at, "paused_at")

        if self.paused_duration_seconds < 0:
            raise InvalidStudySessionStateError("Paused duration cannot be negative")

        if self.duration_seconds is not None and self.duration_seconds < 0:
            raise InvalidStudySessionStateError("Duration cannot be negative")

        if self.status is StudySessionStatus.RUNNING:
            if self.ended_at is not None:
                raise InvalidStudySessionStateError(
                    "A running study session cannot have an end timestamp"
                )

            if self.paused_at is not None:
                raise InvalidStudySessionStateError(
                    "A running study session cannot have a pause timestamp"
                )

        elif self.status is StudySessionStatus.PAUSED:
            if self.ended_at is not None:
                raise InvalidStudySessionStateError(
                    "A paused study session cannot have an end timestamp"
                )

            if self.paused_at is None:
                raise InvalidStudySessionStateError(
                    "A paused study session must have a pause timestamp"
                )

        elif self.status is StudySessionStatus.FINISHED:
            if self.ended_at is None:
                raise InvalidStudySessionStateError(
                    "A finished study session must have an end timestamp"
                )

            if self.duration_seconds is None:
                raise InvalidStudySessionStateError(
                    "A finished study session must have a duration"
                )

            if self.paused_at is not None:
                raise InvalidStudySessionStateError(
                    "A finished study session cannot have a pause timestamp"
                )

    @classmethod
    def start(
        cls,
        subject_id: int,
        started_at: datetime,
        sub_subject_id: int | None = None,
    ) -> "StudySession":
        return cls(
            subject_id=subject_id,
            sub_subject_id=sub_subject_id,
            started_at=started_at,
            status=StudySessionStatus.RUNNING,
            duration_seconds=None,
        )

    @staticmethod
    def _validate_timezone(value: datetime, field_name: str) -> None:
        if value.tzinfo is None or value.utcoffset() is None:
            raise InvalidStudySessionStateError(
                f"{field_name} must include timezone information"
            )
