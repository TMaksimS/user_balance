import datetime
import uuid

from sqlalchemy import select, func, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from database.db import sync_engine
from database.models import User, Transaction, TransactionStatus
from src.config import LOGER
from api import schemas


class UoW:
    def __init__(self, session: AsyncSession = None):
        self._session: AsyncSession = session
        self._sync_engine = sync_engine

    @LOGER.catch
    async def get_all_transactions_with_page(
        self, limit: int, offset: int, user_id: uuid.UUID
    ) -> tuple:
        """Получает все транзакции пользователя"""
        query = (
            select(Transaction)
            .where(Transaction.user_id == user_id)
            .limit(limit)
            .offset((offset - 1) * limit)
        )
        total_query = (
            select(func.count())
            .select_from(Transaction)
            .where(Transaction.user_id == user_id)
        )
        query_result = await self._session.execute(
            query.order_by(Transaction.created_at.desc())
        )
        result = query_result.scalars()
        counter = await self._session.execute(total_query)
        counter_result = counter.scalar()
        return (result, counter_result)

    @LOGER.catch
    async def get_user_with_lock(self, user_id: int) -> User:
        """Получает пользователя и блокирует его запись для изменения."""
        result = await self._session.execute(
            select(User).where(User.id == user_id).with_for_update()
        )
        result = result.scalar_one_or_none()
        return result

    @LOGER.catch
    async def create_transaction(self, **kwargs) -> schemas.Transaction | None:
        """Создает новую транзакцию с проверкой баланса и блокировками"""
        async with self._session.begin():
            user = await self._session.get(
                User, kwargs.get("user_id"), with_for_update=True
            )
            if not user:
                LOGER.error(f"User {kwargs.get("user_id")} not found")
                return None

            LOGER.info(f"User balance: {user.current_balance}, Max: {user.max_balance}")
            if kwargs.get("amount") < 0:
                reserved_balance = await self._get_reserved_balance(
                    kwargs.get("user_id"), is_negative=True
                )
                available_balance = user.current_balance - reserved_balance
                LOGER.info(
                    f"Available balance: {available_balance},"
                    f" Requested: {abs(kwargs.get("amount"))}"
                )
                if available_balance < abs(kwargs.get("amount")):
                    LOGER.error(f"Insufficient funds for user {kwargs.get("user_id")}")
                    return None
            elif kwargs.get("amount") > 0:
                reserved_balance = await self._get_reserved_balance(
                    kwargs.get("user_id"), is_negative=False
                )
                LOGER.error(reserved_balance)
                new_balance = (
                    user.current_balance + kwargs.get("amount") + reserved_balance
                )
                LOGER.warning(new_balance)
                if new_balance > user.max_balance:
                    LOGER.error(
                        f"Balance would exceed max limit for user {kwargs.get("amount")}"
                    )
                    return None
            db_transaction = Transaction(**kwargs)
            self._session.add(db_transaction)
            LOGER.info(
                f"Transaction created. "
                f"User: {kwargs.get("user_id")},"
                f" Amount: {kwargs.get("amount")},"
                f" Type: {'DEBIT' if kwargs.get("amount") < 0 else 'CREDIT'}"
            )
        return schemas.Transaction.model_validate(db_transaction)

    @LOGER.catch
    async def confirm_transaction(
        self, transaction_id: uuid.UUID
    ) -> schemas.Transaction | None:
        """Подтверждает транзакцию и применяет изменение баланса"""
        async with self._session.begin():
            transaction = await self._session.get(
                Transaction, transaction_id, with_for_update=True
            )
            if not transaction:
                LOGER.error(f"Transaction {transaction_id} not found")
                return None
            if transaction.status != TransactionStatus.PENDING:
                LOGER.warning(
                    f"Transaction {transaction_id} has invalid status: {transaction.status}"
                )
                return None
            if transaction.created_at < (
                datetime.datetime.now()
                - datetime.timedelta(seconds=transaction.timeout_seconds)
            ):
                transaction.status = TransactionStatus.EXPIRED
                LOGER.warning(f"Transaction {transaction_id} expired")
                return None
            user = await self._session.get(
                User, transaction.user_id, with_for_update=True
            )
            if transaction.amount < 0:
                reserved_balance = await self._get_reserved_balance(user.id)
                available_balance = user.current_balance - reserved_balance
                if available_balance < abs(transaction.amount):
                    LOGER.error(
                        f"Insufficient funds for user {user.id}."
                        f" Available: {available_balance},"
                        f" required: {abs(transaction.amount)}"
                    )
                    return None

            elif transaction.amount > 0:
                new_balance = user.current_balance + transaction.amount
                if new_balance > user.max_balance:
                    LOGER.error(f"Balance would exceed max limit for user {user.id}")
                    return None
            user.current_balance += transaction.amount
            if user.current_balance < 0:
                LOGER.critical(
                    f"Critical error: Balance went negative for user {user.id}"
                )
                return None
            transaction.status = TransactionStatus.CONFIRMED
            transaction.updated_at = datetime.datetime.now()
            LOGER.info(
                f"Transaction {transaction_id} confirmed."
                f" Amount: {transaction.amount},"
                f" New balance: {user.current_balance}"
            )
        return schemas.Transaction.model_validate(transaction)

    @LOGER.catch
    async def _get_reserved_balance(self, user_id: int, is_negative: bool) -> int:
        """Вычисляет сумму заблокированных средств для списаний"""
        if is_negative:
            amount_condition = Transaction.amount < 0
        else:
            amount_condition = Transaction.amount > 0
        stmt = select(func.coalesce(func.sum(Transaction.amount), 0)).where(
            (Transaction.user_id == user_id)
            & (Transaction.status == TransactionStatus.PENDING)
            & amount_condition
        )
        result = await self._session.execute(stmt)
        reserved_sum = result.scalar()
        if is_negative:
            return abs(reserved_sum) if reserved_sum < 0 else 0
        else:
            return reserved_sum if reserved_sum > 0 else 0

    @LOGER.catch
    def upd_transaction_expired(self):
        """метод для обновления статусов у транзакции"""
        with Session(self._sync_engine) as session:
            sql = text(
                """
            UPDATE transactions 
            SET status = 'EXPIRED' 
            WHERE status = 'PENDING' 
            AND created_at < NOW() - INTERVAL '1 second' * timeout_seconds
            """
            )
            res = session.execute(sql)
            session.commit()
            session.close()
            return res
