from datetime import date, timedelta
from typing import Optional

from sqlalchemy import case, func
from sqlalchemy.orm import Session

from app.models.transaction import Budget, Transaction


def get_analytics_summary(db: Session, start_date: Optional[date] = None, end_date: Optional[date] = None) -> dict:
    query = db.query(Transaction)
    if start_date:
        query = query.filter(Transaction.date >= start_date)
    if end_date:
        query = query.filter(Transaction.date <= end_date)

    transactions = query.all()
    income = sum(t.amount for t in transactions if t.transaction_type == "income")
    expenses = sum(abs(t.amount) for t in transactions if t.transaction_type == "expense")
    net = income - expenses

    category_totals: dict[str, float] = {}
    for t in transactions:
        if t.transaction_type == "expense":
            category_totals[t.category] = category_totals.get(t.category, 0) + abs(t.amount)

    top_categories = sorted(
        [{"category": k, "amount": round(v, 2)} for k, v in category_totals.items()],
        key=lambda x: x["amount"],
        reverse=True,
    )[:10]

    monthly = (
        db.query(
            func.strftime("%Y-%m", Transaction.date).label("month"),
            func.sum(
                case((Transaction.transaction_type == "income", Transaction.amount), else_=0)
            ).label("income"),
            func.sum(
                case((Transaction.transaction_type == "expense", func.abs(Transaction.amount)), else_=0)
            ).label("expenses"),
        )
        .group_by("month")
        .order_by("month")
        .all()
    )

    monthly_trend = [
        {
            "month": m.month,
            "income": round(float(m.income or 0), 2),
            "expenses": round(float(m.expenses or 0), 2),
            "net": round(float(m.income or 0) - float(m.expenses or 0), 2),
        }
        for m in monthly
    ]

    return {
        "total_income": round(income, 2),
        "total_expenses": round(expenses, 2),
        "net_balance": round(net, 2),
        "transaction_count": len(transactions),
        "top_categories": top_categories,
        "monthly_trend": monthly_trend,
    }


def get_spending_by_category(db: Session, month: Optional[str] = None) -> list[dict]:
    query = db.query(
        Transaction.category,
        func.sum(func.abs(Transaction.amount)).label("total"),
        func.count(Transaction.id).label("count"),
    ).filter(Transaction.transaction_type == "expense")

    if month:
        query = query.filter(func.strftime("%Y-%m", Transaction.date) == month)

    results = query.group_by(Transaction.category).order_by(func.sum(func.abs(Transaction.amount)).desc()).all()
    return [{"category": r.category, "total": round(float(r.total), 2), "count": r.count} for r in results]


def detect_recurring_transactions(db: Session, min_occurrences: int = 3) -> list[dict]:
    """Find transactions that appear to repeat monthly."""
    transactions = db.query(Transaction).filter(Transaction.transaction_type == "expense").all()

    groups: dict[str, list] = {}
    for t in transactions:
        key = t.description.lower().strip()[:50]
        groups.setdefault(key, []).append(t)

    recurring = []
    for desc_key, txns in groups.items():
        if len(txns) >= min_occurrences:
            amounts = [abs(t.amount) for t in txns]
            avg_amount = sum(amounts) / len(amounts)
            variance = max(amounts) - min(amounts)
            if variance / avg_amount < 0.15 if avg_amount else False:
                recurring.append({
                    "description": txns[0].description,
                    "category": txns[0].category,
                    "average_amount": round(avg_amount, 2),
                    "occurrences": len(txns),
                    "last_date": str(max(t.date for t in txns)),
                })

    return sorted(recurring, key=lambda x: x["average_amount"], reverse=True)


def compare_months(db: Session, month1: str, month2: str) -> dict:
    def month_stats(month: str):
        txns = db.query(Transaction).filter(func.strftime("%Y-%m", Transaction.date) == month).all()
        income = sum(t.amount for t in txns if t.transaction_type == "income")
        expenses = sum(abs(t.amount) for t in txns if t.transaction_type == "expense")
        return {"income": round(income, 2), "expenses": round(expenses, 2), "net": round(income - expenses, 2), "count": len(txns)}

    m1 = month_stats(month1)
    m2 = month_stats(month2)
    return {
        "month1": {"month": month1, **m1},
        "month2": {"month": month2, **m2},
        "expense_change": round(m2["expenses"] - m1["expenses"], 2),
        "income_change": round(m2["income"] - m1["income"], 2),
    }


def check_budget_alerts(db: Session) -> list[dict]:
    today = date.today()
    month_start = today.replace(day=1)
    budgets = db.query(Budget).all()
    alerts = []

    for budget in budgets:
        spent = (
            db.query(func.sum(func.abs(Transaction.amount)))
            .filter(
                Transaction.category == budget.category,
                Transaction.transaction_type == "expense",
                Transaction.date >= month_start,
            )
            .scalar()
            or 0
        )
        pct = (spent / budget.monthly_limit * 100) if budget.monthly_limit else 0
        status = "ok"
        if pct >= 100:
            status = "exceeded"
        elif pct >= 80:
            status = "warning"

        alerts.append({
            "category": budget.category,
            "monthly_limit": budget.monthly_limit,
            "spent": round(float(spent), 2),
            "remaining": round(budget.monthly_limit - float(spent), 2),
            "percentage_used": round(pct, 1),
            "status": status,
        })

    return alerts


def get_recent_transactions(db: Session, limit: int = 10) -> list[dict]:
    txns = db.query(Transaction).order_by(Transaction.date.desc()).limit(limit).all()
    return [
        {
            "id": t.id,
            "date": str(t.date),
            "description": t.description,
            "category": t.category,
            "amount": t.amount,
            "type": t.transaction_type,
        }
        for t in txns
    ]
