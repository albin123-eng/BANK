from starlette.responses import HTMLResponse

from .Database import engine, Base
from .routers import Auth, accounts, transactions, transfers, admin
from pathlib import Path
from fastapi import FastAPI, Request, status
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from . import model
from fastapi.templating import Jinja2Templates


app = FastAPI()

Base.metadata.create_all(bind=engine)

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

@app.get("/")
def home(request: Request):
    return templates.TemplateResponse(
    request=request,
    name="home.html",
    context={}
)
@app.get("/login")
def login_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="login.html",
        context={}
    )

@app.get("/register")
def register_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="register.html",
        context={}
    )

@app.get("/deposit")
def deposit_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="deposit.html",
        context={}
    )

@app.get("/withdraw")
def withdraw_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="withdraw.html",
        context={}
    )

@app.get("/transfer")
def transfer_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="transfer.html",
        context={}
    )

@app.get("/transactions")
def transactions_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="transactions.html",
        context={}
    )

@app.get("/account", response_class=HTMLResponse)
def account_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="account.html",
        context={}
    )
app.include_router(Auth.router)
app.include_router(accounts.router)
app.include_router(transfers.router)
app.include_router(transactions.router)
app.include_router(admin.router)