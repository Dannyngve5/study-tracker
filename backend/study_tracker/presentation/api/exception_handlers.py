import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from study_tracker.application.exceptions import (
    InvalidTimezoneError,
    StudySessionAlreadyActiveError,
    StudySessionNotFoundError,
    SubjectNotFoundError,
    SubjectNotFoundForSubSubjectError,
    SubSubjectDoesNotBelongToSubjectError,
    SubSubjectNotFoundError,
)
from study_tracker.domain.exceptions import (
    InvalidStudySessionStateError,
    SubjectAlreadyExistsError,
    SubjectHasDependentsError,
    SubSubjectAlreadyExistsError,
    SubSubjectHasDependentsError,
)

logger = logging.getLogger(__name__)


async def unexpected_exception_handler(
    _request: Request,
    exc: Exception,
) -> JSONResponse:
    logger.exception(
        "Unhandled exception while processing request",
        exc_info=exc,
    )

    return _error_response(
        500,
        "INTERNAL_SERVER_ERROR",
        "An internal server error occurred",
    )


def request_validation_exception_handler(
    _request: Request, _exc: RequestValidationError
) -> JSONResponse:
    return _error_response(
        422,
        "VALIDATION_ERROR",
        "Request validation failed",
    )


def invalid_timezone_exception_handler(
    _request: Request,
    exc: InvalidTimezoneError,
) -> JSONResponse:
    return _error_response(
        400,
        "INVALID_TIMEZONE",
        str(exc),
    )


def _error_response(
    status_code: int,
    code: str,
    message: str,
) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={
            "code": code,
            "message": message,
        },
    )


def subject_not_found_exception_handler(
    _request: Request,
    exc: SubjectNotFoundError,
) -> JSONResponse:
    return _error_response(
        404,
        "SUBJECT_NOT_FOUND",
        str(exc),
    )


def subject_already_exists_exception_handler(
    _request: Request,
    exc: SubjectAlreadyExistsError,
) -> JSONResponse:
    return _error_response(
        409,
        "SUBJECT_ALREADY_EXISTS",
        str(exc),
    )


def subject_has_dependents_exception_handler(
    _request: Request,
    exc: SubjectHasDependentsError,
) -> JSONResponse:
    return _error_response(
        409,
        "SUBJECT_HAS_DEPENDENTS",
        str(exc),
    )


def study_session_not_found_exception_handler(
    _request: Request,
    exc: StudySessionNotFoundError,
) -> JSONResponse:
    return _error_response(
        404,
        "STUDY_SESSION_NOT_FOUND",
        str(exc),
    )


def study_session_already_active_exception_handler(
    _request: Request,
    exc: StudySessionAlreadyActiveError,
) -> JSONResponse:
    return _error_response(
        409,
        "STUDY_SESSION_ALREADY_ACTIVE",
        str(exc),
    )


def sub_subject_not_found_exception_handler(
    _request: Request,
    exc: SubSubjectNotFoundError,
) -> JSONResponse:
    return _error_response(
        404,
        "SUB_SUBJECT_NOT_FOUND",
        str(exc),
    )


def subject_not_found_for_sub_subject_exception_handler(
    _request: Request,
    exc: SubjectNotFoundForSubSubjectError,
) -> JSONResponse:
    return _error_response(
        404,
        "SUBJECT_NOT_FOUND",
        str(exc),
    )


def sub_subject_already_exists_exception_handler(
    _request: Request,
    exc: SubSubjectAlreadyExistsError,
) -> JSONResponse:
    return _error_response(
        409,
        "SUB_SUBJECT_ALREADY_EXISTS",
        str(exc),
    )


def sub_subject_has_dependents_exception_handler(
    _request: Request,
    exc: SubSubjectHasDependentsError,
) -> JSONResponse:
    return _error_response(
        409,
        "SUB_SUBJECT_HAS_DEPENDENTS",
        str(exc),
    )


def sub_subject_does_not_belong_to_subject_exception_handler(
    _request: Request,
    exc: SubSubjectDoesNotBelongToSubjectError,
) -> JSONResponse:
    return _error_response(
        400,
        "SUB_SUBJECT_DOES_NOT_BELONG_TO_SUBJECT",
        str(exc),
    )


def invalid_study_session_state_exception_handler(
    _request: Request,
    exc: InvalidStudySessionStateError,
) -> JSONResponse:
    return _error_response(
        400,
        "INVALID_STUDY_SESSION_STATE",
        str(exc),
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
        SubjectNotFoundForSubSubjectError,
        subject_not_found_for_sub_subject_exception_handler,
    )
    app.add_exception_handler(
        SubSubjectAlreadyExistsError,
        sub_subject_already_exists_exception_handler,
    )
    app.add_exception_handler(
        SubSubjectHasDependentsError,
        sub_subject_has_dependents_exception_handler,
    )
    app.add_exception_handler(
        SubSubjectDoesNotBelongToSubjectError,
        sub_subject_does_not_belong_to_subject_exception_handler,
    )
    app.add_exception_handler(
        InvalidStudySessionStateError,
        invalid_study_session_state_exception_handler,
    )
    app.add_exception_handler(
        RequestValidationError,
        request_validation_exception_handler,
    )
    app.add_exception_handler(
        Exception,
        unexpected_exception_handler,
    )
    app.add_exception_handler(
        InvalidTimezoneError,
        invalid_timezone_exception_handler,
    )
