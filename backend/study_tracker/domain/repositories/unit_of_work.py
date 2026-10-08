from abc import ABC, abstractmethod

from study_tracker.domain.repositories.analytics_repository import AnalyticsRepository
from study_tracker.domain.repositories.study_session_repository import (
    StudySessionRepository,
)
from study_tracker.domain.repositories.sub_subject_repository import (
    SubSubjectRepository,
)
from study_tracker.domain.repositories.subject_repository import SubjectRepository


class UnitOfWork(ABC):

    subjects: SubjectRepository
    sub_subjects: SubSubjectRepository
    study_sessions: StudySessionRepository
    analytics: AnalyticsRepository

    @abstractmethod
    def __enter__(self) -> "UnitOfWork":
        pass

    @abstractmethod
    def __exit__(self, exc_type, exc_value, traceback) -> None:
        pass

    @abstractmethod
    def commit(self) -> None:
        pass

    @abstractmethod
    def rollback(self) -> None:
        pass
