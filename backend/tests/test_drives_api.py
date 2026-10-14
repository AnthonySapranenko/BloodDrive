import pytest

from sqlalchemy import update

from app.models import Organization, OrganizationStatus
from app.seed_demo import seed


@pytest.fixture
def seeded_client(client, db_session):
    seed(db_session)
    return client


def titles(response) -> list[str]:
    return [drive["title"] for drive in response.json()]


def test_lists_only_public_upcoming_drives_soonest_first(seeded_client):
    response = seeded_client.get("/api/drives")

    assert response.status_code == 200
    # The draft and the already-ended drive are hidden; the cancelled one stays visible.
    assert titles(response) == [
        "[DEMO] Fall Campus Blood Drive",
        "[DEMO] Community Blood Drive",
        "[DEMO] Winter Blood Drive",
    ]


def test_response_includes_status_demo_flag_and_organization(seeded_client):
    winter = seeded_client.get("/api/drives", params={"city": "Pittsburgh"}).json()[0]

    assert winter["status"] == "cancelled"
    assert winter["is_demo"] is True
    assert winter["organization"]["name"] == "Demo Student Blood Club"
    assert winter["starts_at"].endswith("Z")  # Times are sent as UTC.
    assert "created_at" not in winter


@pytest.mark.parametrize(
    "params, expected_count",
    [
        ({"state": "pa"}, 3),  # Case-insensitive.
        ({"state": "NY"}, 0),
        ({"city": " state college "}, 2),  # Case- and whitespace-insensitive.
        ({"zip": "15213"}, 1),
        ({"city": "State College", "zip": "15213"}, 0),  # Filters combine.
    ],
)
def test_filters(seeded_client, params, expected_count):
    response = seeded_client.get("/api/drives", params=params)

    assert response.status_code == 200
    assert len(response.json()) == expected_count


@pytest.mark.parametrize(
    "params",
    [{"state": "Pennsylvania"}, {"state": "P1"}, {"zip": "1680"}, {"zip": "16801-1234"}, {"zip": "abcde"}],
)
def test_invalid_filters_are_rejected(seeded_client, params):
    assert seeded_client.get("/api/drives", params=params).status_code == 422


def test_seed_can_be_rerun_without_duplicates(seeded_client, db_session):
    seed(db_session)

    assert len(seeded_client.get("/api/drives").json()) == 3


def test_drives_from_unapproved_organizations_are_hidden(seeded_client, db_session):
    db_session.execute(
        update(Organization)
        .where(Organization.name == "Demo Community Church")
        .values(status=OrganizationStatus.PENDING)
    )
    db_session.commit()

    assert "[DEMO] Community Blood Drive" not in titles(seeded_client.get("/api/drives"))
