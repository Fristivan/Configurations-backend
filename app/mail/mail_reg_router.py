# app/auth/mail_router.py

import random
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field, EmailStr

from app.auth.auth_service import get_db
from app.database.crud import get_user_by_email, create_user, store_verification_code, get_verification_code, delete_verification_code
from app.mail.mail_service import send_email

mail_router = APIRouter()


class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, description="Password must be at least 8 characters long")


class VerifyCode(BaseModel):
    email: str
    code: str


@mail_router.post("/register/request-code/")
def request_verification_code(user: UserRegister, db: Session = Depends(get_db)):
    if get_user_by_email(db, user.email):
        raise HTTPException(status_code=400, detail="User already exists!")

    code = str(random.randint(100000, 999999))
    try:
        store_verification_code(db, user.email, code, user.password)
    except IntegrityError:
        raise HTTPException(status_code=400, detail="Вы уже зарегистрированы.")

    send_email(
        receiver_email=user.email,
        subject=f"Ваш код: {code} | Подтверждение регистрации",
        template_name="email_verification_template.html",
        context={"code": code}
    )

    return {"message": "Verification code sent to email"}


@mail_router.post("/register/verify/")
def verify_registration(data: VerifyCode, db: Session = Depends(get_db)):
    stored_code_entry = get_verification_code(db, data.email)
    if not stored_code_entry:
        raise HTTPException(status_code=400, detail="No verification request found or code expired")

    if stored_code_entry.code != data.code:
        raise HTTPException(status_code=400, detail="Invalid verification code")

    create_user(db, data.email, stored_code_entry.password)
    delete_verification_code(db, data.email)
    return {"message": "User successfully registered"}
