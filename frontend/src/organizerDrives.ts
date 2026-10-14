import type { Drive } from './drives'

/** Thrown on 401 so pages can send the organizer back to sign in. */
export class NotSignedInError extends Error {
  constructor() {
    super('Please sign in again.')
  }
}

/** A rejected save: `fields` holds a message per form field, `message` anything else. */
export class SaveError extends Error {
  fields: Record<string, string>
  constructor(message: string, fields: Record<string, string> = {}) {
    super(message)
    this.fields = fields
  }
}

// Mirrors DriveIn in backend/app/schemas.py. Times are local to `timezone`, e.g. "2027-01-15T10:00".
export type DriveInput = {
  title: string
  description: string | null
  starts_at: string
  ends_at: string
  timezone: string
  venue_name: string
  street_address: string
  city: string
  state: string
  postal_code: string
  registration_url: string | null
  capacity: number | null
  status: Drive['status']
}

export const US_TIMEZONES: [string, string][] = [
  ['America/New_York', 'Eastern'],
  ['America/Chicago', 'Central'],
  ['America/Denver', 'Mountain'],
  ['America/Phoenix', 'Arizona'],
  ['America/Los_Angeles', 'Pacific'],
  ['America/Anchorage', 'Alaska'],
  ['Pacific/Honolulu', 'Hawaii'],
]

// Shown instead of the backend's technical messages, which are written for developers.
const FIELD_MESSAGES: Record<string, string> = {
  title: 'Enter a title.',
  venue_name: 'Enter the venue.',
  street_address: 'Enter the street address.',
  city: 'Enter the city.',
  state: 'Use the 2-letter state code, like PA.',
  postal_code: 'Use a 5-digit ZIP code.',
  registration_url: 'Use a full link starting with https://',
  capacity: 'Use a whole number above 0, or leave it blank.',
  timezone: 'Pick a time zone.',
  starts_at: 'Check the date and start time.',
  ends_at: 'Check the date and end time.',
}

/** Date ("2027-01-15") and time ("10:00") of a UTC instant, as a clock in `timeZone` shows it. */
export function localDateTime(iso: string, timeZone: string): { date: string; time: string } {
  const parts = Object.fromEntries(
    new Intl.DateTimeFormat('en-US', {
      timeZone,
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
      hourCycle: 'h23',
    })
      .formatToParts(new Date(iso))
      .map((part) => [part.type, part.value]),
  )
  return { date: `${parts.year}-${parts.month}-${parts.day}`, time: `${parts.hour}:${parts.minute}` }
}

/** Builds the API body from the drive form's fields. */
export function formToDriveInput(fields: Record<string, string>, status: Drive['status']): DriveInput {
  // shortcut: one date for start and end, matching formatWhen; add an end date if overnight drives appear.
  return {
    title: fields.title,
    description: fields.description.trim() || null,
    starts_at: `${fields.date}T${fields.start_time}`,
    ends_at: `${fields.date}T${fields.end_time}`,
    timezone: fields.timezone,
    venue_name: fields.venue_name,
    street_address: fields.street_address,
    city: fields.city,
    state: fields.state,
    postal_code: fields.postal_code,
    registration_url: fields.registration_url.trim() || null,
    capacity: fields.capacity ? Number(fields.capacity) : null,
    status,
  }
}

type ValidationError = { loc: (string | number)[]; msg: string }

/** Turns FastAPI's 422 body into one message per field, plus whole-drive problems. */
export function saveErrorFrom(detail: ValidationError[]): SaveError {
  const fields: Record<string, string> = {}
  const general: string[] = []
  for (const error of detail) {
    const field = error.loc[1]
    if (typeof field === 'string' && FIELD_MESSAGES[field]) fields[field] = FIELD_MESSAGES[field]
    else general.push(error.msg.replace(/^Value error, /, '') + '.')
  }
  return new SaveError(general.join(' ') || 'Check the highlighted fields.', fields)
}

async function request(path: string, init?: RequestInit): Promise<Response> {
  const response = await fetch(path, init).catch(() => {
    throw new Error("Couldn't reach BloodDrive. Check your connection and try again.")
  })
  if (response.status === 401) throw new NotSignedInError()
  if (response.status === 404) throw new Error('That drive was not found.')
  return response
}

function drivesUrl(orgId: number, driveId?: number): string {
  return `/api/organizations/${orgId}/drives` + (driveId ? `/${driveId}` : '')
}

async function json<T>(response: Response): Promise<T> {
  if (!response.ok) throw new Error('Something went wrong. Please try again.')
  return response.json()
}

export async function listOwnDrives(orgId: number): Promise<Drive[]> {
  return json(await request(drivesUrl(orgId)))
}

export async function getOwnDrive(orgId: number, driveId: number): Promise<Drive> {
  return json(await request(drivesUrl(orgId, driveId)))
}

/** Creates the drive when `driveId` is undefined, otherwise replaces it. */
export async function saveDrive(orgId: number, driveId: number | undefined, input: DriveInput): Promise<Drive> {
  const response = await request(drivesUrl(orgId, driveId), {
    method: driveId ? 'PUT' : 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(input),
  })
  if (response.status === 422) throw saveErrorFrom((await response.json()).detail)
  return json(response)
}

export async function deleteDrive(orgId: number, driveId: number): Promise<void> {
  const response = await request(drivesUrl(orgId, driveId), { method: 'DELETE' })
  if (response.status === 409) throw new Error((await response.json()).detail)
  if (!response.ok) throw new Error('Something went wrong. Please try again.')
}
