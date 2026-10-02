from pydantic import BaseModel


class CreateSubjectDTO(BaseModel):
    name: str
    description: str | None = None
