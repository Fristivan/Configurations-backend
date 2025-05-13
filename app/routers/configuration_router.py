# app/routers/configuration_router.py
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.auth.auth_service import get_current_user
from app.database.models import User
from app.schemas.configuration import Configuration, ConfigurationCreate, ConfigurationUpdate
from app.database.configuration_crud import (
    create_configuration,
    get_configurations_by_user,
    get_configuration,
    update_configuration,
    delete_configuration
)

router = APIRouter(
    prefix="/configurations"
)

@router.post("", response_model=Configuration)
def create_config(
    config: ConfigurationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        new_config = create_configuration(db, config, current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return new_config

@router.get("", response_model=List[Configuration])
def read_configs(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    configs = get_configurations_by_user(db, current_user.id)
    return configs

@router.get("/{config_id}", response_model=Configuration)
def read_config(
    config_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    config = get_configuration(db, config_id, current_user.id)
    if not config:
        raise HTTPException(status_code=404, detail="Configuration not found")
    return config

@router.put("/{config_id}", response_model=Configuration)
def update_config(
    config_id: int,
    config_update: ConfigurationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    config = update_configuration(db, config_id, current_user.id, config_update)
    if not config:
        raise HTTPException(status_code=404, detail="Configuration not found")
    return config

@router.delete("/{config_id}", response_model=Configuration)
def delete_config(
    config_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    config = delete_configuration(db, config_id, current_user.id)
    if not config:
        raise HTTPException(status_code=404, detail="Configuration not found")
    return config