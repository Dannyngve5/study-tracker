from typing import Annotated

from pydantic import BaseModel, StringConstraints

SubjectName = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True,
        min_length=1,
        max_length=100,
    ),
]


class CreateSubjectDTO(BaseModel):
    name: SubjectName
    description: str | None = None


class UpdateSubjectDTO(BaseModel):
    name: SubjectName
    description: str | None = None
