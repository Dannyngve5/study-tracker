from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from study_tracker.domain.entities.subject import Subject
from study_tracker.domain.exceptions import (
    SubjectAlreadyExistsError,
    SubjectHasDependentsError,
)
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
        try:
            self.session.flush()
        except IntegrityError as error:
            if self._is_subject_name_conflict(error):
                raise SubjectAlreadyExistsError(subject.name) from error
            raise

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

    def update(self, subject: Subject) -> Subject | None:
        model = self.session.get(SubjectModel, subject.id)

        if model is None:
            return None

        model.name = subject.name
        model.description = subject.description

        try:
            self.session.flush()
        except IntegrityError as error:
            if self._is_subject_name_conflict(error):
                raise SubjectAlreadyExistsError(subject.name) from error
            raise

        return Subject(
            id=model.id,
            name=model.name,
            description=model.description,
            created_at=model.created_at,
        )

    def delete(self, subject_id: int) -> bool:
        model = self.session.get(SubjectModel, subject_id)

        if model is None:
            return False

        self.session.delete(model)
        try:
            self.session.flush()
        except IntegrityError as error:
            if self._is_foreign_key_conflict(error):
                raise SubjectHasDependentsError(subject_id) from error
            raise

        return True

    @staticmethod
    def _is_subject_name_conflict(error: IntegrityError) -> bool:
        original_error = error.orig
        diagnostic = getattr(original_error, "diag", None)
        return (
            getattr(original_error, "sqlstate", None) == "23505"
            and getattr(diagnostic, "constraint_name", None) == "uq_subjects_name"
        )

    @staticmethod
    def _is_foreign_key_conflict(error: IntegrityError) -> bool:
        original_error = error.orig
        diagnostic = getattr(original_error, "diag", None)
        return (
            getattr(original_error, "sqlstate", None) == "23503"
            and getattr(diagnostic, "constraint_name", None)
            in {
                "fk_subsubjects_subject_id_subjects",
                "fk_study_sessions_subject_id_subjects",
            }
        )
