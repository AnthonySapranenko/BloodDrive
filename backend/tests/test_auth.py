from datetime import timedelta

import pytest
from fastapi import HTTPException
from sqlalchemy import select, update

from app.approve_org import approve
from app.auth import SESSION_COOKIE, require_org_member
from app.database import utc_now
from app.models import (
    MembershipRole,
    Organization,
    OrganizationMembership,
    OrganizationStatus,
    User,
    UserSession,
)

SIGNUP = {
    "name": "Ada Organizer",
    "email": "Ada@Example.com",
    "password": "correct horse battery",
    "organization_name": "Campus Blood Club",
}


@pytest.fixture
def signed_up(client):
    response = client.post("/auth/signup", json=SIGNUP)
    assert response.status_code == 201
    return response


def login(client, email="ada@example.com", password=SIGNUP["password"]):
    return client.post("/auth/login", json={"email": email, "password": password})


def test_signup_creates_user_pending_org_and_owner_membership(signed_up, db_session):
    user = db_session.scalar(select(User))
    membership = db_session.scalar(select(OrganizationMembership))

    assert user.email == "ada@example.com"  # Stored lowercase.
    assert user.password_hash != SIGNUP["password"]
    assert membership.user == user
    assert membership.role == MembershipRole.OWNER
    assert membership.organization.name == "Campus Blood Club"
    assert membership.organization.status == OrganizationStatus.PENDING
    assert signed_up.json()["organizations"] == [
        {"id": membership.organization.id, "name": "Campus Blood Club", "status": "pending", "role": "owner"}
    ]


def test_signup_signs_the_user_in(signed_up, client):
    assert client.get("/auth/me").json()["email"] == "ada@example.com"


def test_duplicate_email_returns_409_regardless_of_case(signed_up, client, db_session):
    response = client.post("/auth/signup", json=SIGNUP | {"email": "ADA@example.COM"})

    assert response.status_code == 409
    assert len(db_session.scalars(select(Organization)).all()) == 1  # Nothing half-created.


@pytest.mark.parametrize(
    "field, value",
    [("password", "short"), ("password", "x" * 129), ("email", "not-an-email"), ("name", "   ")],
)
def test_invalid_signup_is_rejected(client, field, value):
    assert client.post("/auth/signup", json=SIGNUP | {field: value}).status_code == 422


def test_login_ignores_email_case(signed_up, client):
    client.cookies.clear()

    response = login(client, email="ADA@EXAMPLE.COM")

    assert response.status_code == 200
    assert SESSION_COOKIE in response.cookies


@pytest.mark.parametrize(
    "email, password",
    [("ada@example.com", "wrong password"), ("nobody@example.com", SIGNUP["password"])],
)
def test_bad_login_gets_the_same_401(signed_up, client, email, password):
    response = login(client, email, password)

    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid email or password"}


def test_login_requires_a_json_body(signed_up, client):
    # A plain HTML form on another site can't send JSON, which is part of the CSRF protection.
    form = {"email": "ada@example.com", "password": SIGNUP["password"]}
    assert client.post("/auth/login", data=form).status_code == 422


def test_me_without_a_cookie_returns_401(client):
    assert client.get("/auth/me").status_code == 401


def test_logout_makes_the_token_stop_working(signed_up, client, db_session):
    token = signed_up.cookies[SESSION_COOKIE]

    assert client.post("/auth/logout").status_code == 204
    client.cookies.set(SESSION_COOKIE, token)  # Replay the old token.

    assert client.get("/auth/me").status_code == 401
    assert db_session.scalar(select(UserSession)) is None


def test_logout_when_signed_out_is_harmless(client):
    assert client.post("/auth/logout").status_code == 204


@pytest.mark.parametrize(
    "change",
    [
        update(UserSession).values(expires_at=utc_now() - timedelta(seconds=1)),
        update(User).values(is_active=False),
    ],
    ids=["expired session", "deactivated user"],
)
def test_expired_session_or_deactivated_user_returns_401(signed_up, client, db_session, change):
    db_session.execute(change)
    db_session.commit()

    assert client.get("/auth/me").status_code == 401


def test_deactivated_user_cannot_log_in(signed_up, client, db_session):
    db_session.execute(update(User).values(is_active=False))
    db_session.commit()

    assert login(client).status_code == 401


def test_password_hash_never_appears_in_responses(signed_up, client, db_session):
    password_hash = db_session.scalar(select(User)).password_hash

    for response in (signed_up, login(client), client.get("/auth/me")):
        assert password_hash not in response.text
        assert "password" not in response.json()


def test_require_org_member_only_lets_members_through(signed_up, db_session):
    user = db_session.scalar(select(User))
    own_org = user.memberships[0].organization
    other_org = Organization(name="Someone Else's Club")
    db_session.add(other_org)
    db_session.commit()

    assert require_org_member(own_org.id, user, db_session) == own_org
    with pytest.raises(HTTPException) as error:
        require_org_member(other_org.id, user, db_session)
    assert error.value.status_code == 403


def test_approve_org(signed_up, db_session):
    org = db_session.scalar(select(Organization))

    assert approve(db_session, org.id).status == OrganizationStatus.APPROVED
    assert approve(db_session, 9999) is None
