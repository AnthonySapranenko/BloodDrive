from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, inspect, text

BACKEND_DIR = Path(__file__).resolve().parent.parent


def make_config(database_url: str) -> Config:
    config = Config(BACKEND_DIR / "alembic.ini")
    config.set_main_option("script_location", str(BACKEND_DIR / "alembic"))
    config.set_main_option("sqlalchemy.url", database_url)
    return config


def test_migrations_create_tables_and_can_be_undone(tmp_path):
    database_url = f"sqlite:///{tmp_path / 'migrations.db'}"
    config = make_config(database_url)

    command.upgrade(config, "head")
    engine = create_engine(database_url)
    assert {
        "organizations",
        "blood_drives",
        "users",
        "organization_memberships",
        "user_sessions",
    } <= set(inspect(engine).get_table_names())

    command.downgrade(config, "base")
    assert "blood_drives" not in inspect(engine).get_table_names()
    engine.dispose()


def test_auth_migration_keeps_existing_data_and_approves_existing_orgs(tmp_path):
    # Regression: rebuilding `organizations` on SQLite used to fail once drives pointed at it.
    database_url = f"sqlite:///{tmp_path / 'migrations.db'}"
    config = make_config(database_url)
    command.upgrade(config, "c7f32136f106")
    engine = create_engine(database_url)
    with engine.begin() as connection:
        connection.execute(text(
            "INSERT INTO organizations (id, name, is_demo, created_at, updated_at) "
            "VALUES (1, 'Demo Org', 1, '2026-01-01', '2026-01-01')"
        ))
        connection.execute(text(
            "INSERT INTO blood_drives (organization_id, title, starts_at, ends_at, timezone, "
            "venue_name, street_address, city, state, postal_code, status, is_demo, created_at, updated_at) "
            "VALUES (1, 'Demo Drive', '2026-11-14 15:00', '2026-11-14 20:00', 'America/New_York', "
            "'Hall', '1 Example St', 'Town', 'PA', '16801', 'published', 1, '2026-01-01', '2026-01-01')"
        ))

    command.upgrade(config, "head")

    with engine.connect() as connection:
        assert connection.execute(text("SELECT status FROM organizations")).scalar_one() == "approved"
        assert connection.execute(text("SELECT count(*) FROM blood_drives")).scalar_one() == 1
    engine.dispose()
