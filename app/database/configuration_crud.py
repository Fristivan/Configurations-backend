# app/crud/configuration_crud.py
from sqlalchemy.orm import Session
from app.database.models import Configuration, User
from app.schemas.configuration import ConfigurationCreate, ConfigurationUpdate

## Лимиты по подпискам
SUBSCRIPTION_LIMITS = {
    "free": 5,   # Базовый (раньше "basic")
    "paid": 25   # Платный (раньше "paid")
}

def create_configuration(db: Session, config: ConfigurationCreate, user_id: int):
    # Получаем пользователя
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return None  # Можно кинуть HTTPException

    # Определяем лимит для пользователя
    user_configs_count = db.query(Configuration).filter(Configuration.user_id == user_id).count()
    max_configs = SUBSCRIPTION_LIMITS.get(user.subscription_level, 5)  # По умолчанию считаем, что "free"

    if user_configs_count >= max_configs:
        raise ValueError(f"Превышен лимит конфигураций ({max_configs}) для уровня подписки {user.subscription_level}")

    # Если лимит не превышен, создаем конфигурацию
    db_config = Configuration(**config.dict(), user_id=user_id)
    db.add(db_config)
    db.commit()
    db.refresh(db_config)
    return db_config


def get_configurations_by_user(db: Session, user_id: int):
    return db.query(Configuration).filter(Configuration.user_id == user_id).all()

def get_configuration(db: Session, config_id: int, user_id: int):
    return db.query(Configuration).filter(Configuration.id == config_id, Configuration.user_id == user_id).first()

def update_configuration(db: Session, config_id: int, user_id: int, config_update: ConfigurationUpdate):
    db_config = get_configuration(db, config_id, user_id)
    if not db_config:
        return None
    for field, value in config_update.dict(exclude_unset=True).items():
        setattr(db_config, field, value)
    db.commit()
    db.refresh(db_config)
    return db_config

def delete_configuration(db: Session, config_id: int, user_id: int):
    db_config = get_configuration(db, config_id, user_id)
    if not db_config:
        return None
    db.delete(db_config)
    db.commit()
    return db_config
