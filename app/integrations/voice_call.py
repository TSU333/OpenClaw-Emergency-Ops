import httpx

from app.core.config import get_settings
from app.integrations.types import DeliveryResult
from app.models.enums import NotificationStatus


settings = get_settings()


class OpenClawVoiceCallClient:
    def build_script(self, event_title: str, severity: str, summary: dict) -> str:
        return (
            f"OpenClaw emergency alert. Severity {severity}. "
            f"{event_title}. "
            f"Impact: {summary.get('impact_scope', 'Scope unknown')}. "
            f"Risk: {summary.get('current_risk', 'Risk assessment unavailable')}. "
            f"Recommended actions: {', '.join(summary.get('recommended_actions', [])) or 'review immediately'}."
        )

    def send(
        self,
        phone_number: str | None,
        event_id: str,
        event_title: str,
        severity: str,
        summary: dict,
    ) -> DeliveryResult:
        if not phone_number:
            return DeliveryResult(
                status=NotificationStatus.SKIPPED.value,
                provider_message="No phone number configured for voice call.",
                response_payload={"mode": "no_phone"},
            )

        script = self.build_script(event_title, severity, summary)
        if not settings.openclaw_voice_call_url:
            return DeliveryResult(
                status=NotificationStatus.SENT.value,
                provider_message="Voice call simulated. Configure OPENCLAW_VOICE_CALL_URL for live calls.",
                response_payload={
                    "mode": "dry_run",
                    "phone_number": phone_number,
                    "script": script,
                },
            )

        headers = {}
        if settings.openclaw_voice_call_token:
            headers["Authorization"] = f"Bearer {settings.openclaw_voice_call_token}"

        payload = {
            "phone_number": phone_number,
            "event_id": event_id,
            "title": event_title,
            "severity": severity,
            "script": script,
        }

        try:
            response = httpx.post(
                settings.openclaw_voice_call_url,
                json=payload,
                headers=headers,
                timeout=settings.openclaw_voice_call_timeout_seconds,
            )
            response.raise_for_status()
        except httpx.HTTPError as exc:
            return DeliveryResult(
                status=NotificationStatus.FAILED.value,
                provider_message=f"Voice call dispatch failed: {exc}",
                response_payload={"mode": "http_error"},
            )

        return DeliveryResult(
            status=NotificationStatus.SENT.value,
            provider_message="Voice call dispatched to OpenClaw Voice Call.",
            response_payload={
                "mode": "live",
                "status_code": response.status_code,
                "provider_response": response.json() if response.content else {},
            },
        )

