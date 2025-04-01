# В app/schemas/service_template.py

from pydantic import BaseModel
from typing import Optional

class ServiceTemplateBase(BaseModel):
    name: str
    description: Optional[str] = None
    file_extension: Optional[str] = None
    template_filename: str
    icon: Optional[str] = None  # Base64-строка

class ServiceTemplateCreate(ServiceTemplateBase):
    pass

class ServiceTemplateUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    file_extension: Optional[str] = None
    template_filename: Optional[str] = None
    icon: Optional[str] = None

class ServiceTemplateResponse(ServiceTemplateBase):
    id: int

    class Config:
        orm_mode = True