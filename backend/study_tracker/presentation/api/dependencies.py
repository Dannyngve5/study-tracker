from study_tracker.application.services.subject_service import SubjectService
from study_tracker.application.services.study_session_service import StudySessionService

from study_tracker.infrastructure.database.unit_of_work import UnitOfWork


def get_subject_service() -> SubjectService:
    return SubjectService(UnitOfWork())


def get_study_session_service() -> StudySessionService:
    return StudySessionService(UnitOfWork())
