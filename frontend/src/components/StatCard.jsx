export default function StatCard({ title, value, subtitle, variant = 'default', icon: Icon }) {
  return (
    <div className={`stat-card stat-card--${variant}`}>
      <div className="stat-card-header">
        <span className="stat-card-title">{title}</span>
        {Icon && <Icon size={20} className="stat-card-icon" />}
      </div>
      <div className="stat-card-value">{value}</div>
      {subtitle && <div className="stat-card-subtitle">{subtitle}</div>}
    </div>
  )
}
