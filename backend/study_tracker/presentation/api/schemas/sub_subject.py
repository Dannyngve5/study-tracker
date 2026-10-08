from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class SubSubjectCreateRequest(BaseModel):
    subject_id: int = Field(gt=0)
    name: str = Field(min_length=1, max_length=100)
    description: str | None = None


class SubSubjectUpdateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    description: str | None = None


class SubSubjectResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    subject_id: int
    name: str
    description: str | None
    created_at: datetime
