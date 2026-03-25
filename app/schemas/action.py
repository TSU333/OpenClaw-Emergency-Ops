from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ActionRunRequest(BaseModel):
    actor: str = Field(default="human")
    parameters: dict[str, Any] = Field(default_factory=dict)


class ActionRunResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    action_name: str
    requested_by: str
    status: str
    request_payload: dict[str, Any] = Field(default_factory=dict)
    result_payload: dict[str, Any] = Field(default_factory=dict)
    error_message: str | None = None
    started_at: datetime | None = None
    finished_at: datetime | None = None

