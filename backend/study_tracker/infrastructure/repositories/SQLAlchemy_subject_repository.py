from sqlalchemy import select
from sqlalchemy.orm import Session

from study_tracker.domain.entities.subject import Subject
from study_tracker.domain.repositories.subject_repository import SubjectRepository
from study_tracker.infrastructure.database.models.subject import Subject as SubjectModel


class SQLAlchemySubjectRepository(SubjectRepository):

    def __init__(self, session: Session):
        self.session = session

    def create(self, subject: Subject) -> Subject:
        model = SubjectModel(
            name=subject.name,
            description=subject.description,
        )

        self.session.add(model)
        self.session.flush()

        return Subject(
            id=model.id,
            name=model.name,
            description=model.description,
            created_at=model.created_at,
        )

    def get_by_id(self, subject_id: int) -> Subject | None:
        model = self.session.get(SubjectModel, subject_id)

        if model is None:
            return None

        return Subject(
            id=model.id,
            name=model.name,
            description=model.description,
            created_at=model.created_at,
        )

    def get_all(self) -> list[Subject]:
        statement = select(SubjectModel)
        models = self.session.scalars(statement).all()

        return [
            Subject(
                id=model.id,
                name=model.name,
                description=model.description,
                created_at=model.created_at,
            )
            for model in models
        ]

    def update(self, subject: Subject) -> Subject:
        model = self.session.get(SubjectModel, subject.id)

        if model is None:
            raise ValueError("Subject not found")

        model.name = subject.name
        model.description = subject.description

        self.session.flush()

        return Subject(
            id=model.id,
            name=model.name,
            description=model.description,
            created_at=model.created_at,
        )

    def delete(self, subject_id: int) -> None:
        model = self.session.get(SubjectModel, subject_id)

        if model is None:
            return

        self.session.delete(model)
        self.session.flush()
