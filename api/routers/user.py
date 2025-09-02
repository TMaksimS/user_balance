"""user endpoints"""

import uuid

from fastapi import APIRouter
from fastapi.params import Depends
from sqlalchemy.ext.asyncio import AsyncSession

import database as db
from api import schemas
from api.routers.settings import verify_api_key, CustomExceptions
from src.config import LOGER

app = APIRouter(prefix="/users", tags=["USERS"])


@LOGER.catch
@app.post("/")
async def create(
        body: schemas.CreateUser,
        session: AsyncSession = Depends(db.get_db),
        api_key: str = Depends(verify_api_key)
):
    """Метод для создания пользователя"""
    if isinstance(api_key, CustomExceptions):
        raise api_key.value
    user = await db.User.create(session, **body.model_dump())
    user_dto = schemas.User.model_validate(user)
    return user_dto


@LOGER.catch
@app.get("/{user_id}", response_model=schemas.User)
async def get(
        user_id: uuid.UUID,
        session: AsyncSession = Depends(db.get_db),
        api_key: str = Depends(verify_api_key)
):
    """Метод для получения конкретного пользователя"""
    if isinstance(api_key, CustomExceptions):
        raise api_key.value
    user = await db.User.read_by_id(session, user_id)
    if user:
        user_dto = schemas.User.model_validate(user)
        return user_dto
    raise CustomExceptions.NOT_FOUND.value


@LOGER.catch
@app.delete("/{user_id}")
async def delete(
        user_id: uuid.UUID,
        session: AsyncSession = Depends(db.get_db),
        api_key: str = Depends(verify_api_key)
):
    """Метод для удаления пользователя"""
    if isinstance(api_key, CustomExceptions):
        raise api_key.value
    user = await db.User.delete(session, user_id)
    if user is True:
        return {"status": "OK"}
    return {"status": "Failed"}


@LOGER.catch
@app.patch("/{user_id}/current-balance", response_model=schemas.User)
async def update_current_balance(
        user_id: uuid.UUID,
        current_balance: int,
        session: AsyncSession = Depends(db.get_db),
        api_key: str = Depends(verify_api_key)
):
    """Метод для обновления данных пользователя"""
    if isinstance(api_key, CustomExceptions):
        raise api_key.value
    user = await db.User.read_by_id(session, user_id)
    user_dto = schemas.User.model_validate(user)
    if user is None:
        raise CustomExceptions.NOT_FOUND.value
    if current_balance > user_dto.max_balance:
        raise CustomExceptions.BAD_REQUEST.value
    user = await db.User.update(session, user_id, **{"current_balance": current_balance})
    user_dto = schemas.User.model_validate(user)
    return user_dto


@LOGER.catch
@app.patch("/{user_id}/max-balance", response_model=schemas.User)
async def update_max_balance(
        user_id: uuid.UUID,
        max_balance: int,
        session: AsyncSession = Depends(db.get_db),
        api_key: str = Depends(verify_api_key)
):
    """Метод для обновления данных пользователя"""
    if isinstance(api_key, CustomExceptions):
        raise api_key.value
    user = await db.User.read_by_id(session, user_id)
    user_dto = schemas.User.model_validate(user)
    if user is None:
        raise CustomExceptions.NOT_FOUND.value
    if max_balance < user_dto.current_balance:
        raise CustomExceptions.BAD_REQUEST.value
    user = await db.User.update(session, user_id, **{"max_balance": max_balance})
    user_dto = schemas.User.model_validate(user)
    return user_dto


@LOGER.catch
@app.get("/{user_id}/transactions")
async def transactions(
        user_id: uuid.UUID,
        limit: int,
        offset: int,
        session: AsyncSession = Depends(db.get_db),
        api_key: str = Depends(verify_api_key),
):
    """Метод для получения всех транзакций пользователя"""
    if isinstance(api_key, CustomExceptions):
        raise api_key.value
    result = await db.UoW(session).get_all_transactions_with_page(limit, offset, user_id)
    data = {
        "transactions": [schemas.Transaction.model_validate(i) for i in result[0]],
        "total": result[1]
    }
    return data
