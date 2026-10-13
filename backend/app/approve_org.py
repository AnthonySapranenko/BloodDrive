"""Approve an organization so its published drives appear in the public directory.

Run from the backend folder:
    python -m app.approve_org          lists organizations waiting for approval
    python -m app.approve_org <id>     approves one
"""

import sys

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import Organization, OrganizationStatus


def approve(session: Session, org_id: int) -> Organization | None:
    organization = session.get(Organization, org_id)
    if organization:
        organization.status = OrganizationStatus.APPROVED
        session.commit()
    return organization


if __name__ == "__main__":
    with SessionLocal() as session:
        if len(sys.argv) == 1:
            pending = session.scalars(
                select(Organization).where(Organization.status == OrganizationStatus.PENDING)
            ).all()
            for org in pending:
                print(f"{org.id}\t{org.name}")
            print(f"{len(pending)} organization(s) pending.")
        elif len(sys.argv) == 2 and sys.argv[1].isdigit():
            organization = approve(session, int(sys.argv[1]))
            if organization is None:
                sys.exit(f"No organization with id {sys.argv[1]}.")
            print(f"Approved: {organization.name}")
        else:
            sys.exit("Usage: python -m app.approve_org [organization id]")
