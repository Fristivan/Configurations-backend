from typing import Optional, List, Dict
from pydantic import BaseModel, Field


class CopyFile(BaseModel):
    source: str = Field(
        ...,
        example="./local/path/file.txt",
        description="Путь к файлу или папке на хосте, который нужно скопировать в контейнер."
    )
    destination: str = Field(
        ...,
        example="/app/file.txt",
        description="Путь внутри контейнера, куда будет скопирован файл или папка."
    )


class HealthCheck(BaseModel):
    test: List[str] = Field(
        ...,
        example=["CMD", "curl", "-f", "http://localhost"],
        description="Команда для проверки работоспособности контейнера."
    )
    interval: str = Field(
        ...,
        example="30s",
        description="Интервал между проверками работоспособности контейнера."
    )
    timeout: str = Field(
        ...,
        example="10s",
        description="Время ожидания перед завершением неудачной проверки."
    )
    retries: int = Field(
        ...,
        example=3,
        description="Количество попыток перед тем, как пометить контейнер как неработоспособный."
    )


class DockerfileConfig(BaseModel):
    base_image: Optional[str] = Field(
        None,
        example="python:3.9",
        description="Образ контейнера, на основе которого будет создан новый контейнер."
    )
    maintainer: Optional[str] = Field(
        None,
        example="admin@example.com",
        description="Email или имя разработчика контейнера."
    )
    workdir: Optional[str] = Field(
        None,
        example="/app",
        description="Рабочая директория контейнера."
    )
    copy_files: Optional[List[CopyFile]] = Field(
        default=[],
        example=[{"source": "./app", "destination": "/app"}],
        description="Список файлов или директорий, которые будут скопированы в контейнер."
    )
    run_commands: Optional[List[str]] = Field(
        default=[],
        example=["apt-get update", "pip install -r requirements.txt"],
        description="Список команд, которые будут выполнены при сборке контейнера."
    )
    expose_ports: Optional[List[int]] = Field(
        default=[],
        example=[80, 443],
        description="Порты, которые должны быть доступны в контейнере."
    )
    entrypoint: Optional[str] = Field(
        None,
        example="python app.py",
        description="Основная команда, которая будет запущена в контейнере."
    )
    cmd: Optional[List[str]] = Field(
        default=[],
        example=["gunicorn", "app:app"],
        description="Команда, которая будет выполнена при запуске контейнера."
    )
    env_variables: Optional[Dict[str, str]] = Field(
        default={},
        example={"APP_ENV": "production", "DATABASE_URL": "postgres://user:pass@db:5432/dbname"},
        description="Переменные окружения, которые будут заданы в контейнере."
    )
    labels: Optional[Dict[str, str]] = Field(
        default={},
        example={"maintainer": "admin@example.com", "version": "1.0"},
        description="Метаинформация о контейнере в формате ключ-значение."
    )
    volumes: Optional[List[str]] = Field(
        default=[],
        example=["/data:/var/data"],
        description="Тома, которые будут примонтированы к контейнеру."
    )
    user: Optional[str] = Field(
        None,
        example="appuser",
        description="Пользователь, от имени которого будет выполняться контейнер."
    )
    healthcheck: Optional[HealthCheck] = Field(
        None,
        description="Настройки проверки работоспособности контейнера."
    )


class ServiceConfig(BaseModel):
    image: str = Field(
        ...,
        example="nginx:latest",
        description="Docker-образ контейнера."
    )
    container_name: Optional[str] = Field(
        None,
        example="my_nginx",
        description="Название контейнера."
    )
    ports: Optional[List[str]] = Field(
        None,
        example=["80:80", "443:443"],
        description="Порты в формате host:container."
    )
    volumes: Optional[List[str]] = Field(
        None,
        example=["./data:/app/data"],
        description="Тома для монтирования данных."
    )
    networks: Optional[List[str]] = Field(
        None,
        example=["backend", "frontend"],
        description="Сети, к которым подключен контейнер."
    )
    build: Optional[Dict[str, str]] = Field(
        None,
        example={"context": ".", "dockerfile": "Dockerfile"},
        description="Настройки сборки образа контейнера."
    )
    command: Optional[List[str]] = Field(
        None,
        example=["npm", "start"],
        description="Команда, выполняемая при запуске контейнера."
    )


class DockerComposeConfig(BaseModel):
    version: str = Field(
        "3.9",
        example="3.9",
        description="Версия docker-compose файла."
    )
    services: Dict[str, ServiceConfig] = Field(
        ...,
        description="Определяет контейнеры в конфигурации."
    )
    networks: Optional[Dict[str, Dict[str, str]]] = Field(
        None,
        example={"frontend": {}, "backend": {}},
        description="Определяет сети для контейнеров."
    )
    volumes: Optional[Dict[str, Dict[str, str]]] = Field(
        None,
        example={"db_data": {}},
        description="Общие тома для контейнеров."
    )