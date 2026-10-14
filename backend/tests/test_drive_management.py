import pytest
from sqlalchemy import update

from app.database import utc_now
from app.models import Organization, OrganizationStatus

NEXT_YEAR = utc_now().year + 1

DRIVE = {
    "title": "Fall Campus Blood Drive",
    "description": "Bring a photo ID.",
    "starts_at": f"{NEXT_YEAR}-01-15T10:00",
    "ends_at": f"{NEXT_YEAR}-01-15T16:00",
    "timezone": "America/New_York",
    "venue_name": "Student Union",
    "street_address": "100 Example Ave",
    "city": "State College",
    "state": "pa",
    "postal_code": "16801",
    "registration_url": "https://example.com/register",
    "capacity": 60,
}


def sign_up(client, email: str) -> int:
    """Sign up as a new organizer (replacing any current sign-in) and return their organization's id."""
    client.cookies.clear()
    response = client.post(
        "/api/auth/signup",
        json={"name": "Organizer", "email": email, "password": "long enough", "organization_name": email},
    )
    return response.json()["organizations"][0]["id"]


@pytest.fixture
def org_id(client):
    return sign_up(client, "ada@example.com")


def drives_url(org_id: int, drive_id: int | None = None) -> str:
    return f"/api/organizations/{org_id}/drives" + (f"/{drive_id}" if drive_id else "")


def create(client, org_id: int, **changes) -> dict:
    response = client.post(drives_url(org_id), json=DRIVE | changes)
    assert response.status_code == 201, response.text
    return response.json()


def public_titles(client) -> list[str]:
    return [drive["title"] for drive in client.get("/api/drives").json()]


def approve(db_session, org_id: int) -> None:
    db_session.execute(update(Organization).where(Organization.id == org_id).values(status=OrganizationStatus.APPROVED))
    db_session.commit()


def test_new_drive_starts_as_a_draft(client, org_id):
    drive = create(client, org_id)

    assert drive["status"] == "draft"
    assert drive["state"] == "PA"
    assert client.get(drives_url(org_id)).json() == [drive]
    assert client.get(drives_url(org_id, drive["id"])).json() == drive


@pytest.mark.parametrize(
    "month, utc_hour",
    [("01", "15"), ("07", "14")],  # New York is UTC-5 in winter and UTC-4 in summer.
    ids=["standard time", "daylight saving time"],
)
def test_local_times_are_stored_as_utc(client, org_id, month, utc_hour):
    drive = create(
        client, org_id, starts_at=f"{NEXT_YEAR}-{month}-15T10:00", ends_at=f"{NEXT_YEAR}-{month}-15T16:00"
    )

    assert drive["starts_at"] == f"{NEXT_YEAR}-{month}-15T{utc_hour}:00:00Z"


def test_publishing_lists_the_drive_once_the_organization_is_approved(client, db_session, org_id):
    drive = create(client, org_id)
    publish = client.put(drives_url(org_id, drive["id"]), json=DRIVE | {"status": "published"})

    assert publish.status_code == 200
    assert DRIVE["title"] not in public_titles(client)  # The organization is still pending.

    approve(db_session, org_id)
    assert DRIVE["title"] in public_titles(client)

    client.put(drives_url(org_id, drive["id"]), json=DRIVE | {"status": "draft"})  # Unpublish.
    assert DRIVE["title"] not in public_titles(client)


def test_update_replaces_every_field(client, org_id):
    drive = create(client, org_id)

    updated = client.put(drives_url(org_id, drive["id"]), json=DRIVE | {"capacity": None, "venue_name": "Gym"}).json()

    assert updated["capacity"] is None
    assert updated["venue_name"] == "Gym"


def test_only_drafts_can_be_deleted(client, org_id):
    draft = create(client, org_id)
    published = create(client, org_id, status="published")

    assert client.delete(drives_url(org_id, draft["id"])).status_code == 204
    assert client.delete(drives_url(org_id, published["id"])).status_code == 409
    assert [d["id"] for d in client.get(drives_url(org_id)).json()] == [published["id"]]


def test_signed_out_requests_are_rejected(client, org_id):
    client.cookies.clear()

    assert client.get(drives_url(org_id)).status_code == 401
    assert client.post(drives_url(org_id), json=DRIVE).status_code == 401


def test_non_members_cannot_touch_another_organizations_drives(client, org_id):
    drive = create(client, org_id)
    sign_up(client, "mallory@example.com")
    url = drives_url(org_id, drive["id"])

    assert client.get(drives_url(org_id)).status_code == 403
    assert client.post(drives_url(org_id), json=DRIVE).status_code == 403
    assert client.get(url).status_code == 403
    assert client.put(url, json=DRIVE).status_code == 403
    assert client.delete(url).status_code == 403


def test_another_organizations_drive_is_not_found_through_your_own_organization(client, org_id):
    drive = create(client, org_id)
    mallory_org = sign_up(client, "mallory@example.com")
    url = drives_url(mallory_org, drive["id"])  # Mallory's org id, Ada's drive id.

    assert client.get(url).status_code == 404
    assert client.put(url, json=DRIVE | {"title": "Hijacked"}).status_code == 404
    assert client.delete(url).status_code == 404


@pytest.mark.parametrize(
    "changes",
    [
        {"ends_at": f"{NEXT_YEAR}-01-15T09:00"},  # Ends before it starts.
        {"starts_at": "2020-01-15T10:00", "ends_at": "2020-01-15T16:00"},  # Already over.
        {"starts_at": f"{NEXT_YEAR}-01-15T10:00-05:00"},  # Has a UTC offset.
        {"timezone": "Mars/Olympus_Mons"},
        {"timezone": "../../etc/passwd"},
        {"state": "Pennsylvania"},
        {"postal_code": "1680"},
        {"registration_url": "javascript:alert(1)"},
        {"capacity": 0},
        {"title": "   "},
        {"status": "deleted"},
    ],
)
def test_invalid_drives_are_rejected(client, org_id, changes):
    assert client.post(drives_url(org_id), json=DRIVE | changes).status_code == 422
