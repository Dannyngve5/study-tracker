from typing import Annotated

from fastapi import APIRouter, Depends, Path, status

from study_tracker.application.dto.study_session import (
    CreateStudySessionDTO,
    StartSessionDTO,
    UpdateStudySessionDTO,
)
from study_tracker.application.services.study_session_service import (
    StudySessionService,
)
from study_tracker.presentation.api.dependencies import (
    get_study_session_service,
)
from study_tracker.presentation.api.schemas.study_session import (
    StudySessionResponse,
)

router = APIRouter(
    prefix="/study-sessions",
    tags=["Study Sessions"],
)


@router.post(
    "/",
    response_model=StudySessionResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_study_session(
    dto: CreateStudySessionDTO,
    service: Annotated[
        StudySessionService,
        Depends(get_study_session_service),
    ],
) -> StudySessionResponse:
    return service.create_session(dto)


@router.get(
    "/",
    response_model=list[StudySessionResponse],
)
def get_study_sessions(
    service: Annotated[
        StudySessionService,
        Depends(get_study_session_service),
    ],
) -> list[StudySessionResponse]:
    return service.get_sessions()


@router.get(
    "/active",
    response_model=StudySessionResponse | None,
)
def get_active_study_session(
    service: Annotated[
        StudySessionService,
        Depends(get_study_session_service),
    ],
) -> StudySessionResponse | None:
    return service.get_active_session()


@router.post(
    "/start",
    response_model=StudySessionResponse,
    status_code=status.HTTP_201_CREATED,
)
def start_study_session(
    dto: StartSessionDTO,
    service: Annotated[
        StudySessionService,
        Depends(get_study_session_service),
    ],
) -> StudySessionResponse:
    return service.start_session(dto)


@router.get(
    "/{study_session_id}",
    response_model=StudySessionResponse,
)
def get_study_session(
    study_session_id: Annotated[int, Path(gt=0)],
    service: Annotated[
        StudySessionService,
        Depends(get_study_session_service),
    ],
) -> StudySessionResponse:
    return service.get_session(study_session_id)


@router.post(
    "/{study_session_id}/pause",
    response_model=StudySessionResponse,
)
def pause_study_session(
    study_session_id: Annotated[int, Path(gt=0)],
    service: Annotated[
        StudySessionService,
        Depends(get_study_session_service),
    ],
) -> StudySessionResponse:
    return service.pause_session(study_session_id)


@router.post(
    "/{study_session_id}/resume",
    response_model=StudySessionResponse,
)
def resume_study_session(
    study_session_id: Annotated[int, Path(gt=0)],
    service: Annotated[
        StudySessionService,
        Depends(get_study_session_service),
    ],
) -> StudySessionResponse:
    return service.resume_session(study_session_id)


@router.post(
    "/{study_session_id}/stop",
    response_model=StudySessionResponse,
)
def stop_study_session(
    study_session_id: Annotated[int, Path(gt=0)],
    service: Annotated[
        StudySessionService,
        Depends(get_study_session_service),
    ],
) -> StudySessionResponse:
    return service.stop_session(study_session_id)


@router.put(
    "/{study_session_id}",
    response_model=StudySessionResponse,
)
def update_study_session(
    study_session_id: Annotated[int, Path(gt=0)],
    dto: UpdateStudySessionDTO,
    service: Annotated[
        StudySessionService,
        Depends(get_study_session_service),
    ],
) -> StudySessionResponse:
    return service.update_session(study_session_id, dto)


@router.delete(
    "/{study_session_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_study_session(
    study_session_id: Annotated[int, Path(gt=0)],
    service: Annotated[
        StudySessionService,
        Depends(get_study_session_service),
    ],
) -> None:
    service.delete(study_session_id)
