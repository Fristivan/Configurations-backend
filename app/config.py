from datetime import timedelta

SECRET_KEY = "your_secret_key"  # Замени на более сложный ключ
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60  # 1 час
REFRESH_TOKEN_EXPIRE_DAYS = 30  # 30 дней

ACCESS_TOKEN_EXPIRE = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
REFRESH_TOKEN_EXPIRE = timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)