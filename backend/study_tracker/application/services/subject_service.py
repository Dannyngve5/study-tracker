# editar Subject
# eliminar Subject
# obtener Subject
# listar Subjects


from study_tracker.application.dto.subject import CreateSubjectDTO
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
