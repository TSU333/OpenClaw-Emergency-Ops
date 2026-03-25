from app.core.config import get_settings
from app.integrations.types import DeliveryResult
from app.models.enums import NotificationStatus

settings = get_settings()

try:
    import apprise
except ImportError:  # pragma: no cover - covered indirectly via dry-run fallback
    apprise = None


class AppriseClient:
    def send(self, targets: list[str], title: str, body: str) -> DeliveryResult:
        if not targets:
            return DeliveryResult(
                status=NotificationStatus.SKIPPED.value,
                provider_message="No Apprise targets configured.",
                response_payload={"mode": "no_targets"},
            )
        if not settings.apprise_enabled:
            return DeliveryResult(
                status=NotificationStatus.SKIPPED.value,
                provider_message="Apprise disabled by configuration.",
                response_payload={"mode": "disabled"},
            )
        if apprise is None:
            return DeliveryResult(
                status=NotificationStatus.FAILED.value,
                provider_message="Apprise package is not installed.",
                response_payload={"mode": "missing_dependency"},
            )

        client = apprise.Apprise()
        for target in targets:
            client.add(target)

        success = client.notify(title=title, body=body)
        return DeliveryResult(
            status=NotificationStatus.SENT.value if success else NotificationStatus.FAILED.value,
            provider_message="Apprise notification sent." if success else "Apprise notification failed.",
            response_payload={"targets": targets, "success": success},
        )

