# Configurations-backend

**Configurations-backend** — это серверное приложение на FastAPI, предназначенное для управления пользовательскими конфигурациями. Оно реализует безопасную авторизацию через JWT-токены, которые хранятся в HTTP-only куках, и предоставляет API для создания и управления конфигурациями. Визуальное представление конфигураций формируется с помощью шаблонов Jinja2 или Mako. Для работы с базой данных используется Alembic.

---

## 🚀 Стек технологий

- **Python 3**
- **FastAPI** — асинхронный web-фреймворк
- **JWT (JSON Web Tokens)** — механизм авторизации
- **HTTP-only Cookies** — безопасное хранение токенов
- **Alembic** — миграции базы данных
- **Jinja2 / Mako** — шаблонизаторы
- **Uvicorn** — ASGI-сервер

---

## ⚙️ Принцип работы

### Общий процесс

1. Пользователь проходит аутентификацию.
2. Сервер устанавливает JWT-токен в безопасной HTTP-only cookie.
3. Все защищённые запросы автоматически содержат эту куку.
4. Пользователь может выполнять действия: создавать, получать или удалять конфигурации.
5. По выходу — кука очищается, и доступ блокируется.

---

## 🔐 Аутентификация через JWT в HTTP-only cookies

### Преимущества подхода:

- **Безопасность от XSS**: cookie с флагом `HttpOnly` не доступна из JavaScript.
- **Удобство**: браузер автоматически отправляет cookie с каждым запросом.

### JWT Flow

```
[ Клиент ] -- POST /auth/login --> [ Сервер ]
              <-- Set-Cookie: access_token=...; HttpOnly; Secure --

[ Клиент ] -- GET /configs --> [ Сервер ]
              (автоматически отправляет access_token cookie)

[ Клиент ] -- POST /auth/logout --> [ Сервер ]
              <-- Set-Cookie: access_token=""; Max-Age=0 --
```

---

## 📥 Примеры API-запросов

### 🔑 Авторизация

#### Вход (Login)

```http
POST /auth/login
Content-Type: application/json

{
  "username": "user1",
  "password": "your_password"
}
```

**Ответ:**  
- `Set-Cookie: access_token=<jwt>; HttpOnly; Secure`
- `200 OK`

---

#### Выход (Logout)

```http
POST /auth/logout
```

**Ответ:**  
- `Set-Cookie: access_token=""; Max-Age=0`
- `200 OK`

---

### 📦 Конфигурации

> Все действия требуют авторизованного пользователя (наличие access_token cookie)

#### Получить список конфигураций

```http
GET /configs
```

#### Создать конфигурацию

```http
POST /configs
Content-Type: application/json

{
  "name": "My Config",
  "template_type": "jinja2",
  "variables": {
    "env": "production",
    "version": "1.0.0"
  }
}
```

#### Удалить конфигурацию

```http
DELETE /configs/{config_id}
```

---

## 🛠️ Установка и запуск

```bash
git clone https://github.com/Fristivan/Configurations-backend.git
cd Configurations-backend

python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate

pip install -r req.txt
alembic upgrade head

uvicorn app.main:app --reload
#Или
python3 -m app.main #В корне проекта
```

Приложение доступно по адресу: [http://127.0.0.1:8000](http://127.0.0.1:8000)

---

## 📚 Swagger-документация

FastAPI автоматически предоставляет интерактивную документацию:

- Swagger UI: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- ReDoc: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)
