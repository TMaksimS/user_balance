"""Модуль для считывания .env"""

from envparse import Env

env = Env()
env.read_envfile(path=".env")

DB_ECHO = env.bool("DB_ECHO")
DB_USER = env.str("DB_USER", default="postgres_test")
DB_PASS = env.str("DB_PASS", default="postgres_test")
DB_NAME = env.str("DB_NAME", default="postgres_test")
DB_HOST = env.str("DB_HOST", default="localhost")
REAL_DATABASE_URL = env.str(
    "REAL_DATABASE_URL",
    default=f"postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}:5432/{DB_NAME}",
)
APP_PORT = env.int("APP_PORT", default=8000)
APP_HOST = env.str("APP_HOST", default="0.0.0.0")
APP_RELOAD = env.bool("APP_RELOAD", default=True)
X_API_KEY = env.str("X_API_KEY")
