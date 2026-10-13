from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, EmailStr, StringConstraints

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
    """Drive fields shown in the public directory. Internal fields are left out on purpose."""

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
