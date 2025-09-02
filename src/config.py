"""Сборщик логов"""

from loguru import logger

LOGER = logger
LOGER.add(
    "backend-logs/error.log",
    rotation="100 KB",
    format="{time} {level} {message}",
    level="ERROR"
)
