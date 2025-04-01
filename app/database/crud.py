from datetime import datetime, timedelta

from fastapi import HTTPException, Depends
from sqlalchemy.orm import Session

from app.core.security import decode_token
from app.database.models import User, VerificationCode
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

def create_user(db: Session, email: str, password: str):
    hashed_password = pwd_context.hash(password)
    new_user = User(email=email, hashed_password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


def increment_user_requests(db: Session, user_id: int):
    """ Увеличивает количество использованных запросов пользователя """
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        user.requests_this_month += 1
        db.commit()


def store_verification_code(db: Session, email: str, code: str, password: str):
    expiration_time = datetime.utcnow() + timedelta(minutes=10)
    verification_entry = VerificationCode(email=email, code=code, password=password, expires_at=expiration_time)
    db.add(verification_entry)
    db.commit()

def get_verification_code(db: Session, email: str):
    return db.query(VerificationCode).filter(VerificationCode.email == email, VerificationCode.expires_at > datetime.utcnow()).first()

def delete_verification_code(db: Session, email: str):
    db.query(VerificationCode).filter(VerificationCode.email == email).delete()
    db.commit()
