import { afterEach, describe, expect, it, vi } from 'vitest'

import { fetchMe, login, signup } from './auth'

const ME = { id: 1, name: 'Ada', email: 'ada@example.com', organizations: [] }
const FORM = { name: 'Ada', email: 'ada@example.com', password: 'long enough', organization_name: 'Club' }

function respond(status: number, body: unknown = {}) {
  const fetchMock = vi.fn(async () => new Response(JSON.stringify(body), { status }))
  vi.stubGlobal('fetch', fetchMock)
  return fetchMock
}

afterEach(() => {
  vi.unstubAllGlobals()
})

describe('signup', () => {
  it('sends the form as JSON and returns the user', async () => {
    const fetchMock = respond(201, ME)

    expect(await signup(FORM)).toEqual(ME)
    // The backend only accepts JSON, which is part of its CSRF protection.
    expect(fetchMock).toHaveBeenCalledWith('/auth/signup', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(FORM),
    })
  })

  it('explains a taken email', async () => {
    respond(409)
    await expect(signup(FORM)).rejects.toThrow('An account with this email already exists.')
  })
})

describe('login', () => {
  it('gives one message for any wrong email or password', async () => {
    respond(401)
    await expect(login('ada@example.com', 'wrong')).rejects.toThrow('Invalid email or password.')
  })

  it('explains a network failure', async () => {
    vi.stubGlobal('fetch', vi.fn(async () => Promise.reject(new TypeError('Failed to fetch'))))
    await expect(login('ada@example.com', 'x')).rejects.toThrow("Couldn't reach BloodDrive.")
  })
})

describe('fetchMe', () => {
  it('returns null when nobody is signed in', async () => {
    respond(401)
    expect(await fetchMe()).toBeNull()
  })

  it('returns the signed-in user', async () => {
    respond(200, ME)
    expect(await fetchMe()).toEqual(ME)
  })

  it('throws on a server error instead of pretending nobody is signed in', async () => {
    respond(500)
    await expect(fetchMe()).rejects.toThrow('Something went wrong.')
  })
})
