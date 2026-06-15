import re
from datetime import datetime
from typing import Optional

import pandas as pd

DATE_COLUMNS = ["date", "transaction date", "trans date", "posted date", "posting date", "txn date"]
DESC_COLUMNS = ["description", "memo", "narration", "details", "payee", "merchant", "name"]
AMOUNT_COLUMNS = ["amount", "debit", "credit", "value", "transaction amount", "amt"]
CATEGORY_COLUMNS = ["category", "type", "classification", "group"]
TYPE_COLUMNS = ["transaction type", "type", "dr/cr", "debit/credit"]

CATEGORY_KEYWORDS = {
    "Food & Dining": ["restaurant", "cafe", "coffee", "food", "grocery", "supermarket", "uber eats", "doordash", "swiggy", "zomato"],
    "Transportation": ["uber", "lyft", "fuel", "gas", "petrol", "metro", "taxi", "parking", "transit"],
    "Shopping": ["amazon", "walmart", "target", "flipkart", "myntra", "store", "shop", "mall"],
    "Bills & Utilities": ["electric", "water", "internet", "phone", "utility", "bill", "rent", "insurance"],
    "Entertainment": ["netflix", "spotify", "movie", "cinema", "game", "subscription", "youtube"],
    "Healthcare": ["pharmacy", "hospital", "doctor", "medical", "health", "clinic"],
    "Salary & Income": ["salary", "payroll", "income", "deposit", "refund", "interest"],
    "Transfer": ["transfer", "atm", "withdrawal", "payment to", "payment from"],
}


def _normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = [str(c).strip().lower() for c in df.columns]
    return df


def _find_column(columns: list[str], candidates: list[str]) -> Optional[str]:
    for candidate in candidates:
        if candidate in columns:
            return candidate
    for col in columns:
        for candidate in candidates:
            if candidate in col:
                return col
    return None


def _parse_date(value) -> Optional[datetime]:
    if pd.isna(value):
        return None
    if isinstance(value, datetime):
        return value
    try:
        return pd.to_datetime(value, dayfirst=False, errors="coerce").to_pydatetime()
    except Exception:
        return None


def _parse_amount(row: pd.Series, amount_col: Optional[str], columns: list[str]) -> Optional[float]:
    if amount_col and not pd.isna(row.get(amount_col)):
        val = row[amount_col]
        if isinstance(val, str):
            val = re.sub(r"[^\d.\-]", "", val)
        try:
            return float(val)
        except (TypeError, ValueError):
            pass

    debit_col = _find_column(columns, ["debit", "withdrawal", "dr"])
    credit_col = _find_column(columns, ["credit", "deposit", "cr"])

    debit = row.get(debit_col) if debit_col else None
    credit = row.get(credit_col) if credit_col else None

    try:
        if debit_col and not pd.isna(debit) and float(debit) != 0:
            return -abs(float(debit))
        if credit_col and not pd.isna(credit) and float(credit) != 0:
            return abs(float(credit))
    except (TypeError, ValueError):
        pass
    return None


def auto_categorize(description: str) -> str:
    desc_lower = description.lower()
    for category, keywords in CATEGORY_KEYWORDS.items():
        if any(kw in desc_lower for kw in keywords):
            return category
    return "Uncategorized"


def parse_finance_file(file_bytes: bytes, filename: str) -> tuple[list[dict], int]:
    """Parse CSV or XLSX file into transaction dicts. Returns (transactions, skipped_count)."""
    if filename.lower().endswith(".xlsx") or filename.lower().endswith(".xls"):
        df = pd.read_excel(file_bytes)
    else:
        df = pd.read_csv(file_bytes)

    if df.empty:
        return [], 0

    df = _normalize_columns(df)
    columns = list(df.columns)

    date_col = _find_column(columns, DATE_COLUMNS)
    desc_col = _find_column(columns, DESC_COLUMNS)
    amount_col = _find_column(columns, AMOUNT_COLUMNS)
    category_col = _find_column(columns, CATEGORY_COLUMNS)
    type_col = _find_column(columns, TYPE_COLUMNS)

    transactions = []
    skipped = 0

    for _, row in df.iterrows():
        parsed_date = _parse_date(row[date_col]) if date_col else None
        description = str(row[desc_col]).strip() if desc_col and not pd.isna(row.get(desc_col)) else ""
        amount = _parse_amount(row, amount_col, columns)

        if not parsed_date or not description or amount is None or amount == 0:
            skipped += 1
            continue

        category = "Uncategorized"
        if category_col and not pd.isna(row.get(category_col)):
            category = str(row[category_col]).strip()
        else:
            category = auto_categorize(description)

        transaction_type = "income" if amount > 0 else "expense"

        if type_col and not pd.isna(row.get(type_col)):
            type_val = str(row[type_col]).lower()
            if any(w in type_val for w in ["credit", "income", "deposit", "cr"]):
                transaction_type = "income"
                amount = abs(amount)
            elif any(w in type_val for w in ["debit", "expense", "withdrawal", "dr"]):
                transaction_type = "expense"
                amount = -abs(amount)

        transactions.append({
            "date": parsed_date.date(),
            "description": description[:500],
            "category": category[:100],
            "amount": amount,
            "transaction_type": transaction_type,
            "source_file": filename,
        })

    return transactions, skipped
