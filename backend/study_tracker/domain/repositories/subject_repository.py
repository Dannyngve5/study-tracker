from abc import ABC, abstractmethod

from study_tracker.domain.entities.subject import Subject


class SubjectRepository(ABC):

    @abstractmethod
    def create(self, subject: Subject) -> Subject:
        pass

    @abstractmethod
    def get_by_id(self, subject_id: int) -> Subject | None:
        pass

    @abstractmethod
    def get_all(self) -> list[Subject]:
        pass

    @abstractmethod
    def update(self, subject: Subject) -> Subject:
        pass

    @abstractmethod
    def delete(self, subject_id: int) -> None:
        pass
