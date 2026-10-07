from datetime import datetime
from enum import Enum


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
