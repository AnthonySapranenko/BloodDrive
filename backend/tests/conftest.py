import pytest
from sqlalchemy.orm import Session

from app.database import Base, create_db_engine


@pytest.fixture
def db_session():
    """A fresh, empty in-memory database for each test."""
    engine = create_db_engine("sqlite://")
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        yield session

    engine.dispose()
