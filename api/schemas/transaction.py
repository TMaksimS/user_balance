import datetime
import uuid
from typing import Self

from pydantic import model_validator

from api.schemas.settings import MyOrmModel
from database import TransactionStatus


class CreateTransaction(MyOrmModel):
    """Схема для создания транзакции"""

    user_id: uuid.UUID
    amount: int
    status: TransactionStatus
    timeout_seconds: int

    @model_validator(mode="after")
    def validate_prices(self) -> Self:
        if self.timeout_seconds <= 0:
            raise ValueError("Current timeout should be less 0")
        return self


class Transaction(CreateTransaction):
    """Схема транзакции"""

    id: uuid.UUID
    status: TransactionStatus
    created_at: datetime.datetime
    updated_at: datetime.datetime
