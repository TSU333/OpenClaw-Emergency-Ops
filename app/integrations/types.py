from dataclasses import dataclass, field
from typing import Any

from app.models.enums import NotificationStatus


@dataclass(slots=True)
class DeliveryResult:
    status: str = NotificationStatus.SENT.value
    provider_message: str | None = None
    response_payload: dict[str, Any] = field(default_factory=dict)

