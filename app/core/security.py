from datetime import datetime, timedelta
from jose import jwt
from typing import Dict

# Секретный ключ для подписи токенов
SECRET_KEY = "your_secret_key"
ALGORITHM = "HS256"

# Время жизни access и refresh токенов
ACCESS_TOKEN_EXPIRE_MINUTES = 60  # 1 час
REFRESH_TOKEN_EXPIRE_DAYS = 30    # 30 дней

def create_access_token(data: Dict):
    """Создаёт access_token с ограниченным временем жизни"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def create_refresh_token(data: Dict):
    """Создаёт refresh_token с более длительным временем жизни"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def decode_token(token: str):
    """Декодирует токен и возвращает его данные"""
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.JWTError:
        return None
