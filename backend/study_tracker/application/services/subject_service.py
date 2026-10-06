from study_tracker.application.dto.subject import (
    CreateSubjectDTO,
    UpdateSubjectDTO,
)
from study_tracker.application.exceptions import SubjectNotFoundError
from study_tracker.domain.entities.subject import Subject
from study_tracker.domain.repositories.unit_of_work import UnitOfWork


class SubjectService:

    def __init__(self, unit_of_work: UnitOfWork):
        self.unit_of_work = unit_of_work

    def create(self, dto: CreateSubjectDTO) -> Subject:
        subject = Subject(
            name=dto.name,
            description=dto.description,
        )

        with self.unit_of_work as uow:
            return uow.subjects.create(subject)

    def get_by_id(self, subject_id: int) -> Subject:
        with self.unit_of_work as uow:
            subject = uow.subjects.get_by_id(subject_id)

            if subject is None:
                raise SubjectNotFoundError(subject_id)

            return subject

    def get_all(self) -> list[Subject]:
        with self.unit_of_work as uow:
            return uow.subjects.get_all()

    def update(
        self,
        subject_id: int,
        dto: UpdateSubjectDTO,
    ) -> Subject:
        subject = Subject(
            id=subject_id,
            name=dto.name,
            description=dto.description,
        )

        with self.unit_of_work as uow:
            updated_subject = uow.subjects.update(subject)

            if updated_subject is None:
                raise SubjectNotFoundError(subject_id)

            return updated_subject

    def delete(self, subject_id: int) -> None:
        with self.unit_of_work as uow:
            deleted = uow.subjects.delete(subject_id)

            if not deleted:
                raise SubjectNotFoundError(subject_id)
