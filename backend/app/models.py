from datetime import datetime
from enum import StrEnum

from sqlalchemy import CheckConstraint, Enum, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base, UTCDateTime, utc_now


class DriveStatus(StrEnum):
    DRAFT = "draft"  # Only visible to the organizer.
    PUBLISHED = "published"  # Visible in the public directory.
    CANCELLED = "cancelled"  # Still public, clearly labeled, so donors know it is off.


class OrganizationStatus(StrEnum):
    PENDING = "pending"  # New sign-up; its drives stay out of the public directory.
    APPROVED = "approved"  # Reviewed by an admin; published drives are public.


class MembershipRole(StrEnum):
    OWNER = "owner"


def string_enum(enum_class: type[StrEnum]) -> Enum:
    """Store an enum as its text value, with a CHECK constraint (works on SQLite and PostgreSQL)."""
    return Enum(
        enum_class,
        native_enum=False,
        create_constraint=True,
        length=20,
        values_callable=lambda enum: [member.value for member in enum],
    )


class Organization(Base):
    __tablename__ = "organizations"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200))
    description: Mapped[str | None] = mapped_column(Text)
    # Public contact address shown on listings, not a login email.
    contact_email: Mapped[str | None] = mapped_column(String(320))
    website_url: Mapped[str | None] = mapped_column(String(2048))
    status: Mapped[OrganizationStatus] = mapped_column(
        string_enum(OrganizationStatus), default=OrganizationStatus.PENDING
    )
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
        string_enum(DriveStatus), default=DriveStatus.DRAFT
    )
    is_demo: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[datetime] = mapped_column(UTCDateTime, default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(
        UTCDateTime, default=utc_now, onupdate=utc_now
    )

    organization: Mapped[Organization] = relationship(back_populates="drives")


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    # Login email, always stored lowercase. Never shown publicly.
    email: Mapped[str] = mapped_column(String(320), unique=True)
    name: Mapped[str] = mapped_column(String(200))
    # Argon2 hash; the plain password is never stored.
    password_hash: Mapped[str] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(UTCDateTime, default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(
        UTCDateTime, default=utc_now, onupdate=utc_now
    )

    memberships: Mapped[list["OrganizationMembership"]] = relationship(
        back_populates="user"
    )


class OrganizationMembership(Base):
    """Which users may manage which organization's drives."""

    __tablename__ = "organization_memberships"
    __table_args__ = (
        UniqueConstraint("user_id", "organization_id", name="one_membership_per_org"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    organization_id: Mapped[int] = mapped_column(
        ForeignKey("organizations.id"), index=True
    )
    role: Mapped[MembershipRole] = mapped_column(
        string_enum(MembershipRole), default=MembershipRole.OWNER
    )
    created_at: Mapped[datetime] = mapped_column(UTCDateTime, default=utc_now)

    user: Mapped[User] = relationship(back_populates="memberships")
    organization: Mapped[Organization] = relationship()


class UserSession(Base):
    """A signed-in browser. Deleting the row signs that browser out immediately."""

    __tablename__ = "user_sessions"

    id: Mapped[int] = mapped_column(primary_key=True)
    # SHA-256 of the cookie token, so a database leak doesn't hand out working logins.
    token_hash: Mapped[str] = mapped_column(String(64), unique=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    expires_at: Mapped[datetime] = mapped_column(UTCDateTime)
    created_at: Mapped[datetime] = mapped_column(UTCDateTime, default=utc_now)

    user: Mapped[User] = relationship()
