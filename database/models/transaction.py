import uuid

from sqlalchemy import ForeignKey, UUID, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.db import Base
from database.models.user import User
from database.models.settings import TransactionStatus, CreatedAT, UpdatedAT


class Transaction(Base):
    """Object transaction DB"""
    __tablename__ = "transactions"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    amount: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[TransactionStatus]
    created_at: Mapped[CreatedAT]
    updated_at: Mapped[UpdatedAT]
    timeout_seconds: Mapped[int] = mapped_column(Integer, default=300, nullable=False)

    user: Mapped[User] = relationship(
        back_populates="transactions"
    )
