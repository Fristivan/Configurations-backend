from fastapi import APIRouter, HTTPException, Response, Depends
from sqlalchemy.orm import Session
from typing import get_args, Optional, get_type_hints

from app.auth.auth_service import get_current_user, get_db, check_user_limit, increment_user_requests
from app.services import render_template
from app.models.postgresql_model import PostgreSQLConfig

router = APIRouter()

@router.get("/form-metadata/postgresql")
def get_postgresql_form_metadata():
    schema = PostgreSQLConfig.schema()
    fields = []
    dependencies = {}

    dependency_map = {
        "enable_ssl": ["ssl_cert_file", "ssl_key_file"],
        "enable_logging": ["log_directory", "log_filename", "log_statement"],
        "enable_replication": ["wal_level", "max_wal_senders", "synchronous_commit"],
        "enable_autovacuum": ["autovacuum_vacuum_threshold", "autovacuum_analyze_threshold"]
    }

    type_hints = get_type_hints(PostgreSQLConfig)

    type_mapping = {
        bool: "bool",
        int: "int",
        str: "str",
        dict: "dict",
    }

    def get_real_type(field_name):
        annotation = type_hints.get(field_name, str)
        if hasattr(annotation, "__origin__") and annotation.__origin__ is Optional:
            annotation = get_args(annotation)[0]
        return annotation

    for field_name, field_info in schema["properties"].items():
        python_type = get_real_type(field_name)
        mapped_type = type_mapping.get(python_type, "str")

        field = {
            "name": field_name,
            "label": field_name.replace("_", " ").capitalize(),
            "required": field_name in schema.get("required", []),
            "defaultValue": field_info.get("default", None),
            "description": field_info.get("description", ""),
            "variableType": mapped_type
        }

        if mapped_type == "bool":
            field["type"] = "checkbox"
        elif mapped_type == "int":
            field["type"] = "number"
        elif mapped_type == "dict":
            field["type"] = "json"
        else:
            field["type"] = "text"

        if "example" in field_info:
            field["placeholder"] = str(field_info["example"])

        field["isAdvanced"] = not field["required"] and not field_name.startswith("enable_")

        if field_name in dependency_map:
            dependencies[field_name] = dependency_map[field_name]

        fields.append(field)

    return {"fields": fields, "dependencies": dependencies}

@router.post("/generate/postgresql")
def generate_postgresql(
    config: PostgreSQLConfig,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")

    if not check_user_limit(db, user.id):
        raise HTTPException(status_code=403, detail="Request limit exceeded")

    postgresql_conf = render_template("postgresql.j2", config.dict())
    increment_user_requests(db, user.id)

    return Response(content=postgresql_conf, media_type="text/plain")
