from pydantic import BaseModel, Field


class CreateSubSubjectDTO(BaseModel):
    subject_id: int = Field(gt=0)
    name: str = Field(min_length=1, max_length=100)
    description: str | None = None


class UpdateSubSubjectDTO(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    description: str | None = None
