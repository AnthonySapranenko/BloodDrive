import { useEffect, useState, type FormEvent, type ReactNode } from 'react'
import { Link, Navigate, useNavigate } from 'react-router'

import { fetchMe, login, logout, signup, type Me, type SignupForm } from './auth'
import { formatWhen, type Drive } from './drives'
import { NotSignedInError, listOwnDrives } from './organizerDrives'

export function OrganizerLayout({ title, children }: { title: string; children: ReactNode }) {
  return (
    <>
      <header className="masthead">
        <div className="wrap topbar">
          <Link className="wordmark" to="/">
            BloodDrive
          </Link>
          <span className="nav">For organizers</span>
        </div>
      </header>
      <main className="wrap">
        <h1 className="page-title">{title}</h1>
        {children}
      </main>
    </>
  )
}

/** Submits a form's fields, shows any error, and goes to the organizer page on success. */
function useAuthForm(send: (fields: Record<string, string>) => Promise<Me>) {
  const navigate = useNavigate()
  const [error, setError] = useState<string | null>(null)
  const [busy, setBusy] = useState(false)

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setBusy(true)
    setError(null)
    try {
      await send(Object.fromEntries(new FormData(event.currentTarget)) as Record<string, string>)
      navigate('/organizer')
    } catch (err) {
      setError((err as Error).message)
      setBusy(false)
    }
  }

  return { error, busy, onSubmit }
}

export function FormError({ message }: { message: string | null }) {
  return message ? (
    <p className="form-message" role="alert">
      {message}
    </p>
  ) : null
}

export function SignupPage() {
  const { error, busy, onSubmit } = useAuthForm((fields) => signup(fields as SignupForm))

  return (
    <OrganizerLayout title="Create an organizer account">
      <form className="form" onSubmit={onSubmit}>
        <label>
          Your name
          <input name="name" required maxLength={200} autoComplete="name" />
        </label>
        <label>
          Email
          <input name="email" type="email" required maxLength={320} autoComplete="email" />
        </label>
        <label>
          Password
          <input
            name="password"
            type="password"
            required
            minLength={8}
            maxLength={128}
            autoComplete="new-password"
            aria-describedby="password-hint"
          />
          <span id="password-hint" className="hint">
            At least 8 characters.
          </span>
        </label>
        <label>
          Organization name
          <input name="organization_name" required maxLength={200} autoComplete="organization" />
          <span className="hint">The club, church or group running your drives.</span>
        </label>
        <FormError message={error} />
        <button type="submit" className="button" disabled={busy}>
          {busy ? 'Creating account…' : 'Create account'}
        </button>
      </form>
      <p className="form-footer">
        Already have an account? <Link to="/login">Sign in</Link>
      </p>
    </OrganizerLayout>
  )
}

export function LoginPage() {
  const { error, busy, onSubmit } = useAuthForm((fields) => login(fields.email, fields.password))

  return (
    <OrganizerLayout title="Organizer sign in">
      <form className="form" onSubmit={onSubmit}>
        <label>
          Email
          <input name="email" type="email" required maxLength={320} autoComplete="email" />
        </label>
        <label>
          Password
          <input name="password" type="password" required maxLength={128} autoComplete="current-password" />
        </label>
        <FormError message={error} />
        <button type="submit" className="button" disabled={busy}>
          {busy ? 'Signing in…' : 'Sign in'}
        </button>
      </form>
      <p className="form-footer">
        New organizer? <Link to="/signup">Create an account</Link>
      </p>
    </OrganizerLayout>
  )
}

export function OrganizerHome() {
  const navigate = useNavigate()
  // undefined while loading; null means nobody is signed in.
  const [me, setMe] = useState<Me | null | undefined>(undefined)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    fetchMe()
      .then(setMe)
      .catch((err: Error) => setError(err.message))
  }, [])

  async function signOut() {
    try {
      await logout()
      navigate('/login')
    } catch (err) {
      setError((err as Error).message)
    }
  }

  if (me === null) return <Navigate to="/login" replace />

  return (
    <OrganizerLayout title="Your organization">
      <FormError message={error} />
      {me === undefined && !error && <p className="status">Loading…</p>}
      {me && (
        <>
          <p className="meta">Signed in as {me.name} ({me.email})</p>
          {me.organizations.map((org) => (
            <section key={org.id} className="org">
              <h2 className="org-name">{org.name}</h2>
              {org.status === 'pending' ? (
                <p className="form-message">
                  <span className="tag">Pending approval</span> We review new organizations before their drives
                  appear in the public directory. Until then, nothing you publish is shown to donors.
                </p>
              ) : (
                <p className="meta">
                  <span className="tag">Approved</span> Your published drives appear in the public directory.
                </p>
              )}
              <OrgDrives orgId={org.id} />
            </section>
          ))}
          <button type="button" className="text-button" onClick={signOut}>
            Sign out
          </button>
        </>
      )}
    </OrganizerLayout>
  )
}

function OrgDrives({ orgId }: { orgId: number }) {
  const navigate = useNavigate()
  const [drives, setDrives] = useState<Drive[] | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    listOwnDrives(orgId)
      .then(setDrives)
      .catch((err: Error) => (err instanceof NotSignedInError ? navigate('/login') : setError(err.message)))
  }, [orgId, navigate])

  return (
    <>
      <FormError message={error} />
      {drives?.length === 0 && <p className="meta">No drives yet.</p>}
      {drives && drives.length > 0 && (
        <ul className="own-drives">
          {drives.map((drive) => {
            const { date, time } = formatWhen(drive)
            return (
              <li key={drive.id}>
                <Link to={`/organizer/orgs/${orgId}/drives/${drive.id}`}>{drive.title}</Link>
                <span className="meta">
                  {date} · {time} · {drive.venue_name}
                </span>
                <span className={`tag${drive.status === 'cancelled' ? ' solid' : ''}`}>{drive.status}</span>
              </li>
            )
          })}
        </ul>
      )}
      <Link className="button" to={`/organizer/orgs/${orgId}/drives/new`}>
        New drive
      </Link>
    </>
  )
}
