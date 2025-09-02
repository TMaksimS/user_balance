"""transaction endponts"""

import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

import database as db
from api import schemas
from api.routers.settings import verify_api_key, CustomExceptions
from src.config import LOGER

app = APIRouter(prefix="/transaction", tags=["TRANSACTIONS"])


@LOGER.catch
@app.post("/", response_model=schemas.Transaction)
async def create(
    body: schemas.CreateTransaction,
    session: AsyncSession = Depends(db.get_db),
    api_key: str = Depends(verify_api_key),
):
    if isinstance(api_key, CustomExceptions):
        raise api_key.value
    new_transaction = await db.UoW(session).create_transaction(**body.model_dump())
    LOGER.warning(new_transaction)
    if new_transaction:
        transaction_dto = schemas.Transaction.model_validate(new_transaction)
        return transaction_dto
    raise CustomExceptions.BAD_REQUEST.value


@LOGER.catch
@app.get("/{transaction_id}", response_model=schemas.Transaction)
async def get(
    transaction_id: uuid.UUID,
    session: AsyncSession = Depends(db.get_db),
    api_key: str = Depends(verify_api_key),
):
    if isinstance(api_key, CustomExceptions):
        raise api_key.value
    transaction = await db.Transaction.read_by_id(session, transaction_id)
    if transaction:
        transaction_dto = schemas.Transaction.model_validate(transaction)
        return transaction_dto
    raise CustomExceptions.NOT_FOUND.value


@LOGER.catch
@app.patch("/{transaction_id}/done", response_model=schemas.Transaction)
async def done_transaction(
    transaction_id: uuid.UUID,
    session: AsyncSession = Depends(db.get_db),
    api_key: str = Depends(verify_api_key),
):
    if isinstance(api_key, CustomExceptions):
        raise api_key.value
    result = await db.UoW(session).confirm_transaction(transaction_id)
    if result:
        LOGER.warning(result)
        result_dto = schemas.Transaction.model_validate(result)
        LOGER.info(result_dto)
        return result_dto
    raise CustomExceptions.BAD_REQUEST.value


@LOGER.catch
@app.patch("/{transaction_id}/cancel", response_model=schemas.Transaction)
async def cancel_transaction(
    transaction_id: uuid.UUID,
    session: AsyncSession = Depends(db.get_db),
    api_key: str = Depends(verify_api_key),
):
    if isinstance(api_key, CustomExceptions):
        raise api_key.value
    transaction = await db.Transaction.update(
        session, transaction_id, **{"status": db.TransactionStatus.CANCELED}
    )
    if transaction:
        transaction_dto = schemas.Transaction.model_validate(transaction)
        return transaction_dto
    raise CustomExceptions.NOT_FOUND.value
