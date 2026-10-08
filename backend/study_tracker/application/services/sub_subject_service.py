from study_tracker.application.dto.sub_subject import (
    CreateSubSubjectDTO,
    UpdateSubSubjectDTO,
)
from study_tracker.application.exceptions import (
    SubSubjectNotFoundError,
    SubjectNotFoundForSubSubjectError,
)
from study_tracker.domain.entities.sub_subject import SubSubject
from study_tracker.domain.repositories.unit_of_work import UnitOfWork


class SubSubjectService:

    def __init__(self, unit_of_work: UnitOfWork):
        self.unit_of_work = unit_of_work

    def create(self, dto: CreateSubSubjectDTO) -> SubSubject:
        with self.unit_of_work as uow:
            subject = uow.subjects.get_by_id(dto.subject_id)

            if subject is None:
                raise SubjectNotFoundForSubSubjectError(dto.subject_id)

            sub_subject = SubSubject(
                subject_id=dto.subject_id,
                name=dto.name,
                description=dto.description,
            )

            return uow.sub_subjects.create(sub_subject)

    def get_by_id(self, sub_subject_id: int) -> SubSubject:
        with self.unit_of_work as uow:
            sub_subject = uow.sub_subjects.get_by_id(sub_subject_id)

            if sub_subject is None:
                raise SubSubjectNotFoundError(sub_subject_id)

            return sub_subject

    def get_all(self) -> list[SubSubject]:
        with self.unit_of_work as uow:
            return uow.sub_subjects.get_all()

    def update(
        self,
        sub_subject_id: int,
        dto: UpdateSubSubjectDTO,
    ) -> SubSubject:
        with self.unit_of_work as uow:
            sub_subject = uow.sub_subjects.get_by_id(sub_subject_id)

            if sub_subject is None:
                raise SubSubjectNotFoundError(sub_subject_id)

            updated_sub_subject = SubSubject(
                id=sub_subject_id,
                subject_id=sub_subject.subject_id,
                name=dto.name,
                description=dto.description,
            )

            result = uow.sub_subjects.update(updated_sub_subject)

            if result is None:
                raise SubSubjectNotFoundError(sub_subject_id)

            return result

    def delete(self, sub_subject_id: int) -> None:
        with self.unit_of_work as uow:
            deleted = uow.sub_subjects.delete(sub_subject_id)

            if not deleted:
                raise SubSubjectNotFoundError(sub_subject_id)
