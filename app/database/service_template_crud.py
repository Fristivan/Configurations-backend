from sqlalchemy.orm import Session
from app.database.models import ServiceTemplate
from app.schemas.service_template import ServiceTemplateCreate, ServiceTemplateUpdate

def create_service_template(db: Session, template: ServiceTemplateCreate):
    db_template = ServiceTemplate(**template.dict())
    db.add(db_template)
    db.commit()
    db.refresh(db_template)
    return db_template

def get_all_service_templates(db: Session):
    return db.query(ServiceTemplate).all()

def get_service_template_by_id(db: Session, template_id: int):
    return db.query(ServiceTemplate).filter(ServiceTemplate.id == template_id).first()

def update_service_template(db: Session, template_id: int, template_update: ServiceTemplateUpdate):
    db_template = db.query(ServiceTemplate).filter(ServiceTemplate.id == template_id).first()
    if db_template:
        for key, value in template_update.dict(exclude_unset=True).items():
            setattr(db_template, key, value)
        db.commit()
        db.refresh(db_template)
    return db_template

def delete_service_template(db: Session, template_id: int):
    db_template = db.query(ServiceTemplate).filter(ServiceTemplate.id == template_id).first()
    if db_template:
        db.delete(db_template)
        db.commit()
    return db_template
