from datetime import datetime, timedelta
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship

from app.database.database import Base


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)

    # Подписка и лимиты
    subscription_level = Column(String, default="free", nullable=False)
    subscription_expiry = Column(DateTime, default=lambda: datetime.utcnow() + timedelta(days=30), nullable=False)
    request_limit = Column(Integer, default=15, nullable=False)
    requests_this_month = Column(Integer, default=0, nullable=False)
    limit_reset_date = Column(DateTime, default=lambda: datetime.utcnow() + timedelta(days=30), nullable=False)

    # Связи
    configurations = relationship("Configuration", back_populates="user", cascade="all, delete-orphan")
    payment_orders = relationship("PaymentOrder", back_populates="user", cascade="all, delete-orphan")


class Configuration(Base):
    __tablename__ = "configurations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    service = Column(String, nullable=False)
    config_name = Column(String, nullable=False)
    config_data = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="configurations")


class VerificationCode(Base):
    __tablename__ = "verification_codes"

    email = Column(String, primary_key=True, index=True, nullable=False)
    code = Column(String, nullable=False)
    password = Column(String, nullable=False)
    expires_at = Column(DateTime, nullable=False, default=lambda: datetime.utcnow() + timedelta(minutes=10))


class ServiceTemplate(Base):
    __tablename__ = "service_templates"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    file_extension = Column(String, nullable=True)
    template_filename = Column(String, nullable=False)
    icon = Column(Text, nullable=True)


class PaymentOrder(Base):
    __tablename__ = "payment_orders"

    order_id = Column(String, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    plan = Column(String, nullable=False)
    amount = Column(String, nullable=False)
    status = Column(String, default="created", nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="payment_orders")
