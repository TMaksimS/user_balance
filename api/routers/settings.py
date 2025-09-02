import enum

from fastapi import Header, HTTPException

from src.config import LOGER
from src.settings import X_API_KEY


class CustomExceptions(enum.Enum):
    """Кастомные ошибки"""

    BAD_REQUEST = HTTPException(status_code=400, detail="Bad Request")
    PERMISSION_ERROR = HTTPException(status_code=423, detail="Permission Locked")
    NOT_FOUND = HTTPException(status_code=404, detail="Not Found")
    CREDENTIALS_EXCEPTION = HTTPException(
        status_code=401,
        detail="Invalid API Key",
    )


@LOGER.catch
async def verify_api_key(x_api_key: str = Header(...)) -> str | CustomExceptions:
    if x_api_key != X_API_KEY:
        return CustomExceptions.CREDENTIALS_EXCEPTION
    return x_api_key
