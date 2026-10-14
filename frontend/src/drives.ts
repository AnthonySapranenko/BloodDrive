// Mirrors PublicDrive in backend/app/schemas.py.
export type Drive = {
  id: number
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
  status: 'published' | 'cancelled'
  is_demo: boolean
  organization: {
    id: number
    name: string
    website_url: string | null
    contact_email: string | null
    is_demo: boolean
  }
}

export type Filters = { state: string; city: string; zip: string }

export async function fetchDrives(filters: Filters): Promise<Drive[]> {
  const params = new URLSearchParams()
  for (const [key, value] of Object.entries(filters)) {
    if (value.trim()) params.set(key, value.trim())
  }
  const response = await fetch(`/api/drives?${params}`).catch(() => {
    throw new Error("Drives could not be loaded. Check your connection and try again.")
  })
  if (response.status === 422) {
    throw new Error('Check the filters: state is 2 letters (like PA) and ZIP is 5 digits.')
  }
  if (!response.ok) throw new Error('Drives could not be loaded. Please try again.')
  return response.json()
}

const DAY_MS = 24 * 60 * 60 * 1000

export type Lineup = {
  headliner: Drive | null
  tiers: { name: string; drives: Drive[] }[]
}

/** Splits drives (already sorted soonest first) into a headliner and date tiers. */
export function buildLineup(drives: Drive[], now: Date): Lineup {
  // A cancelled drive never headlines; it stays visible in its tier.
  const headliner = drives.find((drive) => drive.status !== 'cancelled') ?? null
  const rest = drives.filter((drive) => drive !== headliner)
  const tiers = [
    { name: 'This week', drives: [] as Drive[] },
    { name: 'Next week', drives: [] as Drive[] },
    { name: 'Later', drives: [] as Drive[] },
  ]
  for (const drive of rest) {
    const daysAway = (new Date(drive.starts_at).getTime() - now.getTime()) / DAY_MS
    tiers[daysAway < 7 ? 0 : daysAway < 14 ? 1 : 2].drives.push(drive)
  }
  return { headliner, tiers: tiers.filter((tier) => tier.drives.length > 0) }
}

/** Date and time in the drive's own timezone, e.g. "Tue, Oct 13" and "10:00 AM – 4:00 PM EDT". */
export function formatWhen(drive: Drive): { date: string; time: string } {
  // shortcut: assumes a drive starts and ends on the same local day; show both dates if multi-day drives appear.
  const timeZone = drive.timezone
  const start = new Date(drive.starts_at)
  const end = new Date(drive.ends_at)
  const date = start.toLocaleDateString('en-US', { timeZone, weekday: 'short', month: 'short', day: 'numeric' })
  const startTime = start.toLocaleTimeString('en-US', { timeZone, hour: 'numeric', minute: '2-digit' })
  const endTime = end.toLocaleTimeString('en-US', { timeZone, hour: 'numeric', minute: '2-digit', timeZoneName: 'short' })
  return { date, time: `${startTime} – ${endTime}` }
}

/** Only http(s) links are shown, so a bad URL in the data can never run script. */
export function safeExternalUrl(url: string | null): string | null {
  if (!url) return null
  try {
    const parsed = new URL(url)
    return parsed.protocol === 'https:' || parsed.protocol === 'http:' ? parsed.href : null
  } catch {
    return null
  }
}
