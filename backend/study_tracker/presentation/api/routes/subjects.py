from typing import Annotated

from fastapi import APIRouter, Depends, Path, status

from study_tracker.application.dto.subject import (
    CreateSubjectDTO,
    UpdateSubjectDTO,
)
from study_tracker.application.services.subject_service import SubjectService
from study_tracker.presentation.api.dependencies import get_subject_service
from study_tracker.presentation.api.schemas.subject import SubjectResponse

router = APIRouter(
    prefix="/subjects",
    tags=["Subjects"],
)


@router.post(
    "/",
    response_model=SubjectResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_subject(
    dto: CreateSubjectDTO,
    service: Annotated[SubjectService, Depends(get_subject_service)],
) -> SubjectResponse:
    return service.create(dto)


@router.get(
    "/",
    response_model=list[SubjectResponse],
)
def get_subjects(
    service: Annotated[SubjectService, Depends(get_subject_service)],
) -> list[SubjectResponse]:
    return service.get_all()


@router.get(
    "/{subject_id}",
    response_model=SubjectResponse,
)
def get_subject(
    subject_id: Annotated[int, Path(gt=0)],
    service: Annotated[SubjectService, Depends(get_subject_service)],
) -> SubjectResponse:
    return service.get_by_id(subject_id)


@router.put(
    "/{subject_id}",
    response_model=SubjectResponse,
)
def update_subject(
    subject_id: Annotated[int, Path(gt=0)],
    dto: UpdateSubjectDTO,
    service: Annotated[SubjectService, Depends(get_subject_service)],
) -> SubjectResponse:
    return service.update(subject_id, dto)


@router.delete(
    "/{subject_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_subject(
    subject_id: Annotated[int, Path(gt=0)],
    service: Annotated[SubjectService, Depends(get_subject_service)],
) -> None:
    service.delete(subject_id)
