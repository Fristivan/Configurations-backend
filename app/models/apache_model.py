from typing import Optional
from pydantic import BaseModel, Field


class ApacheConfig(BaseModel):
    port: int = Field(
        default=80, 
        description="Порт, на котором Apache будет слушать соединения. Обычно 80 для HTTP или 443 для HTTPS."
    )
    server_admin: str = Field(
        default="webmaster@localhost", 
        description="Email администратора сервера. Используется для сообщений об ошибках."
    )
    server_name: str = Field(
        ..., 
        description="Основное доменное имя, которое обрабатывает сервер. Например: example.com"
    )
    server_alias: Optional[str] = Field(
        None, 
        description="Дополнительные домены, которые указывают на этот же сайт. Например: www.example.com"
    )
    document_root: str = Field(
        ..., 
        description="Путь к корневой директории веб-сайта. Например: /var/www/html"
    )

    directory_options: Optional[str] = Field(
        None, 
        description="Опции для <Directory>. Например: Indexes FollowSymLinks"
    )
    allow_override: Optional[str] = Field(
        None, 
        description="Разрешенные директивы в .htaccess (например: All, None, AuthConfig)"
    )
    directory_index: Optional[str] = Field(
        None, 
        description="Файл, который будет загружаться по умолчанию (например: index.html, index.php)"
    )
    directory_allow: Optional[str] = Field(
        None, 
        description="Параметры разрешения доступа в каталоге. Обычно: 'Require all granted'"
    )

    log_enabled: bool = Field(
        default=True, 
        description="Включить ведение логов для этого виртуального хоста?"
    )

    ssl_enabled: bool = Field(
        default=False, 
        description="Включить поддержку SSL/TLS? Требует установки ssl_certificate_file и ssl_certificate_key_file."
    )
    ssl_certificate_file: Optional[str] = Field(
        None, 
        description="Путь к файлу SSL-сертификата. Например: /etc/apache2/ssl/cert.pem"
    )
    ssl_certificate_key_file: Optional[str] = Field(
        None, 
        description="Путь к приватному ключу SSL. Например: /etc/apache2/ssl/key.pem"
    )
    ssl_chain_file: Optional[str] = Field(
        None, 
        description="Путь к файлу цепочки сертификатов (если требуется). Например: /etc/apache2/ssl/chain.pem"
    )
    ssl_protocols: Optional[str] = Field(
        None, 
        description="Список допустимых протоколов SSL/TLS. Например: TLSv1.2 TLSv1.3"
    )
    ssl_ciphers: Optional[str] = Field(
        None, 
        description="Список допустимых шифров SSL/TLS. Например: HIGH:!aNULL:!MD5"
    )
    ssl_session_cache: Optional[str] = Field(
        None, 
        description="Настройки кэша SSL-сессий. Например: 'shmcb:/var/run/apache2/ssl_scache(512000)'"
    )

    proxy_pass: Optional[str] = Field(
        None, 
        description="URL назначения для обратного прокси. Например: http://127.0.0.1:3000"
    )
    proxy_path: Optional[str] = Field(
        None, 
        description="Путь, который будет проксироваться. Например: /api"
    )

    compression_enabled: bool = Field(
        default=False, 
        description="Включить сжатие ответов сервера с помощью mod_deflate?"
    )
    security_headers: bool = Field(
        default=False, 
        description="Включить стандартные заголовки безопасности (Content-Security-Policy, X-Frame-Options и т.д.)?"
    )

    rewrite_rules: Optional[str] = Field(
        None, 
        description="Правила mod_rewrite для перенаправления URL-адресов. Например: 'RewriteEngine On'"
    )

    additional_config: Optional[str] = Field(
        None, 
        description="Дополнительные настройки Apache, которые можно вставить в конфигурацию виртуального хоста."
    )
