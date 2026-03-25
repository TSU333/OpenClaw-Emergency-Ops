from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ContactBrief(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    role: str
    phone_number: str | None = None
    apprise_targets: list[str] = Field(default_factory=list)
    is_secondary: bool = False


class AISummary(BaseModel):
    what_happened: str
    impact_scope: str
    current_risk: str
    recommended_actions: list[str] = Field(default_factory=list)
    recommend_immediate_stop_loss: bool = False
    operator_brief: str


class AuditLogResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    actor: str
    action: str
    details: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime


class NotificationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    channel: str
    target: str | None = None
    delivery_status: str
    escalation_step: int
    provider_message: str | None = None
    sent_at: datetime | None = None

