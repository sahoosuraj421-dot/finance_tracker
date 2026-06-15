from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.transaction import AnalyticsSummary, BudgetCreate, BudgetResponse
from app.services.analytics import (
    check_budget_alerts,
    compare_months,
    detect_recurring_transactions,
    get_analytics_summary,
    get_spending_by_category,
)

router = APIRouter(prefix="/api/analytics", tags=["analytics"])


@router.get("/summary", response_model=AnalyticsSummary)
def analytics_summary(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: Session = Depends(get_db),
):
    return get_analytics_summary(db, start_date, end_date)


@router.get("/categories")
def category_breakdown(month: Optional[str] = None, db: Session = Depends(get_db)):
    return get_spending_by_category(db, month)


@router.get("/recurring")
def recurring_expenses(db: Session = Depends(get_db)):
    return detect_recurring_transactions(db)


@router.get("/compare")
def month_comparison(month1: str, month2: str, db: Session = Depends(get_db)):
    return compare_months(db, month1, month2)


@router.get("/budget-alerts")
def budget_alerts(db: Session = Depends(get_db)):
    return check_budget_alerts(db)


@router.get("/budgets", response_model=list[BudgetResponse])
def list_budgets(db: Session = Depends(get_db)):
    from app.models.transaction import Budget

    return db.query(Budget).all()


@router.post("/budgets", response_model=BudgetResponse, status_code=201)
def create_budget(payload: BudgetCreate, db: Session = Depends(get_db)):
    from app.models.transaction import Budget

    existing = db.query(Budget).filter(Budget.category == payload.category).first()
    if existing:
        existing.monthly_limit = payload.monthly_limit
        db.commit()
        db.refresh(existing)
        return existing

    budget = Budget(category=payload.category, monthly_limit=payload.monthly_limit)
    db.add(budget)
    db.commit()
    db.refresh(budget)
    return budget
