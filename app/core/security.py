from datetime import datetime
from typing import Dict, Optional
from jose import jwt, JWTError
from app.config import settings

def create_access_token(data: Dict) -> str:
    """Создаёт access_token с ограниченным временем жизни"""
    to_encode = data.copy()
    expire = datetime.utcnow() + settings.access_token_expire
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def create_refresh_token(data: Dict) -> str:
    """Создаёт refresh_token с длительным временем жизни"""
    to_encode = data.copy()
    expire = datetime.utcnow() + settings.refresh_token_expire
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def decode_token(token: str) -> Optional[Dict]:
    """Декодирует токен и возвращает данные, либо None при ошибке"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        return None
