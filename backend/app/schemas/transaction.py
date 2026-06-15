from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, Field


class TransactionCreate(BaseModel):
    date: date
    description: str
    category: str = "Uncategorized"
    amount: float
    transaction_type: str = "expense"
    notes: Optional[str] = None


class TransactionResponse(BaseModel):
    id: int
    date: date
    description: str
    category: str
    amount: float
    transaction_type: str
    source_file: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class BudgetCreate(BaseModel):
    category: str
    monthly_limit: float = Field(gt=0)


class BudgetResponse(BaseModel):
    id: int
    category: str
    monthly_limit: float

    class Config:
        from_attributes = True


class UploadSummary(BaseModel):
    filename: str
    rows_imported: int
    rows_skipped: int
    categories_detected: list[str]


class AnalyticsSummary(BaseModel):
    total_income: float
    total_expenses: float
    net_balance: float
    transaction_count: int
    top_categories: list[dict]
    monthly_trend: list[dict]


class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None


class ChatResponse(BaseModel):
    reply: str
    session_id: str
    tool_calls: list[str] = []
