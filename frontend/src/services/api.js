const API_BASE = import.meta.env.VITE_API_URL || ''

async function request(path, options = {}) {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { 'Content-Type': 'application/json', ...options.headers },
    ...options,
  })
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }))
    throw new Error(err.detail || 'Request failed')
  }
  if (res.status === 204) return null
  return res.json()
}

export const api = {
  health: () => request('/api/health'),

  getTransactions: (params = {}) => {
    const qs = new URLSearchParams(params).toString()
    return request(`/api/transactions?${qs}`)
  },

  createTransaction: (data) =>
    request('/api/transactions', { method: 'POST', body: JSON.stringify(data) }),

  deleteTransaction: (id) =>
    request(`/api/transactions/${id}`, { method: 'DELETE' }),

  uploadFile: async (file) => {
    const form = new FormData()
    form.append('file', file)
    const res = await fetch(`${API_BASE}/api/transactions/upload`, {
      method: 'POST',
      body: form,
    })
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: res.statusText }))
      throw new Error(err.detail || 'Upload failed')
    }
    return res.json()
  },

  getCategories: () => request('/api/transactions/categories'),

  getSummary: (params = {}) => {
    const qs = new URLSearchParams(params).toString()
    return request(`/api/analytics/summary?${qs}`)
  },

  getCategoryBreakdown: (month) => {
    const qs = month ? `?month=${month}` : ''
    return request(`/api/analytics/categories${qs}`)
  },

  getRecurring: () => request('/api/analytics/recurring'),

  getBudgetAlerts: () => request('/api/analytics/budget-alerts'),

  getBudgets: () => request('/api/analytics/budgets'),

  createBudget: (data) =>
    request('/api/analytics/budgets', { method: 'POST', body: JSON.stringify(data) }),

  chat: (message, sessionId) =>
    request('/api/chat', {
      method: 'POST',
      body: JSON.stringify({ message, session_id: sessionId }),
    }),
}

export function formatCurrency(amount) {
  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    maximumFractionDigits: 2,
  }).format(Math.abs(amount))
}
