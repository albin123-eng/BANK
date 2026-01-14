from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from ..Database import SessionLocal, Base, get_db
from ..model import Account, Transfer, Transaction
from .Auth import get_current_user

router = APIRouter(prefix="/transfer", tags=["Transfer"])

# ----------- DB -------


# --------------Request model ------
class TransferRequest(BaseModel):
    to_account_id: int = Field(..., gt=0)
    amount: int = Field(..., gt=0)

# ---------------- Helper -----------
def get_my_account(db: Session, user_id: int) -> Account:
    account = db.query(Account).filter(Account.user_id == user_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    return account

# ------------- Transfer ----------
@router.post("")
def transfer_money(
    req: TransferRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    user_id = int(current_user["id"])

    from_account = get_my_account(db, user_id)

    if from_account.id == req.to_account_id:
        raise HTTPException(status_code=400, detail="Cannot transfer to same account")

    to_account = (
        db.query(Account)
        .filter(Account.id == req.to_account_id)
        .first()
    )

    if not to_account:
        raise HTTPException(status_code=404, detail="Recipient account not found")

    if from_account.balance < req.amount:
        raise HTTPException(status_code=400, detail="Insufficient funds")

    try:
        from_account.balance -= req.amount
        to_account.balance += req.amount


        transfer = Transfer(
            from_account_id=from_account.id,
            to_account_id=to_account.id,
            amount=req.amount,
            status="completed"
        )
        db.add(transfer)
        db.flush()

        db.add(Transaction(
            account_id=from_account.id,
            transfer_id=transfer.id,
            type="debit",
            amount=req.amount
        ))

        db.add(Transaction(
            account_id=to_account.id,
            transfer_id=transfer.id,
            type="credit",
            amount=req.amount
        ))

        db.commit()
        return {"message": "Transfer successful"}

    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="Transfer failed")





