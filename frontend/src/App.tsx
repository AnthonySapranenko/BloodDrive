import { useEffect, useState, type FormEvent } from 'react'

import { buildLineup, fetchDrives, formatWhen, safeExternalUrl, type Drive, type Filters } from './drives'

const NO_FILTERS: Filters = { state: '', city: '', zip: '' }
const TIER_SIZE: Record<string, string> = { 'This week': 'large', 'Next week': 'medium', Later: 'small' }

type Load =
  | { status: 'loading' }
  | { status: 'error'; message: string }
  | { status: 'ready'; drives: Drive[]; loadedAt: Date }

export default function App() {
  const [form, setForm] = useState<Filters>(NO_FILTERS)
  const [filters, setFilters] = useState<Filters>(NO_FILTERS)
  const [load, setLoad] = useState<Load>({ status: 'loading' })

  useEffect(() => {
    let current = true
    fetchDrives(filters)
      .then((drives) => current && setLoad({ status: 'ready', drives, loadedAt: new Date() }))
      .catch((error: Error) => current && setLoad({ status: 'error', message: error.message }))
    return () => {
      current = false // Ignore a slower, older request that finishes after a newer one.
    }
  }, [filters])

  const filtered = Object.values(filters).some(Boolean)

  function submit(event: FormEvent) {
    event.preventDefault()
    setLoad({ status: 'loading' })
    setFilters(form)
  }

  function clear() {
    setForm(NO_FILTERS)
    setLoad({ status: 'loading' })
    setFilters(NO_FILTERS)
  }

  function retry() {
    setLoad({ status: 'loading' })
    setFilters({ ...filters }) // A new object re-runs the effect with the same filters.
  }

  return (
    <>
      <header className="masthead">
        <div className="wrap">
          <h1 className="wordmark">BloodDrive</h1>
          <p className="welcome">Upcoming blood drives near you. Pick one, then sign up on the organizer's official page.</p>
          <form className="filters" onSubmit={submit} aria-label="Filter drives">
            <label>
              State
              <input
                value={form.state}
                onChange={(e) => setForm({ ...form, state: e.target.value.toUpperCase() })}
                placeholder="e.g. PA"
                maxLength={2}
                pattern="[A-Za-z]{2}"
                title="Two-letter state code, like PA"
                autoComplete="address-level1"
              />
            </label>
            <label>
              City
              <input
                value={form.city}
                onChange={(e) => setForm({ ...form, city: e.target.value })}
                placeholder="e.g. State College"
                maxLength={100}
                autoComplete="address-level2"
              />
            </label>
            <label>
              ZIP
              <input
                value={form.zip}
                onChange={(e) => setForm({ ...form, zip: e.target.value })}
                placeholder="e.g. 16801"
                inputMode="numeric"
                maxLength={5}
                pattern="\d{5}"
                title="Five-digit ZIP code"
                autoComplete="postal-code"
              />
            </label>
            <div className="filter-actions">
              <button type="submit">Find drives</button>
              {filtered && (
                <button type="button" className="clear" onClick={clear}>
                  Clear
                </button>
              )}
            </div>
          </form>
        </div>
      </header>

      <main className="wrap" aria-live="polite" aria-busy={load.status === 'loading'}>
        {load.status === 'loading' && <p className="status">Loading drives…</p>}
        {load.status === 'error' && (
          <div className="status error" role="alert">
            <p>{load.message}</p>
            <button type="button" className="text-button" onClick={retry}>
              Try again
            </button>
          </div>
        )}
        {load.status === 'ready' && (
          <Directory drives={load.drives} now={load.loadedAt} filtered={filtered} onClear={clear} />
        )}
      </main>

      <footer className="wrap footer">
        <p>
          BloodDrive lists drives submitted by organizers and is not affiliated with any blood collection organization.
          Check eligibility and appointment details with the organization running the drive.
        </p>
      </footer>
    </>
  )
}

function Directory({
  drives,
  now,
  filtered,
  onClear,
}: {
  drives: Drive[]
  now: Date
  filtered: boolean
  onClear: () => void
}) {
  if (drives.length === 0) {
    return (
      <div className="status">
        <p>{filtered ? 'No upcoming drives match those filters.' : 'No upcoming drives are listed yet.'}</p>
        {filtered && (
          <button type="button" className="text-button" onClick={onClear}>
            Show all drives
          </button>
        )}
      </div>
    )
  }

  const { headliner, tiers } = buildLineup(drives, now)

  return (
    <>
      {drives.some((drive) => drive.is_demo) && (
        <p className="demo-notice">
          <span className="tag">Demo</span> Listings marked Demo are examples for testing, not real blood drives.
        </p>
      )}
      {headliner && (
        <section className="tier headliner" aria-label="Next drive">
          <DriveEntry
            drive={headliner}
            size="headline"
            lead={new Date(headliner.starts_at) <= now ? 'Happening now' : 'Next up'}
          />
        </section>
      )}
      {tiers.map((tier) => (
        <section className="tier" key={tier.name} aria-labelledby={`tier-${tier.name}`}>
          <h2 id={`tier-${tier.name}`} className="tier-name">
            {tier.name}
          </h2>
          <ul className={`drives ${TIER_SIZE[tier.name]}`}>
            {tier.drives.map((drive) => (
              <li key={drive.id}>
                <DriveEntry drive={drive} size={TIER_SIZE[tier.name]} />
              </li>
            ))}
          </ul>
        </section>
      ))}
    </>
  )
}

function DriveEntry({ drive, size, lead }: { drive: Drive; size: string; lead?: string }) {
  const { date, time } = formatWhen(drive)
  const cancelled = drive.status === 'cancelled'
  const registerUrl = cancelled ? null : safeExternalUrl(drive.registration_url)
  // Lower tiers are smaller acts: just venue, when, town and tags.
  const compact = size === 'small'

  return (
    <article className={`drive ${size}${cancelled ? ' cancelled' : ''}`}>
      <h3 className="venue">
        <span>{drive.venue_name}</span>
      </h3>
      <div className="details">
        <p className="when">
          {lead && <span className="lead">{lead} · </span>}
          <time dateTime={drive.starts_at}>
            <span className="nowrap">{date}</span> · <span className="nowrap">{time}</span>
          </time>
        </p>
        {compact ? (
          <p className="meta">
            {drive.city}, {drive.state} · {drive.organization.name}
          </p>
        ) : (
          <>
            <p className="meta">
              {drive.street_address}, {drive.city}, {drive.state} {drive.postal_code}
            </p>
            <p className="meta">
              {drive.title} · {drive.organization.name}
            </p>
            {drive.capacity && !cancelled && <p className="meta">Room for about {drive.capacity} donors</p>}
            {drive.description && <p className="description">{drive.description}</p>}
          </>
        )}
        <div className="actions">
          {cancelled && <span className="tag solid">Cancelled</span>}
          {registerUrl && (
            <a className="register" href={registerUrl} target="_blank" rel="noopener noreferrer">
              Register
              <ExternalIcon />
              <span className="sr-only"> on the organizer's site (opens in a new tab)</span>
            </a>
          )}
          {!cancelled && !registerUrl && <span className="meta">No sign-up link yet</span>}
          {drive.is_demo && <span className="tag">Demo</span>}
        </div>
      </div>
    </article>
  )
}

function ExternalIcon() {
  return (
    <svg aria-hidden="true" width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="2">
      <path d="M6 3H3v10h10v-3M9 2h5v5M14 2 7 9" />
    </svg>
  )
}
