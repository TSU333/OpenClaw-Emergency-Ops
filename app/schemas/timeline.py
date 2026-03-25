from pydantic import BaseModel, Field

from app.schemas.common import AuditLogResponse


class TimelineResponse(BaseModel):
    event_id: str
    items: list[AuditLogResponse] = Field(default_factory=list)
