"""Load clearly labeled demonstration data. Safe to re-run: old demo rows are replaced.

Run from the backend folder:  python -m app.seed_demo
"""

from datetime import UTC, datetime, timedelta

from sqlalchemy import delete
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import BloodDrive, DriveStatus, Organization, OrganizationStatus


def drive(org, title, days_from_now, hour_utc, hours, **fields) -> BloodDrive:
    day = datetime.now(UTC).replace(hour=hour_utc, minute=0, second=0, microsecond=0)
    starts_at = day + timedelta(days=days_from_now)
    return BloodDrive(
        organization=org,
        title=f"[DEMO] {title}",
        description="Demonstration listing. This is not a real blood drive.",
        starts_at=starts_at,
        ends_at=starts_at + timedelta(hours=hours),
        timezone="America/New_York",
        is_demo=True,
        **fields,
    )


def seed(session: Session) -> None:
    # Children first, so the foreign key from drives to organizations isn't violated.
    session.execute(delete(BloodDrive).where(BloodDrive.is_demo))
    session.execute(delete(Organization).where(Organization.is_demo))

    club = Organization(
        name="Demo Student Blood Club",
        description="Fictional organization used for demonstration data.",
        website_url="https://example.com/demo-club",
        status=OrganizationStatus.APPROVED,
        is_demo=True,
    )
    church = Organization(
        name="Demo Community Church",
        description="Fictional organization used for demonstration data.",
        status=OrganizationStatus.APPROVED,
        is_demo=True,
    )
    pa = dict(city="State College", state="PA", postal_code="16801")

    session.add_all([
        drive(club, "Fall Campus Blood Drive", 3, 14, 6, venue_name="Demo Student Union",
              street_address="100 Example Ave", capacity=60,
              registration_url="https://example.com/demo-register", status=DriveStatus.PUBLISHED, **pa),
        drive(church, "Community Blood Drive", 10, 15, 4, venue_name="Demo Fellowship Hall",
              street_address="200 Sample Rd", status=DriveStatus.PUBLISHED, **pa),
        drive(club, "Winter Blood Drive", 20, 14, 5, venue_name="Demo Recreation Center",
              street_address="300 Placeholder Blvd", city="Pittsburgh", state="PA",
              postal_code="15213", status=DriveStatus.CANCELLED),
        drive(club, "Spring Blood Drive (draft)", 60, 14, 5, venue_name="Demo Student Union",
              street_address="100 Example Ave", status=DriveStatus.DRAFT, **pa),
        drive(church, "Summer Blood Drive (already ended)", -30, 15, 4, venue_name="Demo Fellowship Hall",
              street_address="200 Sample Rd", status=DriveStatus.PUBLISHED, **pa),
    ])
    session.commit()


if __name__ == "__main__":
    with SessionLocal() as session:
        seed(session)
    print("Demo data loaded.")
