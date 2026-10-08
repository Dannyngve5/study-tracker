from typing import Annotated

from fastapi import Depends
from study_tracker.application.services.analytics_service import AnalyticsService
from study_tracker.application.services.study_session_service import StudySessionService
from study_tracker.application.services.subject_service import SubjectService
from study_tracker.application.services.sub_subject_service import SubSubjectService
from study_tracker.infrastructure.database.unit_of_work import UnitOfWork


def get_unit_of_work() -> UnitOfWork:
    return UnitOfWork()


def get_subject_service(
    unit_of_work: Annotated[UnitOfWork, Depends(get_unit_of_work)],
) -> SubjectService:
    return SubjectService(unit_of_work)


def get_study_session_service(
    unit_of_work: Annotated[UnitOfWork, Depends(get_unit_of_work)],
) -> StudySessionService:
    return StudySessionService(unit_of_work)


def get_analytics_service(
    unit_of_work: Annotated[UnitOfWork, Depends(get_unit_of_work)],
) -> AnalyticsService:
    return AnalyticsService(unit_of_work)


def get_sub_subject_service(
    unit_of_work: Annotated[UnitOfWork, Depends(get_unit_of_work)],
) -> SubSubjectService:
    return SubSubjectService(unit_of_work)
