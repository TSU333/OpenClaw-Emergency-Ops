from datetime import datetime

from pydantic import BaseModel, Field


class AcknowledgeRequest(BaseModel):
    actor: str = Field(default="human")
    note: str | None = None
    contact_id: str | None = None


class SnoozeRequest(BaseModel):
    actor: str = Field(default="human")
    note: str | None = None
    contact_id: str | None = None
    minutes: int | None = 30
    until: datetime | None = None

