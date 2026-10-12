# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Stack

React + TypeScript (Vite) frontend calling a Python/FastAPI backend. SQLite in development, PostgreSQL before deployment. Chosen by the developer during planning (see README.md and BOSS.md).

## Users

- **Donors (primary, first):** college students in State College, PA (Penn State area), usually on a phone between classes, looking for an upcoming blood drive they can get to and a link to sign up.
- **Organizers:** student clubs, churches, nonprofits, and community groups that run blood drives and need to promote them. Organizer tools come after the public directory.

## Product Purpose

BloodDrive is a directory of blood drives. Donors browse published drives, filter by state, city, or ZIP code, see when and where each one is, and follow the official registration link. Success means a donor finds a drive they can attend and reaches the official sign-up page quickly.

## Positioning

Organizer-submitted listings across many organizations in one place, rather than one blood collection provider's own schedule. BloodDrive does not book appointments; it points to the official registration page.

## Capabilities and Constraints

- Public directory shows only published and cancelled drives that have not ended, soonest first. Cancelled drives stay visible, clearly labeled, so donors who saved them learn they are off.
- Filters: 2-letter state, city name, 5-digit ZIP. No distance or map search in the MVP. US only.
- Times are stored in UTC; each drive has an IANA timezone and must be displayed in that local time.
- Registration links are external, official pages, never presented as BloodDrive's own booking.
- Optional capacity is informational only.
- No donor accounts, medical history, or eligibility decisions. Point donors to official organizations for eligibility.
- Pagination is not built yet.

## Brand Commitments

- Name: "BloodDrive". No logo, colors, or fonts exist yet.
- Voice: warm and encouraging, never preachy or guilt-driven.
- Must not imply affiliation with any blood collection organization.

## Evidence on Hand

No real drives, organizers, testimonials, or statistics yet. All current data is demonstration data (`backend/app/seed_demo.py`), titled "[DEMO]" with `example.com` links. Never present demo data or invented figures as real.

## Product Principles

1. Get the donor to a real, attendable drive and its official sign-up link in as few steps as possible.
2. Trust over polish: demo, cancelled, and external-link states are always unmistakable.
3. Phone-first: the directory must be fully usable one-handed on a small screen.
4. Encourage without pressure: motivate donating, never guilt.

## Accessibility & Inclusion

Target WCAG 2.2 AA: readable contrast, keyboard and screen-reader support for filters and results, and status communicated by text, not color alone.
