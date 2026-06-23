import { useEffect, useState } from 'react'
import { Trash2, Plus } from 'lucide-react'
import { api, formatCurrency } from '../services/api'

export default function Transactions() {
  const [transactions, setTransactions] = useState([])
  const [filter, setFilter] = useState({ category: '', type: '' })
  const [showForm, setShowForm] = useState(false)
  const [form, setForm] = useState({
    date: new Date().toISOString().split('T')[0],
    description: '',
    category: 'Uncategorized',
    amount: '',
    transaction_type: 'expense',
  })
  const [loading, setLoading] = useState(true)

  const load = () => {
    const params = {}
    if (filter.category) params.category = filter.category
    if (filter.type) params.transaction_type = filter.type
    api.getTransactions(params)
      .then(setTransactions)
      .catch(console.error)
      .finally(() => setLoading(false))
  }

  useEffect(() => { load() }, [filter])

  const handleSubmit = async (e) => {
    e.preventDefault()
    try {
      await api.createTransaction({ ...form, amount: parseFloat(form.amount) })
      setShowForm(false)
      setForm({ date: new Date().toISOString().split('T')[0], description: '', category: 'Uncategorized', amount: '', transaction_type: 'expense' })
      load()
    } catch (err) {
      alert(err.message)
    }
  }

  const handleDelete = async (id) => {
    if (!confirm('Delete this transaction?')) return
    await api.deleteTransaction(id)
    load()
  }

  return (
    <div className="page">
      <header className="page-header row">
        <div>
          <h2>Transactions</h2>
          <p>View and manage all your financial records</p>
        </div>
        <button className="btn btn-primary" onClick={() => setShowForm(!showForm)}>
          <Plus size={18} /> Add Transaction
        </button>
      </header>

      {showForm && (
        <form className="card form-card" onSubmit={handleSubmit}>
          <div className="form-grid">
            <label>
              Date
              <input type="date" value={form.date} onChange={(e) => setForm({ ...form, date: e.target.value })} required />
            </label>
            <label>
              Type
              <select value={form.transaction_type} onChange={(e) => setForm({ ...form, transaction_type: e.target.value })}>
                <option value="expense">Expense</option>
                <option value="income">Income</option>
              </select>
            </label>
            <label className="span-2">
              Description
              <input type="text" value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} required placeholder="e.g. Grocery shopping" />
            </label>
            <label>
              Category
              <input type="text" value={form.category} onChange={(e) => setForm({ ...form, category: e.target.value })} />
            </label>
            <label>
              Amount (₹)
              <input type="number" step="0.01" min="0" value={form.amount} onChange={(e) => setForm({ ...form, amount: e.target.value })} required />
            </label>
          </div>
          <div className="form-actions">
            <button type="button" className="btn btn-ghost" onClick={() => setShowForm(false)}>Cancel</button>
            <button type="submit" className="btn btn-primary">Save</button>
          </div>
        </form>
      )}

      <div className="filters">
        <select value={filter.type} onChange={(e) => setFilter({ ...filter, type: e.target.value })}>
          <option value="">All Types</option>
          <option value="expense">Expenses</option>
          <option value="income">Income</option>
        </select>
        <input
          type="text"
          placeholder="Filter by category..."
          value={filter.category}
          onChange={(e) => setFilter({ ...filter, category: e.target.value })}
        />
      </div>

      <div className="card">
        {loading ? (
          <p className="page-loading">Loading...</p>
        ) : transactions.length === 0 ? (
          <p className="empty-text">No transactions found.</p>
        ) : (
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Date</th>
                  <th>Description</th>
                  <th>Category</th>
                  <th>Type</th>
                  <th>Amount</th>
                  <th></th>
                </tr>
              </thead>
              <tbody>
                {transactions.map((t) => (
                  <tr key={t.id}>
                    <td>{t.date}</td>
                    <td>{t.description}</td>
                    <td><span className="badge">{t.category}</span></td>
                    <td><span className={`type-badge type-${t.transaction_type}`}>{t.transaction_type}</span></td>
                    <td className={t.transaction_type === 'income' ? 'text-income' : 'text-expense'}>
                      {t.transaction_type === 'income' ? '+' : '-'}{formatCurrency(t.amount)}
                    </td>
                    <td>
                      <button className="btn-icon" onClick={() => handleDelete(t.id)} title="Delete">
                        <Trash2 size={16} />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  )
}
