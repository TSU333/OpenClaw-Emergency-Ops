from fastapi import APIRouter

from app.core.config import get_settings


router = APIRouter()
settings = get_settings()


@router.get("/health")
def healthcheck() -> dict[str, str]:
    return {"status": "ok", "service": settings.app_name, "environment": settings.app_env}

