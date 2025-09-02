import uuid
from typing import Any, Self

from pydantic import model_validator

from api.schemas.settings import MyOrmModel


class CreateUser(MyOrmModel):
    """Схема для создания пользователя"""
    current_balance: int
    max_balance: int

    @model_validator(mode='after')
    def validate_prices(self) -> Self:
        if self.current_balance > self.max_balance:
            raise ValueError('Current balance should be less Max Balance')
        return self


class User(CreateUser):
    """Схема пользователя"""
    id: uuid.UUID
