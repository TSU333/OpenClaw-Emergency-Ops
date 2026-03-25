from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from app.models.event import Event
from app.schemas.action import ActionRunResponse
from app.schemas.common import AISummary, AuditLogResponse, ContactBrief, NotificationResponse


class EventIngestRequest(BaseModel):
    source: str
    event_type: str
    title: str
    message: str
    severity_hint: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    suggested_actions: list[str] = Field(default_factory=list)


class EventResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    source: str
    event_type: str
    title: str
    message: str
    severity_hint: str | None = None
    severity: str
    status: str
    metadata: dict[str, Any] = Field(default_factory=dict)
    suggested_actions: list[str] = Field(default_factory=list)
    ai_summary: AISummary
    escalation_level: int
    snooze_until: datetime | None = None
    acknowledged_at: datetime | None = None
    closed_at: datetime | None = None
    created_at: datetime
    updated_at: datetime
    primary_contact: ContactBrief | None = None
    secondary_contact: ContactBrief | None = None


class EventDetailResponse(EventResponse):
    notifications: list[NotificationResponse] = Field(default_factory=list)
    action_runs: list[ActionRunResponse] = Field(default_factory=list)
    timeline: list[AuditLogResponse] = Field(default_factory=list)


class EventTimelineResponse(BaseModel):
    event_id: str
    timeline: list[AuditLogResponse] = Field(default_factory=list)


def build_event_response(event: Event) -> EventResponse:
    return EventResponse(
        id=event.id,
        source=event.source,
        event_type=event.event_type,
        title=event.title,
        message=event.message,
        severity_hint=event.severity_hint,
        severity=event.severity,
        status=event.status,
        metadata=event.event_metadata,
        suggested_actions=event.suggested_actions,
        ai_summary=AISummary.model_validate(event.ai_summary),
        escalation_level=event.escalation_level,
        snooze_until=event.snooze_until,
        acknowledged_at=event.acknowledged_at,
        closed_at=event.closed_at,
        created_at=event.created_at,
        updated_at=event.updated_at,
        primary_contact=ContactBrief.model_validate(event.escalation_policy.primary_contact)
        if event.escalation_policy and event.escalation_policy.primary_contact
        else None,
        secondary_contact=ContactBrief.model_validate(event.escalation_policy.secondary_contact)
        if event.escalation_policy and event.escalation_policy.secondary_contact
        else None,
    )


def build_event_detail_response(event: Event) -> EventDetailResponse:
    base = build_event_response(event)
    return EventDetailResponse(
        **base.model_dump(),
        notifications=[
            NotificationResponse.model_validate(notification)
            for notification in sorted(event.notifications, key=lambda item: item.created_at)
        ],
        action_runs=[
            ActionRunResponse.model_validate(action_run)
            for action_run in sorted(event.action_runs, key=lambda item: item.created_at)
        ],
        timeline=[
            AuditLogResponse.model_validate(entry)
            for entry in sorted(event.audit_logs, key=lambda item: item.created_at)
        ],
    )
