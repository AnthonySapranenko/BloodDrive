# Next Time

Handoff notes, last updated 2026-10-13. Read this, `README.md` and `BOSS.md` before starting.

## Where things stand

- **Branch:** `organizer-auth`. Steps 2 and 3 are committed locally; push when you're ready.
- **`main`:** unchanged at `b8f2ec2 Add public drive directory frontend`.
- **Tests:** 52 backend tests pass. Run them from `backend` with `.\.venv\Scripts\python.exe -m pytest` (the venv lives in `backend/.venv`).
- **Local database:** at migration `b6824990c554`. Step 2 didn't change the schema.
- **Milestone:** 3, organizer management. Steps 1–3 are done; drive management is next.

## Decisions made this session

1. **Sign-in method: database sessions with a cookie, not JWT.**
   - On sign-in, the server makes a long random token, stores a SHA-256 hash of it in `user_sessions`, and sends the token to the browser as a cookie.
   - Why: signing out deletes the row, so it takes effect immediately. A JWT keeps working until it expires. No extra library needed.
   - Cookie settings: `HttpOnly` (JavaScript can't read it), `SameSite=Lax` (other sites can't send it), `Secure` turned on in production by an environment variable.
   - CSRF protection: `SameSite=Lax` plus requiring JSON request bodies. No CORS.
2. **New organizations start `pending`.** Their drives stay out of the public directory until an admin approves them with a one-line admin script. No admin interface.
3. **Signing up creates the organization at the same time.** One form: name, email, password, organization name. The user becomes the organization's `owner`.

Other rules agreed in the plan:

- Passwords are hashed with Argon2 (`argon2-cffi`). Length 8 to 128 characters, no "must include a symbol" rules.
- Emails are stored lowercase, so sign-in ignores letter case.
- Sessions last 14 days. Expired sessions and deactivated users are rejected.
- Sign-in failures always say "Invalid email or password". When the email doesn't exist, the server still checks the password against a dummy hash, so response timing doesn't reveal which emails have accounts.
- No response ever includes `password_hash` or a token.

## What was built (step 1)

- **New tables** in `backend/app/models.py`:
  - `users`: email (unique), name, password_hash, is_active, timestamps.
  - `organization_memberships`: user, organization and role (`owner` only for now). A user can join each organization only once.
  - `user_sessions`: token_hash (unique), user, expires_at.
- **`organizations.status`:** `pending` or `approved`. New organizations default to `pending`. The migration marks organizations that already existed as `approved`.
- **`string_enum` helper** in `models.py`, shared by all status and role fields.
- **Public directory** (`GET /drives`) now only lists drives from approved organizations.
- **Demo seed** creates its organizations as `approved`.
- **New tests:**
  - the migration keeps existing data
  - a new organization starts as pending
  - an email can only be used once
  - a membership links a user to an organization as owner
  - a user can only join an organization once
  - each session token is unique
  - drives from pending organizations are hidden from the directory

### Lesson learned: SQLite migrations

SQLite can't change a table in place. Alembic copies the table, drops the original and renames the copy. Dropping `organizations` was blocked because drives have a foreign key pointing at it. The migration failed halfway, and SQLite doesn't undo schema changes on failure.

The fix is in `backend/alembic/env.py`: migrations on SQLite now switch foreign keys off first (`PRAGMA foreign_keys=OFF`, then a commit). A test runs the migration with real rows in place, so this can't come back unnoticed.

Two things to check after `alembic revision --autogenerate`:
- It can write the same CHECK constraint twice.
- In the undo step, a column that has a CHECK constraint needs `drop_constraint` before `drop_column`.

Always read generated migrations before running them.

## Step 2 (done 2026-10-13): sign-up and sign-in API

- `backend/app/auth.py`: `POST /auth/signup`, `POST /auth/login`, `POST /auth/logout`, `GET /auth/me`, plus the `current_user` and `require_org_member` dependencies.
- Cookie name `session_token`. Set `COOKIE_SECURE=true` in production.
- `python -m app.approve_org` lists pending organizations, and `python -m app.approve_org <id>` approves one.
- Tests are in `backend/tests/test_auth.py`.

## Step 3 (done 2026-10-13): sign-up and sign-in pages

- React Router 8 (`BrowserRouter` in `main.tsx`, routes in `App.tsx`). Pages: `/signup`, `/login`, `/organizer` (redirects to `/login` when signed out).
- API calls in `frontend/src/auth.ts`, pages in `frontend/src/OrganizerPages.tsx`, tests in `frontend/src/auth.test.ts`.
- Checked end to end through the Vite proxy with curl; not clicked through in a real browser yet.
- **Watch out:** the Vite proxy forwards every path starting with `/drives`, so a future `/drives/:id` page would be swallowed. Move the API under `/api` before adding one.
- **Port clash:** another local project uses ports 5173 and 8000. Stop it before running BloodDrive's dev servers.

## Next

- **Drive management.** Organizers create, edit, publish and unpublish their own drives, protected by `require_org_member`. This needs its own plan.
- **When Milestone 3 is done:** open a pull request from `organizer-auth` to `main`.

## Deferred on purpose

- **Email verification and password reset by email:** these need an email-sending service. Until then, use admin scripts.
- **Login rate limiting:** add before deployment (Milestone 4). Until then, nothing limits how many passwords someone can try.
- **Inviting more members to an organization:** the table supports it, but there's no feature for it yet.
- **Clearing out expired session rows:** they're rejected when used, but nothing deletes them yet.
- **Switching to PostgreSQL** before deployment (already planned). The new migration hasn't been tested on PostgreSQL.

## Known noise

- When tests run, `StarletteDeprecationWarning: Using httpx with starlette.testclient is deprecated`. This was already there before this session and isn't caused by our code.
