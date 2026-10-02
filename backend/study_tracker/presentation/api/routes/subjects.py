from fastapi import APIRouter, Depends, status

from study_tracker.application.dto.subject import CreateSubjectDTO
from study_tracker.application.services.subject_service import SubjectService
from study_tracker.presentation.api.dependencies import get_subject_service

router = APIRouter(
    prefix="/subjects",
    tags=["Subjects"],
)


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_subject(
    dto: CreateSubjectDTO,
    service: SubjectService = Depends(get_subject_service),
):
    return service.create(dto)
