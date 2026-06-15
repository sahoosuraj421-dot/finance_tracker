"""LangGraph agent tools for finance automation."""

from datetime import date
from typing import Optional

from langchain_core.tools import tool
from sqlalchemy.orm import Session

from app.services.analytics import (
    check_budget_alerts,
    compare_months,
    detect_recurring_transactions,
    get_analytics_summary,
    get_recent_transactions,
    get_spending_by_category,
)
from app.models.transaction import Budget, Transaction


def create_finance_tools(db: Session):
    """Create LangChain tools bound to a database session."""

    @tool
    def get_financial_summary(start_date: Optional[str] = None, end_date: Optional[str] = None) -> str:
        """Get overall financial summary including income, expenses, net balance, and top spending categories.
        Dates should be in YYYY-MM-DD format."""
        sd = date.fromisoformat(start_date) if start_date else None
        ed = date.fromisoformat(end_date) if end_date else None
        summary = get_analytics_summary(db, sd, ed)
        top_cats = ", ".join(f"{c['category']} (${c['amount']:,.2f})" for c in summary["top_categories"][:5])
        return (
            f"Financial Summary:\n"
            f"- Total Income: ${summary['total_income']:,.2f}\n"
            f"- Total Expenses: ${summary['total_expenses']:,.2f}\n"
            f"- Net Balance: ${summary['net_balance']:,.2f}\n"
            f"- Transaction Count: {summary['transaction_count']}\n"
            f"- Top Categories: {top_cats}"
        )

    @tool
    def get_category_spending(month: Optional[str] = None) -> str:
        """Get spending breakdown by category. Optional month in YYYY-MM format."""
        data = get_spending_by_category(db, month)
        if not data:
            return "No expense data found for the specified period."
        lines = [f"- {d['category']}: ${d['total']:,.2f} ({d['count']} transactions)" for d in data]
        period = f" for {month}" if month else ""
        return f"Spending by category{period}:\n" + "\n".join(lines)

    @tool
    def find_recurring_expenses() -> str:
        """Detect recurring monthly expenses like subscriptions and bills."""
        recurring = detect_recurring_transactions(db)
        if not recurring:
            return "No recurring expenses detected."
        lines = [
            f"- {r['description']}: ~${r['average_amount']:,.2f}/month ({r['occurrences']} times, last: {r['last_date']})"
            for r in recurring[:10]
        ]
        return "Recurring expenses detected:\n" + "\n".join(lines)

    @tool
    def compare_two_months(month1: str, month2: str) -> str:
        """Compare finances between two months. Months in YYYY-MM format."""
        result = compare_months(db, month1, month2)
        m1, m2 = result["month1"], result["month2"]
        return (
            f"Month Comparison ({month1} vs {month2}):\n"
            f"{month1}: Income ${m1['income']:,.2f}, Expenses ${m1['expenses']:,.2f}, Net ${m1['net']:,.2f}\n"
            f"{month2}: Income ${m2['income']:,.2f}, Expenses ${m2['expenses']:,.2f}, Net ${m2['net']:,.2f}\n"
            f"Expense change: ${result['expense_change']:+,.2f}\n"
            f"Income change: ${result['income_change']:+,.2f}"
        )

    @tool
    def check_budgets() -> str:
        """Check all budget limits and alert on overspending."""
        alerts = check_budget_alerts(db)
        if not alerts:
            return "No budgets configured. Use the Budgets page to set monthly limits."
        lines = []
        for a in alerts:
            icon = "⚠️" if a["status"] == "warning" else "🚨" if a["status"] == "exceeded" else "✅"
            lines.append(
                f"{icon} {a['category']}: ${a['spent']:,.2f} / ${a['monthly_limit']:,.2f} "
                f"({a['percentage_used']}% used, ${a['remaining']:,.2f} remaining)"
            )
        return "Budget Status:\n" + "\n".join(lines)

    @tool
    def set_budget(category: str, monthly_limit: float) -> str:
        """Set or update a monthly budget limit for a category."""
        existing = db.query(Budget).filter(Budget.category == category).first()
        if existing:
            existing.monthly_limit = monthly_limit
        else:
            db.add(Budget(category=category, monthly_limit=monthly_limit))
        db.commit()
        return f"Budget set for '{category}': ${monthly_limit:,.2f}/month"

    @tool
    def get_recent_activity(limit: int = 5) -> str:
        """Get the most recent transactions."""
        txns = get_recent_transactions(db, limit)
        if not txns:
            return "No transactions found."
        lines = [
            f"- {t['date']}: {t['description']} | {t['category']} | ${abs(t['amount']):,.2f} ({t['type']})"
            for t in txns
        ]
        return "Recent transactions:\n" + "\n".join(lines)

    @tool
    def add_transaction(
        date_str: str,
        description: str,
        amount: float,
        category: str = "Uncategorized",
        transaction_type: str = "expense",
    ) -> str:
        """Add a new transaction. date_str in YYYY-MM-DD format. Use negative amount for expenses."""
        txn = Transaction(
            date=date.fromisoformat(date_str),
            description=description,
            category=category,
            amount=amount if transaction_type == "income" else -abs(amount),
            transaction_type=transaction_type,
        )
        db.add(txn)
        db.commit()
        return f"Added transaction: {description} | ${abs(amount):,.2f} | {category} on {date_str}"

    @tool
    def search_transactions(keyword: str, limit: int = 10) -> str:
        """Search transactions by description keyword."""
        txns = (
            db.query(Transaction)
            .filter(Transaction.description.ilike(f"%{keyword}%"))
            .order_by(Transaction.date.desc())
            .limit(limit)
            .all()
        )
        if not txns:
            return f"No transactions found matching '{keyword}'."
        lines = [
            f"- {t.date}: {t.description} | {t.category} | ${abs(t.amount):,.2f}"
            for t in txns
        ]
        return f"Transactions matching '{keyword}':\n" + "\n".join(lines)

    return [
        get_financial_summary,
        get_category_spending,
        find_recurring_expenses,
        compare_two_months,
        check_budgets,
        set_budget,
        get_recent_activity,
        add_transaction,
        search_transactions,
    ]
