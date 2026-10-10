import os
from datetime import UTC, datetime

from sqlalchemy import DateTime, Engine, create_engine, event
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from sqlalchemy.types import TypeDecorator

# SQLite for local development; PostgreSQL will be used in production.
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./blooddrive.db")


class Base(DeclarativeBase):
    """Parent class for all database models."""


class UTCDateTime(TypeDecorator):
    """Stores datetimes in UTC and always returns them as timezone-aware UTC.

    Naive datetimes (no timezone) are rejected because it is impossible to
    know which local time they meant.
    """

    impl = DateTime
    cache_ok = True

    def process_bind_param(self, value: datetime | None, dialect) -> datetime | None:
        if value is None:
            return None
        if value.tzinfo is None:
            raise ValueError("Datetime must include a timezone.")
        return value.astimezone(UTC).replace(tzinfo=None)

    def process_result_value(self, value: datetime | None, dialect) -> datetime | None:
        if value is None:
            return None
        return value.replace(tzinfo=UTC)


def utc_now() -> datetime:
    return datetime.now(UTC)


def create_db_engine(url: str) -> Engine:
    engine = create_engine(url)

    if engine.dialect.name == "sqlite":
        # SQLite ignores foreign keys unless this is turned on for every connection.
        @event.listens_for(engine, "connect")
        def enable_foreign_keys(dbapi_connection, connection_record):
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()

    return engine


engine = create_db_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
