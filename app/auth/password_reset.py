# app/auth/password_reset.py

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import random
from app.auth.auth_service import get_db, pwd_context
from app.database.crud import get_user_by_email
from app.database.models import VerificationCode, User
from app.auth.mail_service import send_verification_email

password_reset_router = APIRouter()

class PasswordResetRequest(BaseModel):
    email: EmailStr

class PasswordResetConfirm(BaseModel):
    email: EmailStr
    code: str
    new_password: str = Field(..., min_length=8)
    confirm_password: str = Field(..., min_length=8)


@password_reset_router.post("/password/reset/request")
def request_password_reset(data: PasswordResetRequest, db: Session = Depends(get_db)):
    user = get_user_by_email(db, data.email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    code = str(random.randint(100000, 999999))
    expiration_time = datetime.utcnow() + timedelta(minutes=10)

    # Сохраняем код без пароля
    verification_entry = VerificationCode(
        email=data.email,
        code=code,
        password=user.hashed_password,  # Сохраняем текущий хэш, просто для совместимости
        expires_at=expiration_time
    )

    # Затираем старые коды для этого email
    db.query(VerificationCode).filter(VerificationCode.email == data.email).delete()
    db.add(verification_entry)
    db.commit()

    send_verification_email(data.email, code)

    return {"message": "Password reset code sent to email"}


@password_reset_router.post("/password/reset/confirm")
def confirm_password_reset(data: PasswordResetConfirm, db: Session = Depends(get_db)):
    if data.new_password != data.confirm_password:
        raise HTTPException(status_code=400, detail="Passwords do not match")

    verification_entry = db.query(VerificationCode).filter(
        VerificationCode.email == data.email,
        VerificationCode.code == data.code,
        VerificationCode.expires_at > datetime.utcnow()
    ).first()

    if not verification_entry:
        raise HTTPException(status_code=400, detail="Invalid or expired verification code")

    user = get_user_by_email(db, data.email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Обновляем пароль
    hashed_password = pwd_context.hash(data.new_password)
    user.hashed_password = hashed_password
    db.commit()

    # Удаляем использованный код
    db.delete(verification_entry)
    db.commit()

    return {"message": "Password successfully reset"}
