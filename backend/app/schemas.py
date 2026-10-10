from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models import DriveStatus


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
