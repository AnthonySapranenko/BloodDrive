"""Organizers create and edit their own organization's drives.

Every route requires membership of `org_id`, and every drive is looked up by both its
id and `org_id`, so changing the ids in the URL can never reach another organization's drive.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth import require_org_member
from app.database import get_db
from app.models import BloodDrive, DriveStatus, Organization
from app.schemas import DriveIn, PublicDrive

router = APIRouter(prefix="/api/organizations/{org_id}/drives", tags=["drive management"])

DbSession = Annotated[Session, Depends(get_db)]
MemberOrg = Annotated[Organization, Depends(require_org_member)]


def own_drive(drive_id: int, org: MemberOrg, db: DbSession) -> BloodDrive:
    """Dependency: the drive, if it belongs to this organization; otherwise 404."""
    drive = db.scalar(
        select(BloodDrive).where(BloodDrive.id == drive_id, BloodDrive.organization_id == org.id)
    )
    if drive is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Drive not found")
    return drive


OwnDrive = Annotated[BloodDrive, Depends(own_drive)]


@router.get("", response_model=list[PublicDrive])
def list_own_drives(org: MemberOrg, db: DbSession):
    """All of the organization's drives, drafts and past ones included, newest first."""
    # shortcut: no pagination; add it if an organization ever has hundreds of drives.
    return db.scalars(
        select(BloodDrive).where(BloodDrive.organization_id == org.id).order_by(BloodDrive.starts_at.desc())
    ).all()


@router.post("", response_model=PublicDrive, status_code=status.HTTP_201_CREATED)
def create_drive(body: DriveIn, org: MemberOrg, db: DbSession):
    drive = BloodDrive(organization=org, **body.to_columns())
    db.add(drive)
    db.commit()
    return drive


@router.get("/{drive_id}", response_model=PublicDrive)
def get_drive(drive: OwnDrive):
    return drive


@router.put("/{drive_id}", response_model=PublicDrive)
def update_drive(body: DriveIn, drive: OwnDrive, db: DbSession):
    """Replace every editable field, including status (publish, unpublish or cancel)."""
    for column, value in body.to_columns().items():
        setattr(drive, column, value)
    db.commit()
    return drive


@router.delete("/{drive_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_drive(drive: OwnDrive, db: DbSession) -> None:
    # Published or cancelled drives may be saved by donors; unpublish or cancel them instead.
    if drive.status != DriveStatus.DRAFT:
        raise HTTPException(status.HTTP_409_CONFLICT, "Only drafts can be deleted. Unpublish or cancel the drive instead.")
    db.delete(drive)
    db.commit()
