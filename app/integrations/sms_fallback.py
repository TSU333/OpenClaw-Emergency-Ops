from app.integrations.types import DeliveryResult
from app.models.enums import NotificationStatus


class SMSFallbackClient:
    def send(self, phone_number: str | None, title: str, body: str) -> DeliveryResult:
        if not phone_number:
            return DeliveryResult(
                status=NotificationStatus.SKIPPED.value,
                provider_message="No phone number configured for SMS fallback.",
                response_payload={"mode": "no_phone"},
            )
        return DeliveryResult(
            status=NotificationStatus.SENT.value,
            provider_message="SMS-like fallback queued via placeholder adapter.",
            response_payload={
                "mode": "placeholder",
                "phone_number": phone_number,
                "title": title,
                "body_preview": body[:160],
            },
        )

