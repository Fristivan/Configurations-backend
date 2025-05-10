FROM python:3.12-slim

# Установка зависимостей
WORKDIR /app

COPY req.txt .
RUN pip install --upgrade pip && pip install -r req.txt

# Копируем приложение
COPY . .

# Открываем порт
EXPOSE 8000

# Команда запуска
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
