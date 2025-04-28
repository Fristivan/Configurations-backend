# app/mail/mail_service.py

import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from jinja2 import Template
from app.config import settings

def load_template(template_filename: str) -> Template:
    """Загружает HTML-шаблон письма"""
    base_path = os.path.dirname(os.path.abspath(__file__))
    template_path = os.path.join(base_path, template_filename)

    with open(template_path, "r", encoding="utf-8") as file:
        return Template(file.read())

def send_email(receiver_email: str, subject: str, template_name: str, context: dict):
    """Отправляет email"""
    msg = MIMEMultipart()
    msg["Subject"] = subject
    msg["From"] = settings.SMTP_USER
    msg["To"] = receiver_email

    template = load_template(template_name)
    html_content = template.render(**context)
    msg.attach(MIMEText(html_content, "html"))

    try:
        with smtplib.SMTP_SSL(settings.SMTP_SERVER, settings.SMTP_PORT) as server:
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.sendmail(settings.SMTP_USER, receiver_email, msg.as_string())
        print(f"✅ Письмо отправлено на {receiver_email}")
    except Exception as e:
        print(f"❌ Ошибка отправки письма: {e}")
