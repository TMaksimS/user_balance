"""Файл настрокий родительского обьекта конфигурации схем"""

from pydantic import BaseModel, ConfigDict


class MyOrmModel(BaseModel):
    """Конфиг валидации ОРМ моделей"""
    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)