"""Файл для запуска api"""
from contextlib import asynccontextmanager

import uvicorn
from apscheduler.schedulers.background import BackgroundScheduler
from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware

import database as db
from api import app as app_router
from src.config import LOGER
from src.settings import APP_HOST, APP_PORT, APP_RELOAD

def upd_meet_status():
    """задача по обновлению данных в БД"""
    db.UoW().upd_transaction_expired()


scheduler = BackgroundScheduler()
scheduler.add_job(upd_meet_status, 'cron', minute='*/1')

@asynccontextmanager
async def lifespan(app: FastAPI):
    scheduler.start()
    yield

origins = ["*"]
app = FastAPI(
    title="User Balance API",
    description="API",
    version="1.0",
    contact={
        "name": "Tarkin Maksim",
        "email": "williamcano97@gmail.com",
    },
    lifespan=lifespan
)

app.include_router(
    router=app_router
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "DELETE", "PUT", "PATCH", "OPTIONS"],
    allow_headers=[
        "Content-Type",
        "Set-Cookie",
        "Access-Control-Allow-Headers",
        "Access-Control-Allow-Origin",
        "Authorization",
        "X-API-KEY"
    ],
)


@app.get("/")
async def curl():
    """эндпоинт для проверки работоспособности uvicorn"""
    return Response(content="OK", status_code=200)

@LOGER.catch
def main(host: str, port: int, reload: bool) -> uvicorn:
    """Функция для запуска api"""
    return uvicorn.run(
        "main:app",
        host=f"{host}",
        port=port,
        reload=reload
    )


if __name__ == "__main__":
    main(host=APP_HOST, port=APP_PORT, reload=APP_RELOAD)
