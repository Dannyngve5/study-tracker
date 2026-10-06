from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from study_tracker.application.exceptions import SubjectNotFoundError
from study_tracker.domain.exceptions import (
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
