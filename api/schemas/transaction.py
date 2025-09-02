import datetime
import uuid

from api.schemas.settings import MyOrmModel
from database import TransactionStatus

class CreateTransaction(MyOrmModel):
    """Схема для создания транзакции"""
    user_id: uuid.UUID
    amount: int
    status: TransactionStatus
    timeout_seconds: int

class Transaction(CreateTransaction):
    """Схема транзакции"""
    id: uuid.UUID
    status: TransactionStatus
    created_at: datetime.datetime
    updated_at: datetime.datetime
