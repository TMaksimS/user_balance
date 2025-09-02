"""Инициализирующий файл для подключения всех роутеров"""

from fastapi import APIRouter

from api.routers import user_router
from api.routers import transaction_router

app = APIRouter(prefix="/api/v1")
app.include_router(user_router)
app.include_router(transaction_router)