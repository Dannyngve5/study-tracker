from unittest.mock import MagicMock

import pytest
from study_tracker.application.dto.sub_subject import (
    CreateSubSubjectDTO,
    UpdateSubSubjectDTO,
)
from study_tracker.application.exceptions import (
    SubjectNotFoundForSubSubjectError,
    SubSubjectNotFoundError,
)
from study_tracker.application.services.sub_subject_service import (
    SubSubjectService,
)
from study_tracker.domain.entities.sub_subject import SubSubject
from study_tracker.domain.entities.subject import Subject


def make_service():
    unit_of_work = MagicMock()
    unit_of_work.__enter__.return_value = unit_of_work
    unit_of_work.subjects = MagicMock()
    unit_of_work.sub_subjects = MagicMock()
    return SubSubjectService(unit_of_work), unit_of_work


def test_create_sub_subject_validates_parent_and_persists_entity():
    service, unit_of_work = make_service()
    unit_of_work.subjects.get_by_id.return_value = Subject(
        id=4,
        name="Python",
    )
    unit_of_work.sub_subjects.create.side_effect = lambda item: item
    dto = CreateSubSubjectDTO(
        subject_id=4,
        name="Data structures",
        description="Trees and graphs",
    )

    result = service.create(dto)

    unit_of_work.subjects.get_by_id.assert_called_once_with(4)
    created_entity = unit_of_work.sub_subjects.create.call_args.args[0]
    assert isinstance(created_entity, SubSubject)
    assert created_entity.subject_id == 4
    assert created_entity.name == "Data structures"
    assert created_entity.description == "Trees and graphs"
    assert result.name == "Data structures"


def test_create_sub_subject_rejects_missing_parent():
    service, unit_of_work = make_service()
    unit_of_work.subjects.get_by_id.return_value = None

    with pytest.raises(SubjectNotFoundForSubSubjectError):
        service.create(
            CreateSubSubjectDTO(
                subject_id=404,
                name="Data structures",
            )
        )

    unit_of_work.sub_subjects.create.assert_not_called()


def test_get_by_id_raises_when_sub_subject_does_not_exist():
    service, unit_of_work = make_service()
    unit_of_work.sub_subjects.get_by_id.return_value = None

    with pytest.raises(SubSubjectNotFoundError):
        service.get_by_id(404)


def test_get_all_returns_repository_results():
    service, unit_of_work = make_service()
    expected = [SubSubject(id=1, subject_id=4, name="Basics")]
    unit_of_work.sub_subjects.get_all.return_value = expected

    assert service.get_all() == expected


def test_update_preserves_parent_subject_and_updates_fields():
    service, unit_of_work = make_service()
    existing = SubSubject(
        id=12,
        subject_id=4,
        name="Basics",
    )
    unit_of_work.sub_subjects.get_by_id.return_value = existing
    unit_of_work.sub_subjects.update.side_effect = lambda item: item

    result = service.update(
        12,
        UpdateSubSubjectDTO(
            name="Advanced",
            description="Advanced topics",
        ),
    )

    updated_entity = unit_of_work.sub_subjects.update.call_args.args[0]
    assert updated_entity.id == 12
    assert updated_entity.subject_id == 4
    assert updated_entity.name == "Advanced"
    assert updated_entity.description == "Advanced topics"
    assert result.name == "Advanced"


def test_update_raises_when_sub_subject_does_not_exist():
    service, unit_of_work = make_service()
    unit_of_work.sub_subjects.get_by_id.return_value = None

    with pytest.raises(SubSubjectNotFoundError):
        service.update(404, UpdateSubSubjectDTO(name="Advanced"))

    unit_of_work.sub_subjects.update.assert_not_called()


def test_update_raises_if_repository_cannot_find_sub_subject():
    service, unit_of_work = make_service()
    unit_of_work.sub_subjects.get_by_id.return_value = SubSubject(
        id=12,
        subject_id=4,
        name="Basics",
    )
    unit_of_work.sub_subjects.update.return_value = None

    with pytest.raises(SubSubjectNotFoundError):
        service.update(12, UpdateSubSubjectDTO(name="Advanced"))


def test_delete_raises_when_sub_subject_does_not_exist():
    service, unit_of_work = make_service()
    unit_of_work.sub_subjects.delete.return_value = False

    with pytest.raises(SubSubjectNotFoundError):
        service.delete(404)
