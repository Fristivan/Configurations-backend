import os
import random
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from jinja2 import Template
from app.auth.auth_service import get_db
from app.database.crud import get_user_by_email, create_user, store_verification_code, get_verification_code, \
    delete_verification_code
from app.database.models import VerificationCode
from pydantic import BaseModel, Field, EmailStr
from datetime import datetime, timedelta

mail_router = APIRouter()


class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, description="Password must be at least 8 characters long")


class VerifyCode(BaseModel):
    email: str
    code: str

def load_email_template():
    base_path = os.path.dirname(os.path.abspath(__file__))  # Получаем путь текущего файла
    template_path = os.path.join(base_path, "email_verification_template.html")  # Создаем путь к файлу

    with open(template_path, "r", encoding="utf-8") as file:
        return Template(file.read())


def send_verification_email(email: str, code: str):
    sender_email = "code-verification@frist-it.online"
    sender_password = "pUavfGqaUQYpt5cBL7PU"
    smtp_server = "smtp.mail.ru"
    smtp_port = 465

    msg = MIMEMultipart()
    msg["Subject"] = "Verify Your Email"
    msg["From"] = sender_email
    msg["To"] = email

    template = load_email_template()
    html_content = template.render(code=code)
    msg.attach(MIMEText(html_content, "html"))

    try:
        with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, email, msg.as_string())
        print("✅ Verification email sent successfully!")
    except Exception as e:
        print("❌ Failed to send email:", str(e))


@mail_router.post("/register/request-code")
def request_verification_code(user: UserRegister, db: Session = Depends(get_db)):
    if get_user_by_email(db, user.email):
        raise HTTPException(status_code=400, detail="User already exists!")

    code = str(random.randint(100000, 999999))
    try:
        store_verification_code(db, user.email, code, user.password)
    except IntegrityError:
        raise HTTPException(status_code=400, detail="Вы уже зарегистрированы.")
    send_verification_email(user.email, code)
    return {"message": "Verification code sent to email"}


@mail_router.post("/register/verify")
def verify_registration(data: VerifyCode, db: Session = Depends(get_db)):
    stored_code_entry = get_verification_code(db, data.email)
    if not stored_code_entry:
        raise HTTPException(status_code=400, detail="No verification request found or code expired")

    if stored_code_entry.code != data.code:
        raise HTTPException(status_code=400, detail="Invalid verification code")

    create_user(db, data.email, stored_code_entry.password)
    delete_verification_code(db, data.email)
    return {"message": "User successfully registered"}
