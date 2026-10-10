from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, inspect

BACKEND_DIR = Path(__file__).resolve().parent.parent


def test_migrations_create_tables_and_can_be_undone(tmp_path):
    database_url = f"sqlite:///{tmp_path / 'migrations.db'}"
    config = Config(BACKEND_DIR / "alembic.ini")
    config.set_main_option("script_location", str(BACKEND_DIR / "alembic"))
    config.set_main_option("sqlalchemy.url", database_url)

    command.upgrade(config, "head")
    engine = create_engine(database_url)
    assert {"organizations", "blood_drives"} <= set(inspect(engine).get_table_names())

    command.downgrade(config, "base")
    assert "blood_drives" not in inspect(engine).get_table_names()
    engine.dispose()
