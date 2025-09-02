import uuid

from sqlalchemy import UUID, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.db import Base


class User(Base):
    """Object user DB"""
    __tablename__ = "users"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    current_balance: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    max_balance: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    transactions: Mapped[list["Transaction"]] = relationship(
        back_populates="user",
        uselist=True
    )
