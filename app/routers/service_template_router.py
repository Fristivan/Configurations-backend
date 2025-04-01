from fastapi import APIRouter, Depends, HTTPException, File, UploadFile
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.database.service_template_crud import (
    create_service_template, get_all_service_templates,
    get_service_template_by_id, update_service_template, delete_service_template
)
from app.schemas.service_template import ServiceTemplateCreate, ServiceTemplateUpdate, ServiceTemplateResponse
from app.utils.image_utils import convert_image_to_base64

router = APIRouter(prefix="/templates")

@router.post("/", response_model=ServiceTemplateResponse)
def create_template(template: ServiceTemplateCreate, db: Session = Depends(get_db)):
    return create_service_template(db, template)

@router.get("/", response_model=list[ServiceTemplateResponse])
def list_templates(db: Session = Depends(get_db)):
    return get_all_service_templates(db)

@router.get("/{template_id}", response_model=ServiceTemplateResponse)
def get_template(template_id: int, db: Session = Depends(get_db)):
    template = get_service_template_by_id(db, template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    return template

@router.put("/{template_id}", response_model=ServiceTemplateResponse)
def update_template(template_id: int, template_update: ServiceTemplateUpdate, db: Session = Depends(get_db)):
    updated_template = update_service_template(db, template_id, template_update)
    if not updated_template:
        raise HTTPException(status_code=404, detail="Template not found")
    return updated_template

@router.delete("/{template_id}")
def delete_template(template_id: int, db: Session = Depends(get_db)):
    deleted_template = delete_service_template(db, template_id)
    if not deleted_template:
        raise HTTPException(status_code=404, detail="Template not found")
    return {"detail": "Template deleted"}


@router.post("/{template_id}/icon", response_model=ServiceTemplateResponse)
async def upload_template_icon(
        template_id: int,
        icon: UploadFile = File(...),
        db: Session = Depends(get_db)
):
    # Проверяем MIME-тип файла
    content_type = icon.content_type
    if not content_type.startswith("image/"):
        raise HTTPException(
            status_code=400,
            detail="Загруженный файл не является изображением"
        )

    # Получаем шаблон из БД
    template = get_service_template_by_id(db, template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")

    # Конвертируем изображение в Base64
    icon_base64 = convert_image_to_base64(icon)

    # Обновляем шаблон
    template_update = ServiceTemplateUpdate(icon=icon_base64)
    updated_template = update_service_template(db, template_id, template_update)

    return updated_template
