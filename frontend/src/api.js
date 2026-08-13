const BASE = '/api'

async function request(path, options = {}) {
  const resp = await fetch(`${BASE}${path}`, options)
  if (!resp.ok) throw new Error(`请求失败: ${resp.status}`)
  return resp.status === 204 ? null : resp.json()
}

export const listEntries = () => request('/entries')
export const createEntry = (content) =>
  request('/entries', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ content }),
  })
export const deleteEntry = (id) => request(`/entries/${id}`, { method: 'DELETE' })
export const listSummaries = () => request('/summaries')
export const generateSummary = (periodType) =>
  request(`/summaries/${periodType}`, { method: 'POST' })
