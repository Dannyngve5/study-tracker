from sqlalchemy import select
from sqlalchemy.orm import Session

from study_tracker.domain.entities.study_session import StudySession
from study_tracker.domain.repositories.study_session_repository import (
    StudySessionRepository,
)
from study_tracker.infrastructure.database.models.study_session import (
    StudySession as StudySessionModel,
)


class SQLAlchemyStudySessionRepository(StudySessionRepository):

    def __init__(self, session: Session):
        self.session = session

    def create(self, study_session: StudySession) -> StudySession:
        model = StudySessionModel(
            subject_id=study_session.subject_id,
            subsubject_id=study_session.subsubject_id,
            started_at=study_session.started_at,
            ended_at=study_session.ended_at,
            duration_seconds=study_session.duration_seconds,
        )

        self.session.add(model)
        self.session.flush()

        return StudySession(
            id=model.id,
            subject_id=model.subject_id,
            subsubject_id=model.subsubject_id,
            started_at=model.started_at,
            ended_at=model.ended_at,
            duration_seconds=model.duration_seconds,
            created_at=model.created_at,
        )

    def get_by_id(self, study_session_id: int) -> StudySession | None:
        model = self.session.get(StudySessionModel, study_session_id)

        if model is None:
            return None

        return StudySession(
            id=model.id,
            subject_id=model.subject_id,
            subsubject_id=model.subsubject_id,
            started_at=model.started_at,
            ended_at=model.ended_at,
            duration_seconds=model.duration_seconds,
            created_at=model.created_at,
        )

    def get_all(self) -> list[StudySession]:
        statement = select(StudySessionModel)
        models = self.session.scalars(statement).all()

        return [
            StudySession(
                id=model.id,
                subject_id=model.subject_id,
                subsubject_id=model.subsubject_id,
                started_at=model.started_at,
                ended_at=model.ended_at,
                duration_seconds=model.duration_seconds,
                created_at=model.created_at,
            )
            for model in models
        ]

    def update(self, study_session: StudySession) -> StudySession:
        model = self.session.get(StudySessionModel, study_session.id)

        if model is None:
            raise ValueError("StudySession not found")

        model.subject_id = study_session.subject_id
        model.subsubject_id = study_session.subsubject_id
        model.started_at = study_session.started_at
        model.ended_at = study_session.ended_at
        model.duration_seconds = study_session.duration_seconds

        self.session.flush()

        return StudySession(
            id=model.id,
            subject_id=model.subject_id,
            subsubject_id=model.subsubject_id,
            started_at=model.started_at,
            ended_at=model.ended_at,
            duration_seconds=model.duration_seconds,
            created_at=model.created_at,
        )

    def delete(self, study_session_id: int) -> None:
        model = self.session.get(StudySessionModel, study_session_id)

        if model is None:
            return

        self.session.delete(model)
        self.session.flush()
