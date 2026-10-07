from sqlalchemy import select
from sqlalchemy.orm import Session

from study_tracker.domain.entities.study_session import StudySession
from study_tracker.domain.repositories.study_session_repository import (
    StudySessionRepository,
)
from study_tracker.infrastructure.database.models.study_session import (
    StudySession as StudySessionModel,
    StudySessionStatus,
)


class SQLAlchemyStudySessionRepository(StudySessionRepository):

    def __init__(self, session: Session):
        self.session = session

    def create(self, study_session: StudySession) -> StudySession:
        model = StudySessionModel(
            subject_id=study_session.subject_id,
            sub_subject_id=study_session.sub_subject_id,
            started_at=study_session.started_at,
            ended_at=study_session.ended_at,
            duration_seconds=study_session.duration_seconds,
            status=study_session.status,
            paused_at=study_session.paused_at,
            paused_duration_seconds=study_session.paused_duration_seconds,
        )

        self.session.add(model)
        self.session.flush()

        return self._to_domain(model)

    def get_by_id(self, study_session_id: int) -> StudySession | None:
        model = self.session.get(StudySessionModel, study_session_id)

        if model is None:
            return None

        return self._to_domain(model)

    def get_all(self) -> list[StudySession]:
        statement = select(StudySessionModel)
        models = self.session.scalars(statement).all()

        return [self._to_domain(model) for model in models]

    def update(self, study_session: StudySession) -> StudySession | None:
        model = self.session.get(StudySessionModel, study_session.id)

        if model is None:
            return None

        model.subject_id = study_session.subject_id
        model.sub_subject_id = study_session.sub_subject_id
        model.started_at = study_session.started_at
        model.ended_at = study_session.ended_at
        model.duration_seconds = study_session.duration_seconds
        model.status = study_session.status
        model.paused_at = study_session.paused_at
        model.paused_duration_seconds = study_session.paused_duration_seconds

        self.session.flush()

        return self._to_domain(model)

    def get_active(self) -> StudySession | None:
        statement = select(StudySessionModel).where(
            StudySessionModel.status.in_(
                [
                    StudySessionStatus.RUNNING,
                    StudySessionStatus.PAUSED,
                ]
            )
        )

        model = self.session.scalar(statement)

        if model is None:
            return None

        return self._to_domain(model)

    def delete(self, study_session_id: int) -> bool:
        model = self.session.get(StudySessionModel, study_session_id)

        if model is None:
            return False

        self.session.delete(model)
        self.session.flush()

        return True

    @staticmethod
    def _to_domain(model: StudySessionModel) -> StudySession:
        return StudySession(
            id=model.id,
            subject_id=model.subject_id,
            sub_subject_id=model.sub_subject_id,
            started_at=model.started_at,
            ended_at=model.ended_at,
            duration_seconds=model.duration_seconds,
            created_at=model.created_at,
            status=model.status,
            paused_at=model.paused_at,
            paused_duration_seconds=model.paused_duration_seconds,
        )
