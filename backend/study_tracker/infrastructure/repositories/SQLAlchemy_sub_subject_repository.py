from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from study_tracker.domain.entities.sub_subject import SubSubject
from study_tracker.domain.exceptions import (
    SubSubjectAlreadyExistsError,
    SubSubjectHasDependentsError,
)
from study_tracker.domain.repositories.sub_subject_repository import (
    SubSubjectRepository,
)
from study_tracker.infrastructure.database.models.sub_subject import (
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

        try:
            self.session.flush()
        except IntegrityError as error:
            if self._is_name_conflict(error):
                raise SubSubjectAlreadyExistsError(
                    sub_subject.subject_id,
                    sub_subject.name,
                ) from error

            raise

        return self._to_domain(model)

    def get_by_id(self, sub_subject_id: int) -> SubSubject | None:
        model = self.session.get(SubSubjectModel, sub_subject_id)

        if model is None:
            return None

        return self._to_domain(model)

    def get_all(self) -> list[SubSubject]:
        statement = select(SubSubjectModel)
        models = self.session.scalars(statement).all()

        return [self._to_domain(model) for model in models]

    def update(self, sub_subject: SubSubject) -> SubSubject | None:
        model = self.session.get(SubSubjectModel, sub_subject.id)

        if model is None:
            return None

        model.subject_id = sub_subject.subject_id
        model.name = sub_subject.name
        model.description = sub_subject.description

        try:
            self.session.flush()
        except IntegrityError as error:
            if self._is_name_conflict(error):
                raise SubSubjectAlreadyExistsError(
                    sub_subject.subject_id,
                    sub_subject.name,
                ) from error

            raise

        return self._to_domain(model)

    def delete(self, sub_subject_id: int) -> bool:
        model = self.session.get(SubSubjectModel, sub_subject_id)

        if model is None:
            return False

        self.session.delete(model)

        try:
            self.session.flush()
        except IntegrityError as error:
            if self._is_dependents_conflict(error):
                raise SubSubjectHasDependentsError(sub_subject_id) from error

            raise

        return True

    @staticmethod
    def _is_name_conflict(error: IntegrityError) -> bool:
        original_error = error.orig
        diagnostic = getattr(original_error, "diag", None)

        return (
            getattr(original_error, "sqlstate", None) == "23505"
            and getattr(diagnostic, "constraint_name", None)
            == "uq_sub_subjects_subject_id_name"
        )

    @staticmethod
    def _is_dependents_conflict(error: IntegrityError) -> bool:
        original_error = error.orig
        diagnostic = getattr(original_error, "diag", None)

        return (
            getattr(original_error, "sqlstate", None) == "23503"
            and getattr(diagnostic, "constraint_name", None)
            == "fk_study_sessions_sub_subject_id_sub_subjects"
        )

    @staticmethod
    def _to_domain(model: SubSubjectModel) -> SubSubject:
        return SubSubject(
            id=model.id,
            subject_id=model.subject_id,
            name=model.name,
            description=model.description,
            created_at=model.created_at,
        )
