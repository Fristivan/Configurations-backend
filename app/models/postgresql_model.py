from pydantic import BaseModel, Field
from typing import Optional, Dict

class PostgreSQLConfig(BaseModel):
    include_comments: bool = Field(
        default=False,
        description="Включить комментарии в конфигурации"
    )

    # Обязательные настройки
    listen_addresses: str = Field(
        ...,
        example="*",
        description="Адреса для прослушивания (например: '*', 'localhost' или '0.0.0.0')"
    )
    port: int = Field(
        ...,
        example=5432,
        description="Порт PostgreSQL"
    )

    # Логирование
    enable_logging: bool = Field(
        default=False,
        description="Включить логирование в PostgreSQL"
    )
    log_directory: Optional[str] = Field(
        default="pg_log",
        example="pg_log",
        description="Директория для файлов логов"
    )
    log_filename: Optional[str] = Field(
        default="postgresql.log",
        example="postgresql.log",
        description="Имя файла логов"
    )
    log_statement: Optional[str] = Field(
        default="all",
        example="all",
        description="Какие SQL-запросы логировать (none, ddl, mod, all)"
    )

    # Соединения
    max_connections: int = Field(
        default=100,
        example=100,
        description="Максимальное число соединений с базой данных"
    )
    superuser_reserved_connections: int = Field(
        default=3,
        example=3,
        description="Число соединений, зарезервированных для суперпользователя"
    )

    # Настройки производительности
    shared_buffers: str = Field(
        default="128MB",
        example="128MB",
        description="Размер общего буфера в памяти"
    )
    work_mem: str = Field(
        default="4MB",
        example="4MB",
        description="Размер рабочей памяти на один запрос"
    )
    maintenance_work_mem: str = Field(
        default="64MB",
        example="64MB",
        description="Память для операций обслуживания БД"
    )

    # SSL
    enable_ssl: bool = Field(
        default=False,
        description="Использовать SSL-соединения"
    )
    ssl_cert_file: Optional[str] = Field(
        default="/etc/ssl/certs/ssl-cert.pem",
        example="/etc/ssl/certs/ssl-cert.pem",
        description="Путь к сертификату SSL"
    )
    ssl_key_file: Optional[str] = Field(
        default="/etc/ssl/private/ssl-cert.key",
        example="/etc/ssl/private/ssl-cert.key",
        description="Путь к закрытому ключу SSL"
    )

    # Репликация
    enable_replication: bool = Field(
        default=False,
        description="Включить репликацию PostgreSQL"
    )
    wal_level: Optional[str] = Field(
        default="replica",
        example="replica",
        description="Уровень WAL-логирования (minimal, replica, logical)"
    )
    max_wal_senders: Optional[int] = Field(
        default=10,
        example=10,
        description="Максимальное количество отправителей WAL"
    )
    synchronous_commit: Optional[str] = Field(
        default="on",
        example="on",
        description="Тип синхронного подтверждения (on, off, remote_apply)"
    )

    # Автоочистка
    enable_autovacuum: bool = Field(
        default=True,
        description="Включить автоочистку"
    )
    autovacuum_vacuum_threshold: Optional[int] = Field(
        default=50,
        example=50,
        description="Порог для запуска автоочистки"
    )
    autovacuum_analyze_threshold: Optional[int] = Field(
        default=50,
        example=50,
        description="Порог для запуска автоанализа"
    )

    # Пользовательские параметры
    custom_settings: Optional[Dict[str, str]] = Field(
        default={"shared_preload_libraries": "pg_stat_statements"},
        example={"shared_preload_libraries": "pg_stat_statements"},
        description="Дополнительные пользовательские настройки"
    )
