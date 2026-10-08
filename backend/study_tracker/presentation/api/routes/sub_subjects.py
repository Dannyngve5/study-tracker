from typing import Annotated

from fastapi import APIRouter, Depends, status

from study_tracker.application.dto.sub_subject import (
    CreateSubSubjectDTO,
    UpdateSubSubjectDTO,
)
from study_tracker.application.services.sub_subject_service import (
    SubSubjectService,
)
from study_tracker.presentation.api.dependencies import (
    get_sub_subject_service,
)
from study_tracker.presentation.api.schemas.sub_subject import (
    SubSubjectCreateRequest,
    SubSubjectResponse,
    SubSubjectUpdateRequest,
)

router = APIRouter(
    prefix="/sub-subjects",
    tags=["SubSubjects"],
)


@router.post(
    "/",
    response_model=SubSubjectResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_sub_subject(
    request: SubSubjectCreateRequest,
    service: Annotated[
        SubSubjectService,
        Depends(get_sub_subject_service),
    ],
) -> SubSubjectResponse:
    dto = CreateSubSubjectDTO(
        subject_id=request.subject_id,
        name=request.name,
        description=request.description,
    )

    return service.create(dto)


@router.get(
    "/",
    response_model=list[SubSubjectResponse],
)
def get_sub_subjects(
    service: Annotated[
        SubSubjectService,
        Depends(get_sub_subject_service),
    ],
) -> list[SubSubjectResponse]:
    return service.get_all()


@router.get(
    "/{sub_subject_id}",
    response_model=SubSubjectResponse,
)
def get_sub_subject(
    sub_subject_id: int,
    service: Annotated[
        SubSubjectService,
        Depends(get_sub_subject_service),
    ],
) -> SubSubjectResponse:
    return service.get_by_id(sub_subject_id)


@router.put(
    "/{sub_subject_id}",
    response_model=SubSubjectResponse,
)
def update_sub_subject(
    sub_subject_id: int,
    request: SubSubjectUpdateRequest,
    service: Annotated[
        SubSubjectService,
        Depends(get_sub_subject_service),
    ],
) -> SubSubjectResponse:
    dto = UpdateSubSubjectDTO(
        name=request.name,
        description=request.description,
    )

    return service.update(sub_subject_id, dto)


@router.delete(
    "/{sub_subject_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_sub_subject(
    sub_subject_id: int,
    service: Annotated[
        SubSubjectService,
        Depends(get_sub_subject_service),
    ],
) -> None:
    service.delete(sub_subject_id)
