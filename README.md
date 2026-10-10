# Readme, BloodDrive

**BloodDrive is a blood-drive management and discovery platform designed to help organizations promote blood drives and make it easier for donors to find them.**

The initial target users are student organizations, churches, nonprofits, and community groups that organize blood drives. Donors will be able to browse published drives, search by location and date, view important details, and follow official links to make appointments.

The long-term vision is to make organizing, promoting, and discovering blood drives simpler through one accessible platform.

## Project Goals

- Build a complete, deployed full-stack application by the end of 2026.
- Create a strong, demonstrable computer science portfolio project.
- Solve a real problem for blood-drive organizers and potential donors.
- Keep the initial scope small enough for a beginner developer to complete.
- Validate the idea with real users before expanding it.
- Design the application so that future features and integrations can be added safely.

## Core Problem

Blood-drive organizers need effective ways to promote their events, while potential donors may struggle to discover nearby opportunities across different organizations.

BloodDrive aims to connect organizers and donors through a searchable directory of blood drives, with tools for organizers to manage their listings.

The platform will initially manage its own listings. It will not depend on having access to private APIs from existing blood donation organizations.

## Target Users

### Organizers

Student clubs, churches, nonprofits, community organizations, and other groups that coordinate or promote blood drives.

### Donors

People looking for blood drives who want to find relevant event information and navigate to an official appointment or registration page.

## MVP Features

The first release should prioritize the following features.

### Public Drive Discovery

- Browse published blood-drive listings.
- Search or filter by location and date.
- View a drive's name, date, time, address, organizer, and description.
- Access an official appointment or registration link when available.
- Use the directory on desktop and mobile devices.

### Drive Management

- Create an organizer account and sign in.
- Create and edit blood-drive listings.
- Publish or unpublish listings.
- Manage only the listings the organizer is authorized to control.
- Validate required fields and prevent invalid or incomplete listings from being published.

### Data and Administration

- Store drive and organizer information in a database.
- Use clearly labeled demonstration data during development.
- Keep published listings separate from drafts.
- Provide a basic way to handle inaccurate, outdated, or inappropriate listings.
- Protect account information and prevent unauthorized changes.

### Deployment

- Deploy a usable version online.
- Include setup instructions so another developer can run the project.
- Add automated tests for important backend behavior.
- Provide a polished README and screenshots when the interface is ready.

## Out of Scope for the First Release

To keep the MVP achievable, do not initially build:

- Direct appointment booking or payment processing.
- A custom blood donor eligibility determination system.
- Medical advice or individualized medical recommendations.
- Automatic aggregation from every blood donation provider.
- Private integrations without explicit authorization.
- Native iOS or Android applications.
- Complex analytics, messaging, or recommendation algorithms.

Where appropriate, the application should direct donors to official organizations for appointments and authoritative eligibility information.

## Proposed Technology Stack

The final stack should be confirmed after inspecting the existing repository.

- **Backend:** Python and FastAPI.
- **Database:** PostgreSQL for production; a simpler local database may be used during initial development if justified.
- **Frontend:** A modern, responsive web application. Evaluate React with TypeScript if the repository is not already committed to a frontend framework.
- **Testing:** pytest for backend tests, with frontend testing added as the interface develops.
- **Version control:** Git and GitHub.
- **Deployment:** Choose an appropriate hosting provider after the application architecture is established.

Avoid introducing extra frameworks, services, or infrastructure unless they solve a real need.

## Initial Data Model

The exact schema should be proposed and reviewed before implementation. The likely core entities are:

### User

- Unique identifier.
- Name.
- Email address.
- Securely managed authentication credentials.
- Account role and status.

### Organization

- Unique identifier.
- Name.
- Description.
- Public contact information.
- Organization status.

### Organization Membership

- User identifier.
- Organization identifier.
- Role within the organization.

This allows multiple authorized users to manage an organization's listings in the future, without requiring that feature to be fully implemented in the first iteration.

### Blood Drive

- Unique identifier.
- Title and description.
- Organization identifier.
- Start and end date/time.
- Location and address.
- Optional coordinates for geographic search.
- Official registration or appointment URL.
- Publication status.
- Created and updated timestamps.

The design should account for time zones, validation, duplicate submissions, and expired listings.

## Data Integrity and Trust

BloodDrive must not present invented drives as real events.

- Clearly label all demonstration data.
- Do not invent actual event dates, addresses, organizers, or appointment links.
- Obtain permission before publishing real organizations' information where appropriate.
- Use authorized integrations or explicitly permitted data sources.
- Validate external links and distinguish official registration links from general information.
- Make it possible to correct or remove outdated listings.
- Do not collect medical history or unnecessary sensitive donor information.

## Development Approach

The project will use an incremental Plan, Implement, Review, Test, and Explain workflow.

1. Inspect the repository and existing documentation.
2. Agree on a minimal architecture and feature plan.
3. Initialize or verify Git and make a documentation baseline commit.
4. Build the smallest useful feature end to end.
5. Test it before expanding the scope.
6. Review changes and explain them in beginner-friendly language.
7. Deploy and obtain feedback from potential users.
8. Prioritize improvements based on that feedback.

Do not generate the entire application in one large step.

## Definition of Done

A feature is complete when:

- Its intended behavior is clear.
- The implementation fits the agreed architecture.
- Relevant tests pass.
- Errors and invalid inputs are handled reasonably.
- Security and authorization implications are reviewed.
- Documentation is updated where necessary.
- Changes are reviewed before being committed.

## Milestones

**Milestone 1 — Planning and foundation**

Inspect the repository, choose the stack, define the first data model, and establish a working development environment.

**Milestone 2 — Public directory**

Build a responsive directory with search, filtering, drive details, and clearly labeled demonstration data.

**Milestone 3 — Organizer management**

Implement authentication, authorization, and the ability to create, edit, and publish listings.

**Milestone 4 — Pilot and deployment**

Deploy the application, test it with a small number of real organizers if possible, and improve it based on feedback.

**Milestone 5 — Polish**

Improve accessibility, testing, reliability, performance, documentation, and the project presentation.

## Current Status

**Stage:** Planning and architecture.

The product direction is an organizer-focused blood-drive management platform with public discovery. No production data integrations should be assumed to exist.

The immediate next task is to inspect the existing repository and propose a small, achievable implementation plan before writing application code.