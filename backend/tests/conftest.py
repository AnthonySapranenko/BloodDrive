import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.database import Base, create_db_engine, get_db
from app.main import app


@pytest.fixture
def db_session(tmp_path):
    """A fresh, empty database for each test.

    A temporary file rather than in-memory, because the API handles
    requests on a different thread than the test.
    """
    engine = create_db_engine(f"sqlite:///{tmp_path / 'test.db'}")
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        yield session

    engine.dispose()


@pytest.fixture
def client(db_session):
    """An API client whose requests use the test database instead of the real one."""
    app.dependency_overrides[get_db] = lambda: db_session
    yield TestClient(app)
    app.dependency_overrides.clear()
