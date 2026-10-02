from abc import ABC, abstractmethod

from study_tracker.domain.entities.sub_subject import SubSubject


class SubSubjectRepository(ABC):

    @abstractmethod
    def create(self, sub_subject: SubSubject) -> SubSubject:
        pass

    @abstractmethod
    def get_by_id(self, sub_subject_id: int) -> SubSubject | None:
        pass

    @abstractmethod
    def get_all(self) -> list[SubSubject]:
        pass

    @abstractmethod
    def update(self, sub_subject: SubSubject) -> SubSubject:
        pass

    @abstractmethod
    def delete(self, sub_subject_id: int) -> None:
        pass
