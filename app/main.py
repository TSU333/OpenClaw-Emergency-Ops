from contextlib import asynccontextmanager

from fastapi import FastAPI

import app.models  # noqa: F401
from app.api.router import api_router
from app.core.config import get_settings
from app.core.database import init_db, session_scope
from app.services.bootstrap_service import BootstrapService


settings = get_settings()


@asynccontextmanager
async def lifespan(_: FastAPI):
    if settings.auto_create_tables:
        init_db()
    with session_scope() as session:
        BootstrapService().ensure_default_policy(session)
    yield


app = FastAPI(title=settings.app_name, lifespan=lifespan)
app.include_router(api_router, prefix=settings.api_prefix)


@app.get("/")
def root() -> dict[str, str]:
    return {"service": settings.app_name, "docs": "/docs", "api_prefix": settings.api_prefix}
