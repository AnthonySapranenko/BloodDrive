from datetime import UTC, datetime
from typing import Annotated
from zoneinfo import ZoneInfo

from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    HttpUrl,
    StringConstraints,
    field_validator,
    model_validator,
)

from app.database import utc_now
from app.models import DriveStatus, MembershipRole, OrganizationStatus

Name = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=200)]
# Long enough to be guessable only slowly; capped so huge inputs can't make hashing slow.
Password = Annotated[str, StringConstraints(min_length=8, max_length=128)]


class PublicOrganization(BaseModel):
    """Organization fields that are safe to show to anyone."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    website_url: str | None
    contact_email: str | None
    is_demo: bool


class PublicDrive(BaseModel):
    """Drive fields shown in the public directory (and to organizers). Internal fields are left out on purpose."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str | None
    starts_at: datetime
    ends_at: datetime
    timezone: str
    venue_name: str
    street_address: str
    city: str
    state: str
    postal_code: str
    registration_url: str | None
    capacity: int | None
    status: DriveStatus
    is_demo: bool
    organization: PublicOrganization


class SignupIn(BaseModel):
    """One form creates the organizer account and their organization."""

    name: Name
    email: EmailStr
    password: Password
    organization_name: Name


class LoginIn(BaseModel):
    email: EmailStr
    # No minimum here: a wrong password should get "Invalid email or password", not a 422.
    password: Annotated[str, StringConstraints(max_length=128)]


class MyOrganization(BaseModel):
    id: int
    name: str
    status: OrganizationStatus
    role: MembershipRole


class Me(BaseModel):
    """The signed-in user. Never includes the password hash."""

    id: int
    name: str
    email: str
    organizations: list[MyOrganization]


class DriveIn(BaseModel):
    """A drive as an organizer submits it.

    `starts_at` and `ends_at` are wall-clock times in `timezone` with no UTC offset,
    e.g. "2026-11-03T10:00" in "America/New_York". Validation converts them to UTC.
    """

    title: Name
    description: Annotated[str, StringConstraints(strip_whitespace=True, max_length=5000)] | None = None
    starts_at: datetime
    ends_at: datetime
    timezone: Annotated[str, StringConstraints(max_length=64)]
    venue_name: Name
    street_address: Name
    city: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=100)]
    state: Annotated[str, StringConstraints(strip_whitespace=True, to_upper=True, pattern=r"^[A-Za-z]{2}$")]
    postal_code: Annotated[str, StringConstraints(strip_whitespace=True, pattern=r"^\d{5}$")]
    # Only http(s) links pass, so the directory can never link to a `javascript:` URL.
    registration_url: HttpUrl | None = None
    capacity: Annotated[int, Field(gt=0, le=100_000)] | None = None
    status: DriveStatus = DriveStatus.DRAFT

    @field_validator("timezone")
    @classmethod
    def known_timezone(cls, value: str) -> str:
        try:
            ZoneInfo(value)
        except (KeyError, ValueError):  # Unknown name, or not a valid zone name at all.
            raise ValueError("Unknown timezone")
        return value

    @model_validator(mode="after")
    def convert_times_to_utc(self) -> "DriveIn":
        if self.starts_at.tzinfo or self.ends_at.tzinfo:
            raise ValueError("Times must be local to the drive's timezone, without a UTC offset")
        zone = ZoneInfo(self.timezone)
        # Convert to UTC before comparing: Python compares two times in the same zone by
        # wall clock alone, which is wrong across a daylight-saving change.
        self.starts_at = self.starts_at.replace(tzinfo=zone).astimezone(UTC)
        self.ends_at = self.ends_at.replace(tzinfo=zone).astimezone(UTC)
        if self.ends_at <= self.starts_at:
            raise ValueError("The drive must end after it starts")
        if self.ends_at <= utc_now():
            raise ValueError("This drive has already ended")
        return self

    def to_columns(self) -> dict:
        """Field values ready to set on a BloodDrive row."""
        columns = self.model_dump()
        columns["registration_url"] = str(self.registration_url) if self.registration_url else None
        return columns
