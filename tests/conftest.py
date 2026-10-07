import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from study_tracker.infrastructure.database.base import Base
from study_tracker.infrastructure.database.config import settings
from study_tracker.infrastructure.database.unit_of_work import UnitOfWork
from study_tracker.main import app
from study_tracker.presentation.api.dependencies import get_unit_of_work


@pytest.fixture
def db_engine():
    engine = create_engine(settings.test_database_url)

    Base.metadata.create_all(engine)

    yield engine

    Base.metadata.drop_all(engine)
    engine.dispose()


@pytest.fixture
def db_session(db_engine):
    test_session_factory = sessionmaker(
        bind=db_engine,
        class_=Session,
        expire_on_commit=False,
    )

    with test_session_factory() as session:
        yield session
        session.rollback()


@pytest.fixture
def client(db_engine):
    test_session_factory = sessionmaker(
        bind=db_engine,
        class_=Session,
        expire_on_commit=False,
    )

    def get_test_unit_of_work() -> UnitOfWork:
        return UnitOfWork(session_factory=test_session_factory)

    app.dependency_overrides[get_unit_of_work] = get_test_unit_of_work

    with TestClient(app) as client:
        yield client

    app.dependency_overrides.clear()
