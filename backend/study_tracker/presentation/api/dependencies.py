from study_tracker.application.services.subject_service import SubjectService
from study_tracker.infrastructure.database.unit_of_work import UnitOfWork


def get_subject_service() -> SubjectService:
    return SubjectService(UnitOfWork())
