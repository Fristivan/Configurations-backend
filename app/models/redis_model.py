from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Tuple


class RedisConfig(BaseModel):
    include_comments: bool = Field(
        default=False,
        description="Включить комментарии в конфигурации"
    )

    # Обязательные основные настройки
    bind: str = Field(
        ...,
        example="127.0.0.1",
        description="IP-адрес Redis для прослушивания подключений"
    )
    port: int = Field(
        ...,
        example=6379,
        description="Порт Redis"
    )

    # Опциональные основные настройки
    timeout: Optional[int] = Field(
        default=0,
        example=0,
        description="Таймаут соединения в секундах (0 — без таймаута)"
    )

    # Логирование
    enable_logging: bool = Field(
        default=False,
        description="Включить логирование"
    )
    loglevel: Optional[str] = Field(
        default="notice",
        example="notice",
        description="Уровень логирования"
    )
    logfile: Optional[str] = Field(
        default="/var/log/redis/redis-server.log",
        example="/var/log/redis/redis-server.log",
        description="Путь к файлу журнала"
    )

    # Управление памятью
    maxmemory: Optional[str] = Field(
        default="256mb",
        example="256mb",
        description="Максимальный объем используемой памяти"
    )
    maxmemory_policy: Optional[str] = Field(
        default="noeviction",
        example="noeviction",
        description="Политика управления памятью"
    )

    # Персистентность
    enable_persistence: bool = Field(
        default=True,
        description="Включить сохранение данных на диск"
    )
    save_intervals: Optional[List[Tuple[int, int]]] = Field(
        default=[(900, 1), (300, 10), (60, 10000)],
        example=[(900, 1), (300, 10)],
        description="Интервалы сохранения данных (формат: секунды, количество изменений)"
    )

    # Репликация
    enable_replication: bool = Field(
        default=False,
        description="Включить репликацию"
    )
    slaveof: Optional[str] = Field(
        default="",
        example="192.168.1.100 6379",
        description="Адрес и порт мастера для репликации"
    )

    # Безопасность
    requirepass: Optional[str] = Field(
        default="",
        example="strongpassword123",
        description="Пароль для доступа к Redis"
    )

    # Пользовательские настройки
    custom_settings: Optional[Dict[str, str]] = Field(
        default={"appendonly": "yes"},
        example={"maxclients": "1000"},
        description="Дополнительные пользовательские параметры конфигурации"
    )
