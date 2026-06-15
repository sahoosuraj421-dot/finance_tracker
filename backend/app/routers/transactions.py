from io import BytesIO
from typing import Optional

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.transaction import Transaction
from app.schemas.transaction import TransactionCreate, TransactionResponse, UploadSummary
from app.services.file_parser import parse_finance_file

router = APIRouter(prefix="/api/transactions", tags=["transactions"])


@router.get("", response_model=list[TransactionResponse])
def list_transactions(
    category: Optional[str] = None,
    transaction_type: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(get_db),
):
    query = db.query(Transaction).order_by(Transaction.date.desc())
    if category:
        query = query.filter(Transaction.category == category)
    if transaction_type:
        query = query.filter(Transaction.transaction_type == transaction_type)
    return query.offset(offset).limit(limit).all()


@router.post("", response_model=TransactionResponse, status_code=201)
def create_transaction(payload: TransactionCreate, db: Session = Depends(get_db)):
    amount = payload.amount if payload.transaction_type == "income" else -abs(payload.amount)
    txn = Transaction(
        date=payload.date,
        description=payload.description,
        category=payload.category,
        amount=amount,
        transaction_type=payload.transaction_type,
        notes=payload.notes,
    )
    db.add(txn)
    db.commit()
    db.refresh(txn)
    return txn


@router.delete("/{transaction_id}", status_code=204)
def delete_transaction(transaction_id: int, db: Session = Depends(get_db)):
    txn = db.query(Transaction).filter(Transaction.id == transaction_id).first()
    if not txn:
        raise HTTPException(status_code=404, detail="Transaction not found")
    db.delete(txn)
    db.commit()


@router.post("/upload", response_model=UploadSummary)
async def upload_file(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")

    allowed = (".csv", ".xlsx", ".xls")
    if not file.filename.lower().endswith(allowed):
        raise HTTPException(status_code=400, detail=f"File must be one of: {', '.join(allowed)}")

    content = await file.read()
    if len(content) > 10 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File too large (max 10MB)")

    try:
        file_buffer = BytesIO(content)
        transactions, skipped = parse_finance_file(file_buffer, file.filename)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to parse file: {str(e)}")

    if not transactions:
        raise HTTPException(status_code=400, detail="No valid transactions found in file")

    categories = set()
    for t in transactions:
        db.add(Transaction(**t))
        categories.add(t["category"])

    db.commit()

    return UploadSummary(
        filename=file.filename,
        rows_imported=len(transactions),
        rows_skipped=skipped,
        categories_detected=sorted(categories),
    )


@router.get("/categories")
def list_categories(db: Session = Depends(get_db)):
    from sqlalchemy import func

    results = (
        db.query(Transaction.category, func.count(Transaction.id))
        .group_by(Transaction.category)
        .order_by(func.count(Transaction.id).desc())
        .all()
    )
    return [{"category": r[0], "count": r[1]} for r in results]
