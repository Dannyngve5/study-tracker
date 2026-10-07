from typing import Self

from study_tracker.domain.repositories.unit_of_work import (
    UnitOfWork as UnitOfWorkContract,
)
from study_tracker.infrastructure.database.connection import SessionLocal
from study_tracker.infrastructure.repositories.SQLAlchemy_study_session_repository import (
    SQLAlchemyStudySessionRepository,
)
from study_tracker.infrastructure.repositories.SQLAlchemy_sub_subject_repository import (
    SQLAlchemySubSubjectRepository,
)
from study_tracker.infrastructure.repositories.SQLAlchemy_subject_repository import (
    SQLAlchemySubjectRepository,
)

from sqlalchemy.orm import Session
from collections.abc import Callable


class UnitOfWork(UnitOfWorkContract):

    def __init__(self, session_factory: Callable[[], Session] = SessionLocal):
        self._session_factory = session_factory
        self.session: Session | None = None

    def __enter__(self) -> Self:
        self.session = self._session_factory()

        self.subjects = SQLAlchemySubjectRepository(self.session)
        self.sub_subjects = SQLAlchemySubSubjectRepository(self.session)
        self.study_sessions = SQLAlchemyStudySessionRepository(self.session)

        return self

    def __exit__(self, exc_type, _exc_value, _traceback) -> None:
        try:
            if exc_type is not None:
                self.rollback()
            else:
                try:
                    self.commit()
                except Exception:
                    self.rollback()
                    raise
        finally:
            self.session.close()

    def commit(self) -> None:
        self.session.commit()

    def rollback(self) -> None:
        self.session.rollback()
