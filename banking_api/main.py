from fastapi import FastAPI
from app.routers import auth, accounts, transactions
from app.database import create_tables

app = FastAPI(
    title="Banking API",
    description="""
## API Bancária Assíncrona

API RESTful para gerenciamento de operações bancárias com autenticação JWT.

### Funcionalidades
- 🔐 **Autenticação** com JWT (Bearer Token)
- 🏦 **Contas correntes** — criação e listagem
- 💰 **Depósitos e saques** — com validação de saldo
- 📄 **Extrato** — histórico completo de transações

### Como usar
1. `POST /auth/register` — crie seu usuário
2. `POST /auth/login` — obtenha o JWT
3. Clique em **Authorize** e cole o token
4. `POST /accounts/` — crie uma conta corrente
5. Use os endpoints de transações e extrato
    """,
    version="1.0.0",
)


@app.on_event("startup")
async def startup():
    await create_tables()


app.include_router(auth.router, prefix="/auth", tags=["Autenticação"])
app.include_router(accounts.router, prefix="/accounts", tags=["Contas"])
app.include_router(transactions.router, prefix="/transactions", tags=["Transações"])


@app.get("/", tags=["Health"])
async def root():
    return {"message": "Banking API is running", "version": "1.0.0", "docs": "/docs"}
