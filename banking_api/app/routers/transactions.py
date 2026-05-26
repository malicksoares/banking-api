from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models import User, Account, Transaction, TransactionType
from app.schemas import TransactionCreate, TransactionResponse
from app.security import get_current_user

router = APIRouter()


async def _get_account_for_user(account_id: int, user_id: int, db: AsyncSession) -> Account:
    result = await db.execute(
        select(Account).where(Account.id == account_id, Account.owner_id == user_id)
    )
    account = result.scalar_one_or_none()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    return account


@router.post(
    "/{account_id}/deposit",
    response_model=TransactionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Realizar depósito",
    description="Deposita um valor na conta informada. O valor deve ser positivo.",
)
async def deposit(
    account_id: int,
    payload: TransactionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    account = await _get_account_for_user(account_id, current_user.id, db)

    account.balance += payload.amount

    tx = Transaction(
        account_id=account.id,
        type=TransactionType.DEPOSIT,
        amount=payload.amount,
        balance_after=account.balance,
        description=payload.description or "Depósito",
    )
    db.add(tx)
    await db.flush()
    await db.refresh(tx)
    return tx


@router.post(
    "/{account_id}/withdraw",
    response_model=TransactionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Realizar saque",
    description="Saca um valor da conta informada. O valor deve ser positivo e não pode exceder o saldo disponível.",
)
async def withdraw(
    account_id: int,
    payload: TransactionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    account = await _get_account_for_user(account_id, current_user.id, db)

    if account.balance < payload.amount:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Insufficient funds. Available balance: {account.balance}",
        )

    account.balance -= payload.amount

    tx = Transaction(
        account_id=account.id,
        type=TransactionType.WITHDRAWAL,
        amount=payload.amount,
        balance_after=account.balance,
        description=payload.description or "Saque",
    )
    db.add(tx)
    await db.flush()
    await db.refresh(tx)
    return tx


@router.get(
    "/{account_id}",
    response_model=list[TransactionResponse],
    summary="Listar transações",
    description="Retorna todas as transações de uma conta, da mais recente para a mais antiga.",
)
async def list_transactions(
    account_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    await _get_account_for_user(account_id, current_user.id, db)

    result = await db.execute(
        select(Transaction)
        .where(Transaction.account_id == account_id)
        .order_by(Transaction.created_at.desc())
    )
    return result.scalars().all()
