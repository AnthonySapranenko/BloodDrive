from datetime import datetime
from enum import StrEnum

from sqlalchemy import CheckConstraint, Enum, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base, UTCDateTime, utc_now


class DriveStatus(StrEnum):
    DRAFT = "draft"  # Only visible to the organizer.
    PUBLISHED = "published"  # Visible in the public directory.
    CANCELLED = "cancelled"  # Still public, clearly labeled, so donors know it is off.


class Organization(Base):
    __tablename__ = "organizations"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200))
    description: Mapped[str | None] = mapped_column(Text)
    # Public contact address shown on listings, not a login email.
    contact_email: Mapped[str | None] = mapped_column(String(320))
    website_url: Mapped[str | None] = mapped_column(String(2048))
    is_demo: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[datetime] = mapped_column(UTCDateTime, default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(
        UTCDateTime, default=utc_now, onupdate=utc_now
    )

    drives: Mapped[list["BloodDrive"]] = relationship(back_populates="organization")


class BloodDrive(Base):
    __tablename__ = "blood_drives"
    __table_args__ = (
        CheckConstraint("ends_at > starts_at", name="ends_after_starts"),
        CheckConstraint("capacity IS NULL OR capacity > 0", name="capacity_positive"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    organization_id: Mapped[int] = mapped_column(
        ForeignKey("organizations.id"), index=True
    )
    title: Mapped[str] = mapped_column(String(200))
    description: Mapped[str | None] = mapped_column(Text)

    # Stored in UTC; `timezone` (e.g. "America/New_York") is used to display local time.
    starts_at: Mapped[datetime] = mapped_column(UTCDateTime, index=True)
    ends_at: Mapped[datetime] = mapped_column(UTCDateTime)
    timezone: Mapped[str] = mapped_column(String(64))

    venue_name: Mapped[str] = mapped_column(String(200))
    street_address: Mapped[str] = mapped_column(String(200))
    city: Mapped[str] = mapped_column(String(100), index=True)
    state: Mapped[str] = mapped_column(String(2), index=True)
    # Text, not a number: ZIP codes can start with 0 (e.g. "02139").
    postal_code: Mapped[str] = mapped_column(String(10), index=True)

    # Official external sign-up page; BloodDrive does not book appointments itself.
    registration_url: Mapped[str | None] = mapped_column(String(2048))
    # Approximate number of donors the drive can take. Informational only.
    capacity: Mapped[int | None]

    status: Mapped[DriveStatus] = mapped_column(
        Enum(
            DriveStatus,
            native_enum=False,
            create_constraint=True,
            length=20,
            values_callable=lambda enum: [member.value for member in enum],
        ),
        default=DriveStatus.DRAFT,
    )
    is_demo: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[datetime] = mapped_column(UTCDateTime, default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(
        UTCDateTime, default=utc_now, onupdate=utc_now
    )

    organization: Mapped[Organization] = relationship(back_populates="drives")
