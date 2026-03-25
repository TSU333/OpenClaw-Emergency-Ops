from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = Field(default="OpenClaw Emergency Ops", alias="APP_NAME")
    app_env: str = Field(default="development", alias="APP_ENV")
    api_prefix: str = Field(default="/api/v1", alias="API_PREFIX")
    timezone: str = Field(default="Australia/Melbourne", alias="TIMEZONE")

    database_url: str = Field(
        default="postgresql+psycopg://openclaw:openclaw@postgres:5432/openclaw_ops",
        alias="DATABASE_URL",
    )
    redis_url: str = Field(default="redis://redis:6379/0", alias="REDIS_URL")
    celery_broker_url: str = Field(default="", alias="CELERY_BROKER_URL")
    celery_result_backend: str = Field(default="", alias="CELERY_RESULT_BACKEND")

    auto_create_tables: bool = Field(default=True, alias="AUTO_CREATE_TABLES")
    enable_background_escalation: bool = Field(
        default=True,
        alias="ENABLE_BACKGROUND_ESCALATION",
    )
    celery_task_always_eager: bool = Field(
        default=False,
        alias="CELERY_TASK_ALWAYS_EAGER",
    )
    apprise_enabled: bool = Field(default=True, alias="APPRISE_ENABLED")

    default_primary_contact_name: str = Field(
        default="Primary Operator",
        alias="DEFAULT_PRIMARY_CONTACT_NAME",
    )
    default_primary_contact_role: str = Field(
        default="operator",
        alias="DEFAULT_PRIMARY_CONTACT_ROLE",
    )
    default_primary_apprise_targets_raw: str = Field(
        default="",
        alias="DEFAULT_PRIMARY_APPRISE_TARGETS",
    )
    default_primary_phone_number: str | None = Field(
        default=None,
        alias="DEFAULT_PRIMARY_PHONE_NUMBER",
    )

    default_secondary_contact_name: str | None = Field(
        default="Secondary Operator",
        alias="DEFAULT_SECONDARY_CONTACT_NAME",
    )
    default_secondary_contact_role: str = Field(
        default="backup",
        alias="DEFAULT_SECONDARY_CONTACT_ROLE",
    )
    default_secondary_apprise_targets_raw: str = Field(
        default="",
        alias="DEFAULT_SECONDARY_APPRISE_TARGETS",
    )
    default_secondary_phone_number: str | None = Field(
        default=None,
        alias="DEFAULT_SECONDARY_PHONE_NUMBER",
    )

    escalation_first_wait_seconds: int = Field(
        default=300,
        alias="ESCALATION_FIRST_WAIT_SECONDS",
    )
    escalation_second_wait_seconds: int = Field(
        default=600,
        alias="ESCALATION_SECOND_WAIT_SECONDS",
    )

    openclaw_voice_call_url: str | None = Field(
        default=None,
        alias="OPENCLAW_VOICE_CALL_URL",
    )
    openclaw_voice_call_token: str | None = Field(
        default=None,
        alias="OPENCLAW_VOICE_CALL_TOKEN",
    )
    openclaw_voice_call_timeout_seconds: int = Field(
        default=10,
        alias="OPENCLAW_VOICE_CALL_TIMEOUT_SECONDS",
    )

    pause_strategy_endpoint: str | None = Field(
        default=None,
        alias="PAUSE_STRATEGY_ENDPOINT",
    )
    close_positions_endpoint: str | None = Field(
        default=None,
        alias="CLOSE_POSITIONS_ENDPOINT",
    )
    restart_service_endpoint: str | None = Field(
        default=None,
        alias="RESTART_SERVICE_ENDPOINT",
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        populate_by_name=True,
    )

    @property
    def broker_url(self) -> str:
        return self.celery_broker_url or self.redis_url

    @property
    def result_backend(self) -> str:
        return self.celery_result_backend or self.redis_url

    @property
    def default_primary_apprise_targets(self) -> list[str]:
        return [
            item.strip()
            for item in self.default_primary_apprise_targets_raw.split(",")
            if item.strip()
        ]

    @property
    def default_secondary_apprise_targets(self) -> list[str]:
        return [
            item.strip()
            for item in self.default_secondary_apprise_targets_raw.split(",")
            if item.strip()
        ]


@lru_cache
def get_settings() -> Settings:
    return Settings()
