import os
import tempfile

import pytest
from fastapi.testclient import TestClient


TEST_DIR = tempfile.mkdtemp(prefix="openclaw-emergency-ops-")
TEST_DB_PATH = os.path.join(TEST_DIR, "test.db")

os.environ.setdefault("DATABASE_URL", f"sqlite+pysqlite:///{TEST_DB_PATH}")
os.environ.setdefault("AUTO_CREATE_TABLES", "false")
os.environ.setdefault("ENABLE_BACKGROUND_ESCALATION", "false")
os.environ.setdefault("CELERY_TASK_ALWAYS_EAGER", "false")
os.environ.setdefault("APPRISE_ENABLED", "false")
os.environ.setdefault("DEFAULT_PRIMARY_APPRISE_TARGETS", "")
os.environ.setdefault("DEFAULT_SECONDARY_APPRISE_TARGETS", "")
os.environ.setdefault("DEFAULT_PRIMARY_PHONE_NUMBER", "+61000000000")
os.environ.setdefault("DEFAULT_SECONDARY_PHONE_NUMBER", "+61000000001")

import app.models  # noqa: E402,F401
from app.core.database import SessionLocal, engine  # noqa: E402
from app.main import app  # noqa: E402
from app.models.base import Base  # noqa: E402
from app.services.bootstrap_service import BootstrapService  # noqa: E402


@pytest.fixture(autouse=True)
def reset_db() -> None:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as session:
        BootstrapService().ensure_default_policy(session)
        session.commit()


@pytest.fixture
def client() -> TestClient:
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def db_session():
    with SessionLocal() as session:
        yield session

