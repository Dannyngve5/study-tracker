from types import SimpleNamespace
from unittest.mock import Mock

import pytest
from sqlalchemy.exc import IntegrityError
from study_tracker.application.exceptions import SubjectNotFoundError
from study_tracker.application.services.subject_service import SubjectService
from study_tracker.domain.entities.sub_subject import SubSubject
from study_tracker.domain.entities.subject import Subject
from study_tracker.domain.exceptions import (
    SubjectAlreadyExistsError,
    SubjectHasDependentsError,
)
from study_tracker.infrastructure.database.unit_of_work import UnitOfWork
from study_tracker.infrastructure.repositories.SQLAlchemy_sub_subject_repository import (
    SQLAlchemySubSubjectRepository,
)
from study_tracker.infrastructure.repositories.SQLAlchemy_subject_repository import (
    SQLAlchemySubjectRepository,
)


class PostgresError(Exception):
    def __init__(self, sqlstate: str, constraint_name: str | None = None):
        super().__init__()
        self.sqlstate = sqlstate
        self.diag = SimpleNamespace(constraint_name=constraint_name)


def integrity_error(sqlstate: str, constraint_name: str | None = None):
    return IntegrityError(
        statement="statement",
        params=None,
        orig=PostgresError(sqlstate, constraint_name),
    )


def test_create_translates_subject_name_unique_violation():
    session = Mock()
    session.flush.side_effect = integrity_error("23505", "uq_subjects_name")
    repository = SQLAlchemySubjectRepository(session)

    with pytest.raises(SubjectAlreadyExistsError):
        repository.create(Subject(name="Mathematics"))


def test_create_does_not_misreport_other_integrity_errors():
    session = Mock()
    error = integrity_error("23505", "some_other_constraint")
    session.flush.side_effect = error
    repository = SQLAlchemySubjectRepository(session)

    with pytest.raises(IntegrityError) as raised:
        repository.create(Subject(name="Mathematics"))

    assert raised.value is error


def test_update_translates_subject_name_unique_violation():
    session = Mock()
    session.get.return_value = SimpleNamespace(
        id=1,
        name="Old name",
        description=None,
        created_at=None,
    )
    session.flush.side_effect = integrity_error("23505", "uq_subjects_name")
    repository = SQLAlchemySubjectRepository(session)

    with pytest.raises(SubjectAlreadyExistsError):
        repository.update(Subject(id=1, name="Mathematics"))


@pytest.mark.parametrize(
    "constraint_name",
    [
        "fk_subsubjects_subject_id_subjects",
        "fk_study_sessions_subject_id_subjects",
    ],
)
def test_delete_translates_subject_dependent_foreign_key_to_conflict(
    constraint_name,
):
    session = Mock()
    session.get.return_value = SimpleNamespace(id=1)
    session.flush.side_effect = integrity_error("23503", constraint_name)
    repository = SQLAlchemySubjectRepository(session)

    with pytest.raises(SubjectHasDependentsError):
        repository.delete(1)


def test_delete_does_not_translate_unrecognized_foreign_key_violation():
    session = Mock()
    session.get.return_value = SimpleNamespace(id=1)
    error = integrity_error("23503", "some_other_constraint")
    session.flush.side_effect = error
    repository = SQLAlchemySubjectRepository(session)

    with pytest.raises(IntegrityError) as raised:
        repository.delete(1)

    assert raised.value is error


def test_sub_subject_repository_returns_none_for_missing_update():
    session = Mock()
    session.get.return_value = None
    repository = SQLAlchemySubSubjectRepository(session)

    assert repository.update(SubSubject(id=1, subject_id=1, name="Algebra")) is None


def test_sub_subject_repository_delete_reports_whether_a_row_was_deleted():
    session = Mock()
    session.get.return_value = None
    repository = SQLAlchemySubSubjectRepository(session)

    assert repository.delete(1) is False

    session.get.return_value = SimpleNamespace(id=1)

    assert repository.delete(1) is True


def test_subject_service_turns_missing_repository_result_into_not_found():
    unit_of_work = Mock()
    unit_of_work.__enter__ = Mock(return_value=unit_of_work)
    unit_of_work.__exit__ = Mock(return_value=False)
    unit_of_work.subjects.get_by_id.return_value = None
    service = SubjectService(unit_of_work)

    with pytest.raises(SubjectNotFoundError):
        service.get_by_id(404)


def test_unit_of_work_rolls_back_and_closes_when_commit_fails():
    unit_of_work = UnitOfWork()
    unit_of_work.session = Mock()
    unit_of_work.session.commit.side_effect = RuntimeError("commit failed")

    with pytest.raises(RuntimeError, match="commit failed"):
        unit_of_work.__exit__(None, None, None)

    unit_of_work.session.rollback.assert_called_once()
    unit_of_work.session.close.assert_called_once()
