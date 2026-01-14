from datetime import datetime, timedelta, timezone
from typing import Annotated, Optional
from fastapi import Depends, APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from starlette import status
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import jwt, JWTError

from ..Database import  get_db
from ..model import User, Account

router = APIRouter(prefix="/auth", tags=["auth"])

SECRET_KEY = "PUT_THIS_IN_ENV_LATER"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 20

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth_bearer = OAuth2PasswordBearer(tokenUrl="auth/token")


class UserRequest(BaseModel):
    username: str
    email: EmailStr
    first_name: str
    last_name: str
    password: str



class Token(BaseModel):
    access_token: str
    token_type: str





db_dependency = Annotated[Session, Depends(get_db)]


def authenticate_user(username: str, password: str, db: Session) -> Optional[User]:
    user = db.query(User).filter(User.username == username).first()
    if not user:
        return None
    if not bcrypt_context.verify(password, user.hashed_password):
        return None
    return user


def create_access_token(username: str, user_id: str, role: str, expires_delta: timedelta) -> str:
    payload = {"sub": username, "id": user_id, "role": role}
    expire = datetime.now(timezone.utc) + expires_delta
    payload["exp"] = expire
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def get_current_user(token: Annotated[str, Depends(oauth_bearer)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        user_id: int = payload.get("id")
        user_role: str = payload.get("role")

        if username is None or user_id is None or user_role is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate user")

        return {"username": username, "id": user_id, "role": user_role}


    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate user")


@router.post("/register", status_code=status.HTTP_201_CREATED)
def create_user(db: db_dependency, req: UserRequest):

    if db.query(User).filter(User.username == req.username).first():
        raise HTTPException(status_code=400, detail="Username already taken")

    if db.query(User).filter(User.email == req.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")

    # 1) Create user
    user = User(
        email=req.email,
        username=req.username,
        first_name=req.first_name,
        last_name=req.last_name,
        hashed_password=bcrypt_context.hash(req.password),
        role="user",
        is_active=True
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    # 2) Auto-create default account for that user
    account = Account(
        user_id=user.id,
        balance=0
    )

    db.add(account)
    db.commit()
    db.refresh(account)

    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "account_id": account.id,
        "balance": account.balance,
    }




@router.post("/token", response_model=Token)
def login_for_access(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: db_dependency):
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate user")

    token = create_access_token(
        user.username,
        str(user.id),
        user.role,
        timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    return {"access_token": token, "token_type": "bearer"}
