from typing import Optional, List
from pydantic import Field, BaseModel, validator


class SSHConfig(BaseModel):
    port: Optional[int] = Field(
        22,
        description="Порт, на котором слушает SSH-сервер. Обычно 22, но можно изменить для повышения безопасности."
    )
    protocol: Optional[int] = Field(
        2,
        description="Версия протокола SSH. Версия 2 является более безопасной и рекомендуется к использованию."
    )
    permit_root_login: Optional[str] = Field(
        "prohibit-password",
        description="Разрешить ли вход под root-пользователем. Опции: 'yes', 'no', 'without-password', 'prohibit-password'."
    )
    max_auth_tries: Optional[int] = Field(
        6,
        description="Максимальное количество попыток аутентификации перед разрывом соединения."
    )
    max_sessions: Optional[int] = Field(
        10,
        description="Максимальное количество одновременных сеансов SSH на сервере."
    )

    allow_users: Optional[List[str]] = Field(
        None,
        description="Список пользователей, которым разрешён вход по SSH (если не указан, разрешены все)."
    )
    deny_users: Optional[List[str]] = Field(
        None,
        description="Список пользователей, которым запрещён вход по SSH."
    )
    allow_groups: Optional[List[str]] = Field(
        None,
        description="Список групп, членам которых разрешён вход по SSH."
    )
    deny_groups: Optional[List[str]] = Field(
        None,
        description="Список групп, членам которых запрещён вход по SSH."
    )

    password_authentication: Optional[bool] = Field(
        None,
        description="Разрешить аутентификацию по паролю? (True - разрешено, False - только по ключу)."
    )
    permit_empty_passwords: Optional[bool] = Field(
        None,
        description="Разрешить ли вход с пустыми паролями (не рекомендуется)."
    )
    pubkey_authentication: Optional[bool] = Field(
        None,
        description="Разрешить ли аутентификацию с использованием публичного ключа?"
    )
    authorized_keys_file: Optional[str] = Field(
        None,
        description="Файл с авторизованными ключами. Обычно: '~/.ssh/authorized_keys'."
    )

    client_alive_interval: Optional[int] = Field(
        None,
        description="Частота отправки keepalive-запросов клиенту (в секундах)."
    )
    client_alive_count_max: Optional[int] = Field(
        None,
        description="Максимальное количество keepalive-запросов, после которых клиент будет отключен."
    )

    x11_forwarding: Optional[bool] = Field(
        None,
        description="Разрешить ли X11 forwarding (перенаправление графического интерфейса через SSH)."
    )
    banner: Optional[str] = Field(
        None,
        description="Путь к файлу баннера, который будет отображаться перед входом в систему."
    )
    subsystem_sftp: Optional[str] = Field(
        None,
        description="Путь к SFTP-субсистеме. Обычно: '/usr/lib/openssh/sftp-server'."
    )

    # Добавляем валидаторы
    @validator(
        'allow_users',
        'deny_users',
        'allow_groups',
        'deny_groups',
        pre=True
    )
    def empty_string_to_list(cls, v):
        """ Преобразуем пустые строки в None для списков """
        if v == "":
            return None
        return v

    @validator(
        'client_alive_interval',
        'client_alive_count_max',
        pre=True
    )
    def empty_string_to_int(cls, v):
        """ Преобразуем пустые строки в None для целых чисел """
        if v == "":
            return None
        return v