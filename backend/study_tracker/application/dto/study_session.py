from datetime import datetime

from pydantic import BaseModel


class StartSessionDTO(BaseModel):
    subject_id: int
    sub_subject_id: int | None = None


class CreateStudySessionDTO(BaseModel):
    subject_id: int
    sub_subject_id: int | None = None
    started_at: datetime
    ended_at: datetime


class UpdateStudySessionDTO(BaseModel):
    subject_id: int
    sub_subject_id: int | None = None
    started_at: datetime
    ended_at: datetime
