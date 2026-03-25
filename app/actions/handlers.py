from dataclasses import dataclass, field
from typing import Any

import httpx

from app.core.config import get_settings

settings = get_settings()


@dataclass(slots=True)
class ActionExecutionResult:
    ok: bool
    result_payload: dict[str, Any] = field(default_factory=dict)
    error_message: str | None = None


class WebhookActionHandler:
    def __init__(self, action_name: str, endpoint: str | None) -> None:
        self.action_name = action_name
        self.endpoint = endpoint

    def execute(self, event: Any, parameters: dict[str, Any]) -> ActionExecutionResult:
        payload = {
            "event_id": event.id,
            "source": event.source,
            "event_type": event.event_type,
            "severity": event.severity,
            "title": event.title,
            "message": event.message,
            "metadata": event.event_metadata,
            "parameters": parameters,
        }
        if not self.endpoint:
            return ActionExecutionResult(
                ok=True,
                result_payload={"mode": "dry_run", "payload": payload},
            )

        try:
            response = httpx.post(self.endpoint, json=payload, timeout=10)
            response.raise_for_status()
        except httpx.HTTPError as exc:
            return ActionExecutionResult(ok=False, error_message=str(exc), result_payload=payload)

        return ActionExecutionResult(
            ok=True,
            result_payload={
                "mode": "live",
                "status_code": response.status_code,
                "response": response.json() if response.content else {},
            },
        )


def get_action_handler(action_name: str) -> WebhookActionHandler | None:
    mapping = {
        "pause_strategy": settings.pause_strategy_endpoint,
        "close_positions": settings.close_positions_endpoint,
        "restart_service": settings.restart_service_endpoint,
    }
    endpoint = mapping.get(action_name)
    if action_name not in mapping:
        return None
    return WebhookActionHandler(action_name=action_name, endpoint=endpoint)

