from datetime import datetime

from pydantic import BaseModel, ConfigDict

from study_tracker.domain.entities.study_session import StudySessionStatus


class StudySessionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    subject_id: int
    sub_subject_id: int | None
    started_at: datetime
    ended_at: datetime | None
    duration_seconds: int | None
    created_at: datetime
    status: StudySessionStatus
    paused_at: datetime | None
    paused_duration_seconds: int
