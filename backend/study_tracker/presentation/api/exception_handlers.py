from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from study_tracker.application.exceptions import (
    SubjectNotFoundError,
    StudySessionAlreadyActiveError,
    StudySessionNotFoundError,
    SubSubjectDoesNotBelongToSubjectError,
    SubSubjectNotFoundError,
)
from study_tracker.domain.exceptions import (
    InvalidStudySessionStateError,
    SubjectAlreadyExistsError,
    SubjectHasDependentsError,
)


def subject_not_found_exception_handler(
    _request: Request,
    exc: SubjectNotFoundError,
):
    return JSONResponse(
        status_code=404,
        content={"detail": str(exc)},
    )


def subject_already_exists_exception_handler(
    _request: Request,
    exc: SubjectAlreadyExistsError,
):
    return JSONResponse(
        status_code=409,
        content={"detail": str(exc)},
    )


def subject_has_dependents_exception_handler(
    _request: Request,
    exc: SubjectHasDependentsError,
):
    return JSONResponse(
        status_code=409,
        content={"detail": str(exc)},
    )


def study_session_not_found_exception_handler(
    _request: Request,
    exc: StudySessionNotFoundError,
):
    return JSONResponse(
        status_code=404,
        content={"detail": str(exc)},
    )


def study_session_already_active_exception_handler(
    _request: Request,
    exc: StudySessionAlreadyActiveError,
):
    return JSONResponse(
        status_code=409,
        content={"detail": str(exc)},
    )


def sub_subject_not_found_exception_handler(
    _request: Request,
    exc: SubSubjectNotFoundError,
):
    return JSONResponse(
        status_code=404,
        content={"detail": str(exc)},
    )


def sub_subject_does_not_belong_to_subject_exception_handler(
    _request: Request,
    exc: SubSubjectDoesNotBelongToSubjectError,
):
    return JSONResponse(
        status_code=400,
        content={"detail": str(exc)},
    )


def invalid_study_session_state_exception_handler(
    _request: Request,
    exc: InvalidStudySessionStateError,
):
    return JSONResponse(
        status_code=400,
        content={"detail": str(exc)},
    )


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(
        SubjectNotFoundError,
        subject_not_found_exception_handler,
    )

    app.add_exception_handler(
        SubjectAlreadyExistsError,
        subject_already_exists_exception_handler,
    )

    app.add_exception_handler(
        SubjectHasDependentsError,
        subject_has_dependents_exception_handler,
    )

    app.add_exception_handler(
        StudySessionNotFoundError,
        study_session_not_found_exception_handler,
    )

    app.add_exception_handler(
        StudySessionAlreadyActiveError,
        study_session_already_active_exception_handler,
    )

    app.add_exception_handler(
        SubSubjectNotFoundError,
        sub_subject_not_found_exception_handler,
    )

    app.add_exception_handler(
        SubSubjectDoesNotBelongToSubjectError,
        sub_subject_does_not_belong_to_subject_exception_handler,
    )

    app.add_exception_handler(
        InvalidStudySessionStateError,
        invalid_study_session_state_exception_handler,
    )
