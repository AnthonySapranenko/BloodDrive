from typing import Annotated

from fastapi import Depends, FastAPI, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload

from app.database import get_db, utc_now
from app.models import BloodDrive, DriveStatus
from app.schemas import PublicDrive

app = FastAPI(title="BloodDrive API")

# Drafts are private; cancelled drives stay listed so donors who saved them see they're off.
PUBLIC_STATUSES = (DriveStatus.PUBLISHED, DriveStatus.CANCELLED)


@app.get("/health")
def health() -> dict[str, str]:
    """Report that the API is running. Used by tests and, later, the hosting provider."""
    return {"status": "ok"}


@app.get("/drives", response_model=list[PublicDrive])
def list_drives(
    db: Annotated[Session, Depends(get_db)],
    state: Annotated[str | None, Query(pattern=r"^[A-Za-z]{2}$")] = None,
    city: Annotated[str | None, Query(min_length=1, max_length=100)] = None,
    zip: Annotated[str | None, Query(pattern=r"^\d{5}$")] = None,
):
    """Public directory: upcoming and in-progress drives, soonest first."""
    # shortcut: returns every match with no pagination, add paging once listings reach the hundreds.
    query = (
        select(BloodDrive)
        .options(joinedload(BloodDrive.organization))
        .where(BloodDrive.status.in_(PUBLIC_STATUSES), BloodDrive.ends_at > utc_now())
        .order_by(BloodDrive.starts_at)
    )
    if state:
        query = query.where(BloodDrive.state == state.upper())
    if city:
        query = query.where(func.lower(BloodDrive.city) == city.strip().lower())
    if zip:
        query = query.where(BloodDrive.postal_code == zip)

    return db.scalars(query).all()
