from datetime import datetime

from pydantic import BaseModel, Field, model_validator


class StartSessionDTO(BaseModel):
    subject_id: int = Field(gt=0)
    sub_subject_id: int | None = Field(default=None, gt=0)


class CreateStudySessionDTO(BaseModel):
    subject_id: int = Field(gt=0)
    sub_subject_id: int | None = Field(default=None, gt=0)
    started_at: datetime
    ended_at: datetime

    @model_validator(mode="after")
    def validate_dates(self) -> "CreateStudySessionDTO":
        if self.started_at.tzinfo is None or self.started_at.utcoffset() is None:
            raise ValueError("started_at must include timezone information")

        if self.ended_at.tzinfo is None or self.ended_at.utcoffset() is None:
            raise ValueError("ended_at must include timezone information")

        if self.ended_at < self.started_at:
            raise ValueError("ended_at cannot be earlier than started_at")

        return self


class UpdateStudySessionDTO(BaseModel):
    subject_id: int = Field(gt=0)
    sub_subject_id: int | None = Field(default=None, gt=0)
    started_at: datetime
    ended_at: datetime

    @model_validator(mode="after")
    def validate_dates(self) -> "UpdateStudySessionDTO":
        if self.started_at.tzinfo is None or self.started_at.utcoffset() is None:
            raise ValueError("started_at must include timezone information")

        if self.ended_at.tzinfo is None or self.ended_at.utcoffset() is None:
            raise ValueError("ended_at must include timezone information")

        if self.ended_at < self.started_at:
            raise ValueError("ended_at cannot be earlier than started_at")

        return self
