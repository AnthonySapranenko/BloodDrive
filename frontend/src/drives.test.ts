import { describe, expect, it } from 'vitest'

import { buildLineup, formatWhen, safeExternalUrl, type Drive } from './drives'

const NOW = new Date('2026-10-11T12:00:00Z')

function drive(id: number, startsAt: string, status: Drive['status'] = 'published'): Drive {
  return {
    id,
    title: `[DEMO] Drive ${id}`,
    description: null,
    starts_at: startsAt,
    ends_at: new Date(new Date(startsAt).getTime() + 6 * 3600_000).toISOString(),
    timezone: 'America/New_York',
    venue_name: `Venue ${id}`,
    street_address: '100 Example Ave',
    city: 'State College',
    state: 'PA',
    postal_code: '16801',
    registration_url: null,
    capacity: null,
    status,
    is_demo: true,
    organization: { id: 1, name: 'Demo Org', website_url: null, contact_email: null, is_demo: true },
  }
}

describe('buildLineup', () => {
  it('headlines the soonest drive and tiers the rest by days away', () => {
    const lineup = buildLineup(
      [drive(1, '2026-10-13T14:00:00Z'), drive(2, '2026-10-15T14:00:00Z'), drive(3, '2026-10-20T14:00:00Z'), drive(4, '2026-11-20T14:00:00Z')],
      NOW,
    )

    expect(lineup.headliner?.id).toBe(1)
    expect(lineup.tiers.map((tier) => [tier.name, tier.drives.map((d) => d.id)])).toEqual([
      ['This week', [2]],
      ['Next week', [3]],
      ['Later', [4]],
    ])
  })

  it('never headlines a cancelled drive', () => {
    const lineup = buildLineup([drive(1, '2026-10-12T14:00:00Z', 'cancelled'), drive(2, '2026-10-14T14:00:00Z')], NOW)

    expect(lineup.headliner?.id).toBe(2)
    expect(lineup.tiers[0].drives.map((d) => d.id)).toEqual([1])
  })

  it('handles no drives', () => {
    expect(buildLineup([], NOW)).toEqual({ headliner: null, tiers: [] })
  })
})

describe('formatWhen', () => {
  it("shows the drive's own local time, not the viewer's", () => {
    // 14:00 UTC is 10:00 AM in New York during daylight saving time.
    expect(formatWhen(drive(1, '2026-10-13T14:00:00Z'))).toEqual({
      date: 'Tue, Oct 13',
      time: '10:00 AM – 4:00 PM EDT',
    })
  })
})

describe('safeExternalUrl', () => {
  it('allows http and https links only', () => {
    expect(safeExternalUrl('https://example.com/register')).toBe('https://example.com/register')
    expect(safeExternalUrl('javascript:alert(1)')).toBeNull()
    expect(safeExternalUrl('not a url')).toBeNull()
    expect(safeExternalUrl(null)).toBeNull()
  })
})
