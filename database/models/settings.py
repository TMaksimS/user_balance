import datetime
import enum
from typing import Annotated

from sqlalchemy import func
from sqlalchemy.orm import mapped_column

CreatedAT = Annotated[
    datetime.datetime, mapped_column(server_default=func.now(), nullable=True)
]
UpdatedAT = Annotated[
    datetime.datetime, mapped_column(server_default=func.now(), onupdate=func.now())
]


class TransactionStatus(enum.Enum):
    """Enum statuses Transaction"""

    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELED = "canceled"
    EXPIRED = "expired"
