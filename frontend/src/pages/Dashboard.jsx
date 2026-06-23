import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { TrendingUp, TrendingDown, DollarSign, Receipt, AlertTriangle } from 'lucide-react'
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, Legend,
} from 'recharts'
import StatCard from '../components/StatCard'
import { api, formatCurrency } from '../services/api'

const COLORS = ['#6366f1', '#8b5cf6', '#a78bfa', '#c4b5fd', '#818cf8', '#4f46e5', '#7c3aed', '#6d28d9']

export default function Dashboard() {
  const [summary, setSummary] = useState(null)
  const [budgetAlerts, setBudgetAlerts] = useState([])
  const [recurring, setRecurring] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    Promise.all([api.getSummary(), api.getBudgetAlerts(), api.getRecurring()])
      .then(([s, b, r]) => {
        setSummary(s)
        setBudgetAlerts(b.filter((a) => a.status !== 'ok'))
        setRecurring(r.slice(0, 5))
      })
      .catch(console.error)
      .finally(() => setLoading(false))
  }, [])

  if (loading) return <div className="page-loading">Loading dashboard...</div>
  if (!summary) return <div className="page-empty">No data yet. <Link to="/upload">Upload a file</Link> to get started.</div>

  const pieData = summary.top_categories.map((c) => ({ name: c.category, value: c.amount }))

  return (
    <div className="page">
      <header className="page-header">
        <h2>Dashboard</h2>
        <p>Your financial overview at a glance</p>
      </header>

      <div className="stat-grid">
        <StatCard title="Total Income" value={formatCurrency(summary.total_income)} variant="income" icon={TrendingUp} />
        <StatCard title="Total Expenses" value={formatCurrency(summary.total_expenses)} variant="expense" icon={TrendingDown} />
        <StatCard
          title="Net Balance"
          value={formatCurrency(summary.net_balance)}
          variant={summary.net_balance >= 0 ? 'income' : 'expense'}
          icon={DollarSign}
        />
        <StatCard title="Transactions" value={summary.transaction_count} subtitle="total records" icon={Receipt} />
      </div>

      {budgetAlerts.length > 0 && (
        <div className="alert-banner">
          <AlertTriangle size={18} />
          <span>{budgetAlerts.length} budget alert{budgetAlerts.length > 1 ? 's' : ''} — </span>
          <Link to="/budgets">View budgets</Link>
        </div>
      )}

      <div className="chart-grid">
        <div className="card">
          <h3>Monthly Trend</h3>
          <ResponsiveContainer width="100%" height={280}>
            <BarChart data={summary.monthly_trend}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
              <XAxis dataKey="month" tick={{ fontSize: 12 }} />
              <YAxis tick={{ fontSize: 12 }} tickFormatter={(v) => formatCurrency(v)} />
              <Tooltip formatter={(v) => formatCurrency(v)} />
              <Bar dataKey="income" fill="#10b981" name="Income" radius={[4, 4, 0, 0]} />
              <Bar dataKey="expenses" fill="#ef4444" name="Expenses" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="card">
          <h3>Spending by Category</h3>
          {pieData.length > 0 ? (
            <ResponsiveContainer width="100%" height={280}>
              <PieChart>
                <Pie data={pieData} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={90} label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}>
                  {pieData.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
                </Pie>
                <Tooltip formatter={(v) => formatCurrency(v)} />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          ) : (
            <p className="empty-text">No expense data</p>
          )}
        </div>
      </div>

      {recurring.length > 0 && (
        <div className="card">
          <h3>Recurring Expenses</h3>
          <div className="table-wrap">
            <table>
              <thead>
                <tr><th>Description</th><th>Category</th><th>Avg Amount</th><th>Occurrences</th></tr>
              </thead>
              <tbody>
                {recurring.map((r, i) => (
                  <tr key={i}>
                    <td>{r.description}</td>
                    <td><span className="badge">{r.category}</span></td>
                    <td>{formatCurrency(r.average_amount)}</td>
                    <td>{r.occurrences}x</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  )
}
