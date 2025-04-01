from typing import Optional, List
from pydantic import BaseModel, Field

class NginxConfig(BaseModel):
    # Обязательные параметры
    server_name: str = Field(
        ...,
        example="example.com",
        description="Доменное имя или IP-адрес сервера. Например: example.com или 192.168.1.1"
    )
    listen: int = Field(
        ...,
        example=80,
        description="Порт, на котором Nginx будет слушать соединения. По умолчанию: 80 (HTTP). Для HTTPS укажите 443."
    )
    root: str = Field(
        ...,
        example="/var/www/html",
        description="Директория, содержащая файлы веб-сайта. Например: /var/www/html"
    )
    index: str = Field(
        ...,
        example="index.html",
        description="Главная страница сайта, которая будет загружаться по умолчанию. Например: index.html, index.php"
    )

    # SSL
    enable_ssl: bool = Field(
        False,
        description="Включает поддержку HTTPS. Требует указания ssl_certificate и ssl_certificate_key."
    )
    ssl_certificate: Optional[str] = Field(
        "/etc/nginx/ssl/cert.pem",
        example="/etc/nginx/ssl/cert.pem",
        description="Путь к SSL-сертификату для шифрования соединения (если включен HTTPS)."
    )
    ssl_certificate_key: Optional[str] = Field(
        "/etc/nginx/ssl/key.pem",
        example="/etc/nginx/ssl/key.pem",
        description="Путь к закрытому ключу SSL-сертификата."
    )

    # Redirect HTTP → HTTPS
    force_https: bool = Field(
        False,
        description="Автоматически перенаправляет HTTP-запросы на HTTPS (если включено SSL)."
    )

    # Gzip
    enable_gzip: bool = Field(
        False,
        description="Включает сжатие Gzip для уменьшения размера передаваемых данных."
    )

    # Логи
    enable_logging: bool = Field(
        False,
        description="Включает ведение логов доступа и ошибок."
    )
    access_log: Optional[str] = Field(
        "/var/log/nginx/access.log",
        example="/var/log/nginx/access.log",
        description="Путь к файлу журнала доступа."
    )
    error_log: Optional[str] = Field(
        "/var/log/nginx/error.log",
        example="/var/log/nginx/error.log",
        description="Путь к файлу журнала ошибок."
    )

    # Proxy
    enable_proxy: bool = Field(
        False,
        description="Включает проксирование запросов на другой сервер (reverse proxy)."
    )
    proxy_pass: Optional[str] = Field(
        "http://127.0.0.1:3000",
        example="http://127.0.0.1:3000",
        description="Адрес целевого сервера для проксирования (например, backend-сервис)."
    )

    # Ограничения
    limit_rate: Optional[str] = Field(
        "100k",
        example="100k",
        description="Ограничивает скорость загрузки для клиентов. Например: 100k (100 килобайт в секунду)."
    )
    limit_conn: Optional[str] = Field(
        "10",
        example="10",
        description="Ограничивает количество одновременных подключений от одного IP-адреса."
    )

    # Basic Auth
    enable_basic_auth: bool = Field(
        False,
        description="Включает базовую HTTP-аутентификацию (логин/пароль)."
    )
    auth_user_file: Optional[str] = Field(
        "/etc/nginx/.htpasswd",
        example="/etc/nginx/.htpasswd",
        description="Путь к файлу .htpasswd с учетными данными пользователей."
    )

    # CORS
    enable_cors: bool = Field(
        False,
        description="Разрешает кросс-доменные запросы (CORS)."
    )
    cors_allowed_origins: Optional[List[str]] = Field(
        ["https://example.com", "https://api.example.com"],
        example=["https://example.com", "https://api.example.com"],
        description="Список разрешенных источников (origin) для CORS."
    )

    # WebSockets
    enable_websockets: bool = Field(
        False,
        description="Включает поддержку WebSockets."
    )
