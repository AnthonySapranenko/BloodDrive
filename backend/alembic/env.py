from logging.config import fileConfig

from alembic import context

from app import models  # noqa: F401  (registers the models on Base.metadata)
from app.database import DATABASE_URL, Base, UTCDateTime, create_db_engine

# The Alembic Config object, which reads values from alembic.ini.
config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Autogenerate compares the database against these table definitions.
target_metadata = Base.metadata

# A URL set on the config (e.g. by tests) wins over the app's default.
database_url = config.get_main_option("sqlalchemy.url") or DATABASE_URL


def render_item(type_, obj, autogen_context):
    """Write UTCDateTime columns as plain DateTime in migration files.

    The UTC conversion happens in Python, so the database column is an
    ordinary DateTime and migrations don't need to import app code.
    """
    if type_ == "type" and isinstance(obj, UTCDateTime):
        return "sa.DateTime()"
    return False


def run_migrations_offline() -> None:
    """Generate SQL without connecting to a database."""
    context.configure(
        url=database_url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        render_as_batch=True,
        render_item=render_item,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Connect to the database and apply migrations."""
    engine = create_db_engine(database_url)

    with engine.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            # SQLite can't alter most columns in place; batch mode rebuilds
            # the table instead. It is harmless on PostgreSQL.
            render_as_batch=True,
            render_item=render_item,
        )

        with context.begin_transaction():
            context.run_migrations()

    engine.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
