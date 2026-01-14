from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from ..Database import SessionLocal, Base, get_db
from ..model import Account, Transaction
from .Auth import get_current_user

router = APIRouter(prefix="/api/account", tags=["Account"])



class AmountRequest(BaseModel):
    amount: int = Field(..., gt=0)

def get_my_account(db: Session, user_id: int) -> Account:
    account = db.query(Account).filter(Account.user_id == user_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found for this user")
    return account

@router.get("/me")
def read_my_account(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    user_id = int(current_user["id"])
    account = get_my_account(db, user_id)
    return {"account_id": account.id, "balance": account.balance}

@router.post("/deposit")
def deposit(
    req: AmountRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    user_id = int(current_user["id"])
    account = get_my_account(db, user_id)

    account.balance += req.amount

    tx = Transaction(
        account_id=account.id,
        type="deposit",
        amount=req.amount,
    )
    db.add(tx)
    db.commit()
    db.refresh(account)

    return {"account_id": account.id, "new_balance": account.balance}

@router.post("/withdraw")
def withdraw(
    req: AmountRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    user_id = int(current_user["id"])
    account = get_my_account(db, user_id)

    if account.balance < req.amount:
        raise HTTPException(status_code=400, detail="Insufficient funds")

    account.balance -= req.amount

    tx = Transaction(
        account_id=account.id,
        type="withdraw",
        amount=req.amount,
    )
    db.add(tx)
    db.commit()
    db.refresh(account)

    return {"account_id": account.id, "new_balance": account.balance}




