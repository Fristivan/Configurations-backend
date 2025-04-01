from typing import Optional, Dict
from pydantic import BaseModel, Field


class SystemdConfig(BaseModel):
    description: str = Field(
        ...,
        example="My custom systemd service",
        description="Краткое описание службы, отображаемое в systemctl status."
    )
    after: str = Field(
        ...,
        example="network.target",
        description="Служба или цель, после которой должна быть запущена данная служба."
    )
    exec_start: str = Field(
        ...,
        example="/usr/bin/python3 /opt/app.py",
        description="Команда, которая будет выполняться при запуске службы."
    )
    restart_policy: Optional[str] = Field(
        None,
        example="always",
        description="Политика перезапуска службы (например: 'always', 'on-failure', 'no')."
    )
    user: Optional[str] = Field(
        None,
        example="appuser",
        description="Имя пользователя, от имени которого будет запущена служба."
    )
    group: Optional[str] = Field(
        None,
        example="appgroup",
        description="Группа, от имени которой будет запущена служба."
    )
    working_directory: Optional[str] = Field(
        None,
        example="/opt/app",
        description="Рабочая директория, в которой будет выполняться служба."
    )
    environment: Optional[Dict[str, str]] = Field(
        None,
        example={"ENV_VAR": "value", "DEBUG": "true"},
        description="Переменные окружения, которые будут установлены перед запуском службы."
    )
    timeout_start_sec: Optional[int] = Field(
        None,
        example=30,
        description="Время ожидания успешного запуска службы, перед тем как systemd решит, что запуск не удался."
    )
    timeout_stop_sec: Optional[int] = Field(
        None,
        example=30,
        description="Время ожидания корректного завершения службы перед принудительным завершением."
    )
    restart_sec: Optional[int] = Field(
        None,
        example=5,
        description="Задержка перед повторным запуском службы в случае её завершения."
    )
    log_level: Optional[str] = Field(
        None,
        example="info",
        description="Уровень логирования для этой службы (например: 'info', 'debug', 'warning')."
    )
    wanted_by: str = Field(
        default="multi-user.target",
        description="Цель, к которой привязывается служба. Обычно это multi-user.target."
    )
