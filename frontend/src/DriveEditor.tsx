import { useEffect, useState, type FormEvent, type ReactNode } from 'react'
import { Link, useNavigate, useParams } from 'react-router'

import type { Drive } from './drives'
import { FormError, OrganizerLayout } from './OrganizerPages'
import {
  NotSignedInError,
  SaveError,
  US_TIMEZONES,
  deleteDrive,
  formToDriveInput,
  getOwnDrive,
  localDateTime,
  saveDrive,
} from './organizerDrives'

/** Create (no :driveId) or edit one of the organization's drives. */
export function DriveEditor() {
  const params = useParams()
  const orgId = Number(params.orgId)
  const driveId = params.driveId ? Number(params.driveId) : undefined
  const navigate = useNavigate()
  // undefined while an existing drive loads; null for a new drive.
  const [drive, setDrive] = useState<Drive | null | undefined>(driveId ? undefined : null)
  const [error, setError] = useState<SaveError | Error | null>(null)
  const [busy, setBusy] = useState(false)

  function fail(err: Error) {
    if (err instanceof NotSignedInError) navigate('/login')
    else setError(err)
  }

  useEffect(() => {
    if (!driveId) return
    getOwnDrive(orgId, driveId)
      .then(setDrive)
      .catch((err: Error) => (err instanceof NotSignedInError ? navigate('/login') : setError(err)))
  }, [orgId, driveId, navigate])

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    // Each submit button carries the status it saves with: draft, published or cancelled.
    const button = (event.nativeEvent as SubmitEvent).submitter as HTMLButtonElement
    const status = button.value as Drive['status']
    if (status === 'cancelled' && !window.confirm('Cancel this drive? Donors will see it marked Cancelled.')) return
    const fields = Object.fromEntries(new FormData(event.currentTarget)) as Record<string, string>
    setBusy(true)
    setError(null)
    try {
      await saveDrive(orgId, driveId, formToDriveInput(fields, status))
      navigate('/organizer')
    } catch (err) {
      fail(err as Error)
      setBusy(false)
    }
  }

  async function onDelete() {
    if (!driveId || !window.confirm('Delete this draft? This cannot be undone.')) return
    try {
      await deleteDrive(orgId, driveId)
      navigate('/organizer')
    } catch (err) {
      fail(err as Error)
    }
  }

  const title = driveId ? 'Edit drive' : 'New drive'
  if (drive === undefined) {
    return (
      <OrganizerLayout title={title}>
        {error ? <FormError message={error.message} /> : <p className="status">Loading…</p>}
      </OrganizerLayout>
    )
  }

  const fieldErrors = error instanceof SaveError ? error.fields : {}
  const local = drive && localDateTime(drive.starts_at, drive.timezone)
  const timezones = drive && !US_TIMEZONES.some(([zone]) => zone === drive.timezone)
    ? [...US_TIMEZONES, [drive.timezone, drive.timezone] as [string, string]]
    : US_TIMEZONES

  return (
    <OrganizerLayout title={title}>
      {drive && <p className="meta"><span className="tag">{drive.status}</span></p>}
      <form className="form drive-form" onSubmit={onSubmit}>
        <Field label="Title" name="title" errors={fieldErrors}>
          <input name="title" required maxLength={200} defaultValue={drive?.title} />
        </Field>
        <Field label="Date" name="starts_at" errors={fieldErrors}>
          <input name="date" type="date" required defaultValue={local?.date} />
        </Field>
        <div className="form-row">
          <Field label="Starts" name="starts_at" errors={{}}>
            <input name="start_time" type="time" required defaultValue={local?.time} />
          </Field>
          <Field label="Ends" name="ends_at" errors={fieldErrors}>
            <input
              name="end_time"
              type="time"
              required
              defaultValue={drive ? localDateTime(drive.ends_at, drive.timezone).time : undefined}
            />
          </Field>
        </div>
        <Field label="Time zone" name="timezone" errors={fieldErrors}>
          <select name="timezone" defaultValue={drive?.timezone ?? 'America/New_York'}>
            {timezones.map(([zone, label]) => (
              <option key={zone} value={zone}>
                {label}
              </option>
            ))}
          </select>
        </Field>
        <Field label="Venue" name="venue_name" errors={fieldErrors}>
          <input name="venue_name" required maxLength={200} defaultValue={drive?.venue_name} />
        </Field>
        <Field label="Street address" name="street_address" errors={fieldErrors}>
          <input name="street_address" required maxLength={200} autoComplete="street-address" defaultValue={drive?.street_address} />
        </Field>
        <div className="form-row">
          <Field label="City" name="city" errors={fieldErrors}>
            <input name="city" required maxLength={100} defaultValue={drive?.city} />
          </Field>
          <Field label="State" name="state" errors={fieldErrors}>
            <input name="state" required maxLength={2} pattern="[A-Za-z]{2}" title="Two-letter state code, like PA" defaultValue={drive?.state} />
          </Field>
          <Field label="ZIP" name="postal_code" errors={fieldErrors}>
            <input name="postal_code" required inputMode="numeric" maxLength={5} pattern="\d{5}" title="Five-digit ZIP code" defaultValue={drive?.postal_code} />
          </Field>
        </div>
        <Field label="Registration link (optional)" name="registration_url" errors={fieldErrors}
          hint="The official page where donors book an appointment.">
          <input name="registration_url" type="url" maxLength={2048} placeholder="https://" defaultValue={drive?.registration_url ?? ''} />
        </Field>
        <Field label="Capacity (optional)" name="capacity" errors={fieldErrors} hint="About how many donors you can take.">
          <input name="capacity" type="number" min={1} max={100000} step={1} defaultValue={drive?.capacity ?? ''} />
        </Field>
        <Field label="Description (optional)" name="description" errors={fieldErrors}>
          <textarea name="description" rows={4} maxLength={5000} defaultValue={drive?.description ?? ''} />
        </Field>

        {error && <FormError message={error.message} />}
        <div className="form-actions">
          {drive?.status === 'published' ? (
            <>
              <button type="submit" className="button" value="published" disabled={busy}>Save changes</button>
              <button type="submit" className="text-button" value="draft" disabled={busy}>Unpublish</button>
              <button type="submit" className="text-button" value="cancelled" disabled={busy}>Cancel drive</button>
            </>
          ) : drive?.status === 'cancelled' ? (
            <>
              <button type="submit" className="button" value="cancelled" disabled={busy}>Save changes</button>
              <button type="submit" className="text-button" value="published" disabled={busy}>Publish again</button>
            </>
          ) : (
            <>
              {/* Save draft comes first: pressing Enter uses the first submit button, so Enter never publishes. */}
              <button type="submit" className="text-button" value="draft" disabled={busy}>Save draft</button>
              <button type="submit" className="button" value="published" disabled={busy}>Publish</button>
              {drive && (
                <button type="button" className="text-button" onClick={onDelete} disabled={busy}>Delete draft</button>
              )}
            </>
          )}
        </div>
      </form>
      <p className="form-footer">
        <Link to="/organizer">Back to your drives</Link>
      </p>
    </OrganizerLayout>
  )
}

function Field({ label, name, errors, hint, children }: {
  label: string
  name: string
  errors: Record<string, string>
  hint?: string
  children: ReactNode
}) {
  return (
    <label>
      {label}
      {children}
      {hint && <span className="hint">{hint}</span>}
      {errors[name] && <span className="field-error" role="alert">{errors[name]}</span>}
    </label>
  )
}
