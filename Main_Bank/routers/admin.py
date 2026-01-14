from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..Database import  get_db
from ..model import User, Account, Transaction
from .Auth import get_current_user

router = APIRouter(prefix="/admin", tags=["Admin"])



def get_admin(current_user):
    if current_user['role'] != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access only"
        )

@router.get("/see_All_transactions")
def read_all_transactions(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    get_admin(current_user)

    transaction = (db.query(Transaction).order_by(Transaction.created_at.desc()).all())

    return transaction


