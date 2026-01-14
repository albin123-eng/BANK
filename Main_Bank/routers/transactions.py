from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..Database import SessionLocal, Base, get_db
from ..model import Account, Transaction
from .Auth import get_current_user

router = APIRouter(prefix="/transactions", tags=["Transactions"])



def my_account(db: Session, user_id: int) -> Account:
    account = db.query(Account).filter(Account.user_id == user_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    return account

@router.get("/me")
def my_transactions(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
):
    # if your get_current_user returns dict like {"id": "...", "role": "..."}
    user_id = int(current_user["id"])

    account = my_account(db, user_id)

    txs = (
        db.query(Transaction)
        .filter(Transaction.account_id == account.id)
        .order_by(Transaction.created_at.desc())
        .all()
    )

    return txs
