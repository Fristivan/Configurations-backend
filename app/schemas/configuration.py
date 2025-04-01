# app/schemas/configuration.py
from datetime import datetime
from typing import Optional
from pydantic import BaseModel

class ConfigurationBase(BaseModel):
    service: str
    config_name: str
    config_data: str

class ConfigurationCreate(ConfigurationBase):
    pass

class ConfigurationUpdate(BaseModel):
    config_name: Optional[str] = None
    config_data: Optional[str] = None

class Configuration(ConfigurationBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True