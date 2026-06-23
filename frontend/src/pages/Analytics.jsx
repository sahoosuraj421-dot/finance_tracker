import { useEffect, useState } from 'react'
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  LineChart, Line, Legend,
} from 'recharts'
import { api, formatCurrency } from '../services/api'

export default function Analytics() {
  const [summary, setSummary] = useState(null)
  const [categories, setCategories] = useState([])
  const [recurring, setRecurring] = useState([])
  const [month, setMonth] = useState('')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    Promise.all([api.getSummary(), api.getCategoryBreakdown(month || undefined), api.getRecurring()])
      .then(([s, c, r]) => {
        setSummary(s)
        setCategories(c)
        setRecurring(r)
      })
      .catch(console.error)
      .finally(() => setLoading(false))
  }, [month])

  if (loading) return <div className="page-loading">Loading analytics...</div>

  const months = summary?.monthly_trend?.map((m) => m.month) || []

  return (
    <div className="page">
      <header className="page-header row">
        <div>
          <h2>Analytics</h2>
          <p>Deep dive into your spending patterns</p>
        </div>
        <select value={month} onChange={(e) => setMonth(e.target.value)} className="month-select">
          <option value="">All Time</option>
          {months.map((m) => <option key={m} value={m}>{m}</option>)}
        </select>
      </header>

      <div className="chart-grid">
        <div className="card">
          <h3>Category Breakdown</h3>
          {categories.length > 0 ? (
            <ResponsiveContainer width="100%" height={320}>
              <BarChart data={categories} layout="vertical">
                <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                <XAxis type="number" tick={{ fontSize: 12 }} tickFormatter={(v) => formatCurrency(v)} />
                <YAxis dataKey="category" type="category" width={120} tick={{ fontSize: 11 }} />
                <Tooltip formatter={(v) => formatCurrency(v)} />
                <Bar dataKey="total" fill="#6366f1" radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <p className="empty-text">No data for selected period</p>
          )}
        </div>

        <div className="card">
          <h3>Net Balance Trend</h3>
          {summary?.monthly_trend?.length > 0 ? (
            <ResponsiveContainer width="100%" height={320}>
              <LineChart data={summary.monthly_trend}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                <XAxis dataKey="month" tick={{ fontSize: 12 }} />
                <YAxis tick={{ fontSize: 12 }} tickFormatter={(v) => formatCurrency(v)} />
                <Tooltip formatter={(v) => formatCurrency(v)} />
                <Legend />
                <Line type="monotone" dataKey="net" stroke="#6366f1" strokeWidth={2} name="Net Balance" dot={{ r: 4 }} />
                <Line type="monotone" dataKey="income" stroke="#10b981" strokeWidth={2} name="Income" />
                <Line type="monotone" dataKey="expenses" stroke="#ef4444" strokeWidth={2} name="Expenses" />
              </LineChart>
            </ResponsiveContainer>
          ) : (
            <p className="empty-text">No trend data available</p>
          )}
        </div>
      </div>

      {recurring.length > 0 && (
        <div className="card">
          <h3>Detected Recurring Expenses</h3>
          <p className="card-subtitle">Subscriptions and bills that repeat regularly</p>
          <div className="recurring-grid">
            {recurring.map((r, i) => (
              <div key={i} className="recurring-item">
                <div className="recurring-name">{r.description}</div>
                <div className="recurring-meta">
                  <span className="badge">{r.category}</span>
                  <span>{formatCurrency(r.average_amount)}/mo</span>
                  <span className="text-muted">{r.occurrences} times</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
