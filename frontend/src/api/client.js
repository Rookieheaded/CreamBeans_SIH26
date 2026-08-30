const API_URL = (import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000').replace(/\/$/, '')

export const getToken = () => localStorage.getItem('access_token')

async function request(path, options = {}) {
  const token = getToken()
  const headers = new Headers(options.headers || {})
  if (options.body && !(options.body instanceof FormData)) headers.set('Content-Type', 'application/json')
  if (token) headers.set('Authorization', `Bearer ${token}`)
  const response = await fetch(`${API_URL}${path}`, { ...options, headers })
  let data = null
  try { data = await response.json() } catch { data = null }
  if (!response.ok) {
    const error = new Error(formatApiError(data, response.status))
    error.status = response.status
    error.data = data
    throw error
  }
  return data
}

function formatApiError(data, status) {
  if (Array.isArray(data?.detail)) return data.detail.map(x => x.msg).join(', ')
  if (typeof data?.detail === 'string') return data.detail
  return `Request failed (${status})`
}

export const api = {
  baseUrl: API_URL,
  login: (email, password) => request('/auth/login', {method:'POST', body:JSON.stringify({email,password})}),
  health: () => request('/health'),
  getItems: ({type, status, limit=50, offset=0}={}) => {
    const q = new URLSearchParams()
    if (type) q.set('type', type)
    if (status) q.set('status', status)
    q.set('limit', String(limit)); q.set('offset', String(offset))
    return request(`/items?${q}`)
  },
  getItem: id => request(`/items/${encodeURIComponent(id)}`),
  reportLost: payload => request('/items/lost', {method:'POST', body:JSON.stringify(payload)}),
  reportFound: payload => request('/items/found', {method:'POST', body:JSON.stringify(payload)}),
  getMatches: id => request(`/items/${encodeURIComponent(id)}/matches`),
  updateStatus: (id,status) => request(`/items/${encodeURIComponent(id)}/status`, {method:'PATCH', body:JSON.stringify({status})}),
  createClaim: payload => request('/claims', {method:'POST', body:JSON.stringify(payload)}),
}
