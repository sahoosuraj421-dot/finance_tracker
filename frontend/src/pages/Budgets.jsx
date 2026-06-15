import { useEffect, useState } from 'react'
import { Plus, AlertTriangle, CheckCircle } from 'lucide-react'
import { api, formatCurrency } from '../services/api'

export default function Budgets() {
  const [alerts, setAlerts] = useState([])
  const [showForm, setShowForm] = useState(false)
  const [form, setForm] = useState({ category: '', monthly_limit: '' })
  const [loading, setLoading] = useState(true)

  const load = () => {
    api.getBudgetAlerts()
      .then(setAlerts)
      .catch(console.error)
      .finally(() => setLoading(false))
  }

  useEffect(() => { load() }, [])

  const handleSubmit = async (e) => {
    e.preventDefault()
    try {
      await api.createBudget({ category: form.category, monthly_limit: parseFloat(form.monthly_limit) })
      setShowForm(false)
      setForm({ category: '', monthly_limit: '' })
      load()
    } catch (err) {
      alert(err.message)
    }
  }

  const statusIcon = (status) => {
    if (status === 'exceeded' || status === 'warning') return <AlertTriangle size={18} className="text-expense" />
    return <CheckCircle size={18} className="text-income" />
  }

  return (
    <div className="page">
      <header className="page-header row">
        <div>
          <h2>Budgets</h2>
          <p>Set monthly spending limits and track progress</p>
        </div>
        <button className="btn btn-primary" onClick={() => setShowForm(!showForm)}>
          <Plus size={18} /> Add Budget
        </button>
      </header>

      {showForm && (
        <form className="card form-card" onSubmit={handleSubmit}>
          <div className="form-grid">
            <label>
              Category
              <input type="text" value={form.category} onChange={(e) => setForm({ ...form, category: e.target.value })} required placeholder="e.g. Food & Dining" />
            </label>
            <label>
              Monthly Limit ($)
              <input type="number" step="0.01" min="1" value={form.monthly_limit} onChange={(e) => setForm({ ...form, monthly_limit: e.target.value })} required />
            </label>
          </div>
          <div className="form-actions">
            <button type="button" className="btn btn-ghost" onClick={() => setShowForm(false)}>Cancel</button>
            <button type="submit" className="btn btn-primary">Save Budget</button>
          </div>
        </form>
      )}

      {loading ? (
        <p className="page-loading">Loading budgets...</p>
      ) : alerts.length === 0 ? (
        <div className="card page-empty">
          <p>No budgets set yet. Create one to start tracking your spending limits.</p>
        </div>
      ) : (
        <div className="budget-grid">
          {alerts.map((a) => (
            <div key={a.category} className={`budget-card budget-${a.status}`}>
              <div className="budget-header">
                {statusIcon(a.status)}
                <h3>{a.category}</h3>
              </div>
              <div className="budget-amounts">
                <span className="spent">{formatCurrency(a.spent)}</span>
                <span className="limit">/ {formatCurrency(a.monthly_limit)}</span>
              </div>
              <div className="progress-bar">
                <div
                  className="progress-fill"
                  style={{ width: `${Math.min(a.percentage_used, 100)}%` }}
                />
              </div>
              <div className="budget-meta">
                <span>{a.percentage_used}% used</span>
                <span>{formatCurrency(a.remaining)} remaining</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
