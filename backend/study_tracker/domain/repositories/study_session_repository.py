from abc import ABC, abstractmethod

from study_tracker.domain.entities.study_session import StudySession


class StudySessionRepository(ABC):

    @abstractmethod
    def create(self, study_session: StudySession) -> StudySession:
        pass

    @abstractmethod
    def get_by_id(self, study_session_id: int) -> StudySession | None:
        pass

    @abstractmethod
    def get_all(self) -> list[StudySession]:
        pass

    @abstractmethod
    def update(self, study_session: StudySession) -> StudySession:
        pass

    @abstractmethod
    def delete(self, study_session_id: int) -> None:
        pass
