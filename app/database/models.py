from datetime import datetime, timedelta

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship

from app.database.database import Base


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    subscription_level = Column(String, default="free")
    request_limit = Column(Integer, default=15)  # Бесплатные 15 запросов
    requests_this_month = Column(Integer, default=0)  # Учёт использованных запросов
    limit_reset_date = Column(DateTime, default=lambda: datetime.utcnow() + timedelta(days=30))

    # Для связи с конфигурациями:
    configurations = relationship("Configuration", back_populates="user")


class Configuration(Base):
    __tablename__ = "configurations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    service = Column(String, nullable=False)  # Название или тип сервиса
    config_name = Column(String, nullable=False)  # Имя конфигурации
    config_data = Column(String, nullable=False)  # Данные конфигурации (например, JSON в виде строки)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="configurations")


class VerificationCode(Base):
    __tablename__ = "verification_codes"

    email = Column(String, primary_key=True, index=True, nullable=False)
    code = Column(String, nullable=False)
    password = Column(String, nullable=False)  # Хранение пароля до подтверждения регистрации
    expires_at = Column(DateTime, nullable=False, default=datetime.utcnow)

class ServiceTemplate(Base):
    __tablename__ = "service_templates"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    file_extension = Column(String, nullable=True)
    template_filename = Column(String, nullable=False)
    icon = Column(Text, nullable=True)  # Для хранения Base64-строки иконки