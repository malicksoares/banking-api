from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, EmailStr, field_validator, ConfigDict
from app.models import TransactionType


# ── Auth ──────────────────────────────────────────────────────────────────────

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

    @field_validator("username")
    @classmethod
    def username_min_length(cls, v: str) -> str:
        if len(v) < 3:
            raise ValueError("Username must have at least 3 characters")
        return v

    @field_validator("password")
    @classmethod
    def password_min_length(cls, v: str) -> str:
        if len(v) < 6:
            raise ValueError("Password must have at least 6 characters")
        return v


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    email: str
    is_active: bool
    created_at: datetime


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    username: str | None = None


class LoginRequest(BaseModel):
    username: str
    password: str


# ── Accounts ──────────────────────────────────────────────────────────────────

class AccountCreate(BaseModel):
    initial_deposit: Decimal = Decimal("0.00")

    @field_validator("initial_deposit")
    @classmethod
    def non_negative(cls, v: Decimal) -> Decimal:
        if v < 0:
            raise ValueError("Initial deposit cannot be negative")
        return v


class AccountResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    account_number: str
    balance: Decimal
    owner_id: int
    created_at: datetime


# ── Transactions ──────────────────────────────────────────────────────────────

class TransactionCreate(BaseModel):
    amount: Decimal
    description: str | None = None

    @field_validator("amount")
    @classmethod
    def positive_amount(cls, v: Decimal) -> Decimal:
        if v <= 0:
            raise ValueError("Amount must be greater than zero")
        return v


class TransactionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    account_id: int
    type: TransactionType
    amount: Decimal
    balance_after: Decimal
    description: str | None
    created_at: datetime


class StatementResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    account_number: str
    current_balance: Decimal
    transactions: list[TransactionResponse]
