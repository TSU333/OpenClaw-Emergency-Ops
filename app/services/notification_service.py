from sqlalchemy.orm import Session

from app.integrations.apprise_client import AppriseClient
from app.integrations.sms_fallback import SMSFallbackClient
from app.integrations.voice_call import OpenClawVoiceCallClient
from app.models.enums import NotificationChannel
from app.models.event import Event
from app.models.notification import Notification
from app.models.base import utc_now
from app.services.audit_service import AuditService
from app.services.routing_engine import NotificationPlan


class NotificationService:
    def __init__(self) -> None:
        self.apprise_client = AppriseClient()
        self.sms_client = SMSFallbackClient()
        self.voice_client = OpenClawVoiceCallClient()
        self.audit_service = AuditService()

    def dispatch(
        self,
        session: Session,
        event: Event,
        plans: list[NotificationPlan],
    ) -> list[Notification]:
        sent_notifications: list[Notification] = []
        for plan in plans:
            title = self._build_title(event, plan.stage)
            body = self._build_body(event, plan.stage)
            if plan.channel == NotificationChannel.APPRISE.value:
                result = self.apprise_client.send(plan.targets, title, body)
            elif plan.channel == NotificationChannel.SMS_FALLBACK.value:
                result = self.sms_client.send(plan.targets[0] if plan.targets else None, title, body)
            else:
                result = self.voice_client.send(
                    phone_number=plan.targets[0] if plan.targets else None,
                    event_id=event.id,
                    event_title=event.title,
                    severity=event.severity,
                    summary=event.ai_summary,
                )

            notification = Notification(
                event_id=event.id,
                contact_id=plan.contact_id,
                channel=plan.channel,
                target=", ".join(plan.targets),
                delivery_status=result.status,
                escalation_step=plan.escalation_step,
                provider_message=result.provider_message,
                response_payload=result.response_payload,
                sent_at=utc_now(),
            )
            session.add(notification)
            session.flush()
            sent_notifications.append(notification)
            self.audit_service.record(
                session,
                action="notification.dispatched",
                actor="system",
                event_id=event.id,
                details={
                    "notification_id": notification.id,
                    "channel": plan.channel,
                    "contact_id": plan.contact_id,
                    "stage": plan.stage,
                    "status": result.status,
                    "targets": plan.targets,
                },
            )
        return sent_notifications

    def _build_title(self, event: Event, stage: str) -> str:
        stage_label = stage.replace("_", " ").upper()
        return f"[{event.severity.upper()}][{stage_label}] {event.title}"

    def _build_body(self, event: Event, stage: str) -> str:
        summary = event.ai_summary
        actions = ", ".join(summary.get("recommended_actions", [])) or "manual review"
        return (
            f"Event ID: {event.id}\n"
            f"Stage: {stage}\n"
            f"Source: {event.source}\n"
            f"Type: {event.event_type}\n"
            f"Message: {event.message}\n"
            f"What happened: {summary.get('what_happened', '')}\n"
            f"Impact: {summary.get('impact_scope', '')}\n"
            f"Risk: {summary.get('current_risk', '')}\n"
            f"Recommended actions: {actions}\n"
            f"Immediate stop loss: {summary.get('recommend_immediate_stop_loss', False)}"
        )

