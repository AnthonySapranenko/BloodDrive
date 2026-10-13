"""Organizer sign-up, sign-in and sign-out.

Signing in stores a random token in an HttpOnly cookie and its SHA-256 hash in
`user_sessions`. Each request looks the hash up, so deleting the row signs out at once.
"""

import hashlib
import os
import secrets
from datetime import timedelta
from typing import Annotated

from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError
from fastapi import APIRouter, Cookie, Depends, HTTPException, Response, status
from sqlalchemy import delete, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db, utc_now
from app.models import MembershipRole, Organization, OrganizationMembership, User, UserSession
from app.schemas import LoginIn, Me, MyOrganization, SignupIn

SESSION_COOKIE = "session_token"
SESSION_LIFETIME = timedelta(days=14)
# Set COOKIE_SECURE=true in production so the cookie is only ever sent over HTTPS.
COOKIE_SECURE = os.getenv("COOKIE_SECURE", "false").lower() == "true"
COOKIE_SETTINGS = dict(httponly=True, samesite="lax", secure=COOKIE_SECURE)

password_hasher = PasswordHasher()
# Checked when the email is unknown, so a failed sign-in takes the same time either way.
DUMMY_HASH = password_hasher.hash("not-a-real-password")

router = APIRouter(prefix="/auth", tags=["auth"])

DbSession = Annotated[Session, Depends(get_db)]
SessionToken = Annotated[str | None, Cookie(alias=SESSION_COOKIE)]


def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def start_session(db: Session, user: User, response: Response) -> None:
    """Add a session row (the caller commits) and send its token as a cookie."""
    token = secrets.token_urlsafe(32)
    db.add(UserSession(token_hash=hash_token(token), user=user, expires_at=utc_now() + SESSION_LIFETIME))
    response.set_cookie(
        SESSION_COOKIE, token, max_age=int(SESSION_LIFETIME.total_seconds()), **COOKIE_SETTINGS
    )


def current_user(db: DbSession, token: SessionToken = None) -> User:
    """Dependency: the signed-in, active user, or 401."""
    if token:
        session = db.scalar(select(UserSession).where(UserSession.token_hash == hash_token(token)))
        if session and session.expires_at > utc_now() and session.user.is_active:
            return session.user
    raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Not signed in")


CurrentUser = Annotated[User, Depends(current_user)]


def require_org_member(org_id: int, user: CurrentUser, db: DbSession) -> Organization:
    """Dependency for routes with an `org_id` path parameter: only that organization's members pass."""
    membership = db.scalar(
        select(OrganizationMembership).where(
            OrganizationMembership.user_id == user.id,
            OrganizationMembership.organization_id == org_id,
        )
    )
    if membership is None:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "You are not a member of this organization")
    return membership.organization


def me_response(user: User) -> Me:
    return Me(
        id=user.id,
        name=user.name,
        email=user.email,
        organizations=[
            MyOrganization(id=m.organization.id, name=m.organization.name,
                           status=m.organization.status, role=m.role)
            for m in user.memberships
        ],
    )


@router.post("/signup", status_code=status.HTTP_201_CREATED)
def signup(body: SignupIn, db: DbSession, response: Response) -> Me:
    """Create the user, their organization (pending approval) and the owner membership, then sign in."""
    user = User(email=body.email.lower(), name=body.name, password_hash=password_hasher.hash(body.password))
    organization = Organization(name=body.organization_name)
    db.add(OrganizationMembership(user=user, organization=organization, role=MembershipRole.OWNER))
    start_session(db, user, response)
    try:
        db.commit()  # One commit: either all four rows are saved or none are.
    except IntegrityError:
        db.rollback()  # The only unique column here is the email.
        raise HTTPException(status.HTTP_409_CONFLICT, "An account with this email already exists")
    return me_response(user)


@router.post("/login")
def login(body: LoginIn, db: DbSession, response: Response) -> Me:
    user = db.scalar(select(User).where(User.email == body.email.lower()))
    try:
        password_hasher.verify(user.password_hash if user else DUMMY_HASH, body.password)
    except (VerificationError, InvalidHashError):
        user = None
    if user is None or not user.is_active:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid email or password")
    start_session(db, user, response)
    db.commit()
    return me_response(user)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(db: DbSession, response: Response, token: SessionToken = None) -> None:
    """Delete this browser's session. Safe to call when already signed out."""
    if token:
        db.execute(delete(UserSession).where(UserSession.token_hash == hash_token(token)))
        db.commit()
    response.delete_cookie(SESSION_COOKIE, **COOKIE_SETTINGS)


@router.get("/me")
def me(user: CurrentUser) -> Me:
    return me_response(user)
