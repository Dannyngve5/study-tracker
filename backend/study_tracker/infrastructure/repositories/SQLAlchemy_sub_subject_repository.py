from sqlalchemy import select
from sqlalchemy.orm import Session

from study_tracker.domain.entities.sub_subject import SubSubject
from study_tracker.domain.repositories.sub_subject_repository import (
    SubSubjectRepository,
)
from study_tracker.infrastructure.database.models.subsubject import (
    SubSubject as SubSubjectModel,
)


class SQLAlchemySubSubjectRepository(SubSubjectRepository):

    def __init__(self, session: Session):
        self.session = session

    def create(self, sub_subject: SubSubject) -> SubSubject:
        model = SubSubjectModel(
            subject_id=sub_subject.subject_id,
            name=sub_subject.name,
            description=sub_subject.description,
        )

        self.session.add(model)
        self.session.flush()

        return SubSubject(
            id=model.id,
            subject_id=model.subject_id,
            name=model.name,
            description=model.description,
            created_at=model.created_at,
        )

    def get_by_id(self, sub_subject_id: int) -> SubSubject | None:
        model = self.session.get(SubSubjectModel, sub_subject_id)

        if model is None:
            return None

        return SubSubject(
            id=model.id,
            subject_id=model.subject_id,
            name=model.name,
            description=model.description,
            created_at=model.created_at,
        )

    def get_all(self) -> list[SubSubject]:
        statement = select(SubSubjectModel)
        models = self.session.scalars(statement).all()

        return [
            SubSubject(
                id=model.id,
                subject_id=model.subject_id,
                name=model.name,
                description=model.description,
                created_at=model.created_at,
            )
            for model in models
        ]

    def update(self, sub_subject: SubSubject) -> SubSubject:
        model = self.session.get(SubSubjectModel, sub_subject.id)

        if model is None:
            raise ValueError("SubSubject not found")

        model.subject_id = sub_subject.subject_id
        model.name = sub_subject.name
        model.description = sub_subject.description

        self.session.flush()

        return SubSubject(
            id=model.id,
            subject_id=model.subject_id,
            name=model.name,
            description=model.description,
            created_at=model.created_at,
        )

    def delete(self, sub_subject_id: int) -> None:
        model = self.session.get(SubSubjectModel, sub_subject_id)

        if model is None:
            return

        self.session.delete(model)
        self.session.flush()
