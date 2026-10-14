import { describe, expect, it } from 'vitest'

import { formToDriveInput, localDateTime, saveErrorFrom } from './organizerDrives'

describe('localDateTime', () => {
  it("shows a UTC time as the drive's own clock, across daylight saving", () => {
    expect(localDateTime('2027-01-15T15:00:00Z', 'America/New_York')).toEqual({ date: '2027-01-15', time: '10:00' })
    expect(localDateTime('2027-07-15T14:00:00Z', 'America/New_York')).toEqual({ date: '2027-07-15', time: '10:00' })
  })

  it('uses the local date, which can differ from the UTC date', () => {
    // 2 AM UTC on the 16th is still the evening of the 15th in Los Angeles.
    expect(localDateTime('2027-01-16T02:00:00Z', 'America/Los_Angeles')).toEqual({ date: '2027-01-15', time: '18:00' })
  })

  it('writes midnight as 00, not 24', () => {
    expect(localDateTime('2027-01-15T05:00:00Z', 'America/New_York').time).toBe('00:00')
  })
})

describe('formToDriveInput', () => {
  const fields = {
    title: 'Drive',
    description: '  ',
    date: '2027-01-15',
    start_time: '10:00',
    end_time: '16:00',
    timezone: 'America/New_York',
    venue_name: 'Union',
    street_address: '100 Example Ave',
    city: 'State College',
    state: 'PA',
    postal_code: '16801',
    registration_url: '',
    capacity: '',
  }

  it('joins the date and times and turns blank optional fields into null', () => {
    expect(formToDriveInput(fields, 'draft')).toMatchObject({
      starts_at: '2027-01-15T10:00',
      ends_at: '2027-01-15T16:00',
      description: null,
      registration_url: null,
      capacity: null,
      status: 'draft',
    })
  })

  it('sends capacity as a number', () => {
    expect(formToDriveInput({ ...fields, capacity: '60' }, 'published').capacity).toBe(60)
  })
})

describe('saveErrorFrom', () => {
  it('gives friendly per-field messages and keeps whole-drive problems', () => {
    const error = saveErrorFrom([
      { loc: ['body', 'postal_code'], msg: "String should match pattern '^\\d{5}$'" },
      { loc: ['body'], msg: 'Value error, The drive must end after it starts' },
    ])

    expect(error.fields).toEqual({ postal_code: 'Use a 5-digit ZIP code.' })
    expect(error.message).toBe('The drive must end after it starts.')
  })
})
