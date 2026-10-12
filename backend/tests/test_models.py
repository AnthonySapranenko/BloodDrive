from datetime import UTC, datetime, timedelta, timezone

import pytest
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError, StatementError

from app.models import (
    BloodDrive,
    DriveStatus,
    MembershipRole,
    Organization,
    OrganizationMembership,
    OrganizationStatus,
    User,
    UserSession,
)

START = datetime(2026, 11, 14, 15, 0, tzinfo=UTC)


def make_organization() -> Organization:
    return Organization(name="Demo Student Blood Club", is_demo=True)


def make_drive(organization: Organization | None, **overrides) -> BloodDrive:
    fields = dict(
        title="Demo Fall Blood Drive",
        starts_at=START,
        ends_at=START + timedelta(hours=5),
        timezone="America/New_York",
        venue_name="Demo Student Union",
        street_address="123 Example St",
        city="State College",
        state="PA",
        postal_code="16801",
        is_demo=True,
    )
    if organization is not None:
        fields["organization"] = organization
    fields.update(overrides)
    return BloodDrive(**fields)


def test_valid_drive_is_saved_with_defaults(db_session):
    drive = make_drive(make_organization())
    db_session.add(drive)
    db_session.commit()

    assert drive.id is not None
    assert drive.status == DriveStatus.DRAFT
    assert drive.capacity is None
    assert drive.created_at.tzinfo is not None


def test_datetimes_are_returned_as_utc(db_session):
    eastern = timezone(timedelta(hours=-5))
    drive = make_drive(
        make_organization(),
        starts_at=datetime(2026, 11, 14, 10, 0, tzinfo=eastern),
        ends_at=datetime(2026, 11, 14, 15, 0, tzinfo=eastern),
    )
    db_session.add(drive)
    db_session.commit()
    db_session.expire_all()  # Force a fresh read from the database.

    assert drive.starts_at == datetime(2026, 11, 14, 15, 0, tzinfo=UTC)
    assert drive.starts_at.tzinfo == UTC


def test_datetime_without_timezone_is_rejected(db_session):
    db_session.add(make_drive(make_organization(), starts_at=datetime(2026, 11, 14, 10, 0)))

    with pytest.raises(StatementError, match="must include a timezone"):
        db_session.commit()


def test_drive_must_end_after_it_starts(db_session):
    db_session.add(make_drive(make_organization(), ends_at=START - timedelta(hours=1)))

    with pytest.raises(IntegrityError, match="ends_after_starts"):
        db_session.commit()


@pytest.mark.parametrize("capacity", [0, -5])
def test_capacity_must_be_positive(db_session, capacity):
    db_session.add(make_drive(make_organization(), capacity=capacity))

    with pytest.raises(IntegrityError, match="capacity_positive"):
        db_session.commit()


def test_positive_capacity_is_allowed(db_session):
    drive = make_drive(make_organization(), capacity=40)
    db_session.add(drive)
    db_session.commit()

    assert drive.capacity == 40


def test_database_rejects_unknown_status(db_session):
    drive = make_drive(make_organization())
    db_session.add(drive)
    db_session.commit()

    with pytest.raises(IntegrityError, match="drivestatus"):
        db_session.execute(
            text("UPDATE blood_drives SET status = 'bogus' WHERE id = :id"),
            {"id": drive.id},
        )


def test_drive_requires_an_existing_organization(db_session):
    db_session.add(make_drive(None, organization_id=9999))

    with pytest.raises(IntegrityError, match="FOREIGN KEY"):
        db_session.commit()


def test_cancelled_status_can_be_set(db_session):
    drive = make_drive(make_organization(), status=DriveStatus.CANCELLED)
    db_session.add(drive)
    db_session.commit()
    db_session.expire_all()

    assert drive.status == DriveStatus.CANCELLED


def make_user(email: str = "organizer@example.com") -> User:
    return User(email=email, name="Demo Organizer", password_hash="not-a-real-hash")


def test_new_organization_starts_pending(db_session):
    organization = make_organization()
    db_session.add(organization)
    db_session.commit()

    assert organization.status == OrganizationStatus.PENDING


def test_user_email_must_be_unique(db_session):
    db_session.add_all([make_user(), make_user()])

    with pytest.raises(IntegrityError, match="UNIQUE"):
        db_session.commit()


def test_membership_links_user_to_organization_as_owner(db_session):
    user = make_user()
    organization = make_organization()
    db_session.add(OrganizationMembership(user=user, organization=organization))
    db_session.commit()

    assert user.memberships[0].organization is organization
    assert user.memberships[0].role == MembershipRole.OWNER


def test_user_can_join_an_organization_only_once(db_session):
    user = make_user()
    organization = make_organization()
    db_session.add_all([
        OrganizationMembership(user=user, organization=organization),
        OrganizationMembership(user=user, organization=organization),
    ])

    with pytest.raises(IntegrityError, match="UNIQUE"):
        db_session.commit()


def test_session_token_hash_must_be_unique(db_session):
    user = make_user()
    expires_at = START + timedelta(days=14)
    db_session.add_all([
        UserSession(user=user, token_hash="a" * 64, expires_at=expires_at),
        UserSession(user=user, token_hash="a" * 64, expires_at=expires_at),
    ])

    with pytest.raises(IntegrityError, match="UNIQUE"):
        db_session.commit()
