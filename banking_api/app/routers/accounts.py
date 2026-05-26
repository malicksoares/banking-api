import random
import string
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models import User, Account, Transaction, TransactionType
from app.schemas import AccountCreate, AccountResponse, StatementResponse, TransactionResponse
from app.security import get_current_user

router = APIRouter()


def generate_account_number() -> str:
    return "".join(random.choices(string.digits, k=10))


@router.post(
    "/",
    response_model=AccountResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Criar conta corrente",
    description="Cria uma nova conta corrente para o usuário autenticado. Aceita depósito inicial opcional.",
)
async def create_account(
    payload: AccountCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Generate unique account number
    for _ in range(10):
        number = generate_account_number()
        existing = await db.execute(select(Account).where(Account.account_number == number))
        if not existing.scalar_one_or_none():
            break

    account = Account(
        account_number=number,
        balance=payload.initial_deposit,
        owner_id=current_user.id,
    )
    db.add(account)
    await db.flush()

    if payload.initial_deposit > 0:
        tx = Transaction(
            account_id=account.id,
            type=TransactionType.DEPOSIT,
            amount=payload.initial_deposit,
            balance_after=payload.initial_deposit,
            description="Depósito inicial",
        )
        db.add(tx)

    await db.refresh(account)
    return account


@router.get(
    "/",
    response_model=list[AccountResponse],
    summary="Listar contas do usuário",
    description="Retorna todas as contas correntes do usuário autenticado.",
)
async def list_accounts(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(Account).where(Account.owner_id == current_user.id))
    return result.scalars().all()


@router.get(
    "/{account_id}",
    response_model=AccountResponse,
    summary="Detalhe da conta",
    description="Retorna os dados de uma conta corrente específica.",
)
async def get_account(
    account_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Account).where(Account.id == account_id, Account.owner_id == current_user.id)
    )
    account = result.scalar_one_or_none()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    return account


@router.get(
    "/{account_id}/statement",
    response_model=StatementResponse,
    summary="Extrato da conta",
    description="Retorna o extrato completo com todas as transações da conta, ordenadas pela mais recente.",
)
async def get_statement(
    account_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Account).where(Account.id == account_id, Account.owner_id == current_user.id)
    )
    account = result.scalar_one_or_none()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    tx_result = await db.execute(
        select(Transaction)
        .where(Transaction.account_id == account_id)
        .order_by(Transaction.created_at.desc())
    )
    transactions = tx_result.scalars().all()

    return StatementResponse(
        account_number=account.account_number,
        current_balance=account.balance,
        transactions=[TransactionResponse.model_validate(t) for t in transactions],
    )
