// Mirrors Me in backend/app/schemas.py.
export type Me = {
  id: number
  name: string
  email: string
  organizations: { id: number; name: string; status: 'pending' | 'approved'; role: 'owner' }[]
}

export type SignupForm = { name: string; email: string; password: string; organization_name: string }

const TRY_AGAIN = 'Something went wrong. Please try again.'

// The session cookie is HttpOnly, so JavaScript never sees it; the browser sends it on its own.
function post(path: string, body?: object): Promise<Response> {
  const init: RequestInit = body
    ? { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) }
    : { method: 'POST' }
  return fetch(path, init).catch(() => {
    throw new Error("Couldn't reach BloodDrive. Check your connection and try again.")
  })
}

export async function signup(form: SignupForm): Promise<Me> {
  const response = await post('/api/auth/signup', form)
  if (response.status === 409) throw new Error('An account with this email already exists.')
  if (response.status === 422) throw new Error('Check the form: use a valid email and a password of 8 to 128 characters.')
  if (!response.ok) throw new Error(TRY_AGAIN)
  return response.json()
}

export async function login(email: string, password: string): Promise<Me> {
  const response = await post('/api/auth/login', { email, password })
  if (response.status === 401) throw new Error('Invalid email or password.')
  if (response.status === 422) throw new Error('Enter a valid email address.')
  if (!response.ok) throw new Error(TRY_AGAIN)
  return response.json()
}

export async function logout(): Promise<void> {
  const response = await post('/api/auth/logout')
  if (!response.ok) throw new Error(TRY_AGAIN)
}

/** The signed-in user, or null when nobody is signed in. */
export async function fetchMe(): Promise<Me | null> {
  const response = await fetch('/api/auth/me').catch(() => {
    throw new Error("Couldn't reach BloodDrive. Check your connection and try again.")
  })
  if (response.status === 401) return null
  if (!response.ok) throw new Error(TRY_AGAIN)
  return response.json()
}
