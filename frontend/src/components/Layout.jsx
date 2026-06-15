import { NavLink } from 'react-router-dom'
import {
  LayoutDashboard,
  ArrowLeftRight,
  Upload,
  BarChart3,
  Wallet,
  MessageCircle,
} from 'lucide-react'

const navItems = [
  { to: '/', icon: LayoutDashboard, label: 'Dashboard' },
  { to: '/transactions', icon: ArrowLeftRight, label: 'Transactions' },
  { to: '/upload', icon: Upload, label: 'Upload' },
  { to: '/analytics', icon: BarChart3, label: 'Analytics' },
  { to: '/budgets', icon: Wallet, label: 'Budgets' },
  { to: '/chat', icon: MessageCircle, label: 'AI Assistant' },
]

export default function Layout({ children }) {
  return (
    <div className="app-layout">
      <aside className="sidebar">
        <div className="sidebar-brand">
          <div className="brand-icon">$</div>
          <div>
            <h1>FinTrack</h1>
            <p>Finance Tracker</p>
          </div>
        </div>
        <nav className="sidebar-nav">
          {navItems.map(({ to, icon: Icon, label }) => (
            <NavLink
              key={to}
              to={to}
              end={to === '/'}
              className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
            >
              <Icon size={20} />
              <span>{label}</span>
            </NavLink>
          ))}
        </nav>
        <div className="sidebar-footer">
          <p>Powered by Gemini AI</p>
        </div>
      </aside>
      <main className="main-content">{children}</main>
    </div>
  )
}
