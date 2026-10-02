from datetime import datetime


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
    ):
        self.id = id
        self.subject_id = subject_id
        self.sub_subject_id = sub_subject_id
        self.started_at = started_at
        self.ended_at = ended_at
        self.duration_seconds = duration_seconds
        self.created_at = created_at
