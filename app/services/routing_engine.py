from dataclasses import dataclass

from app.models.contact import Contact
from app.models.enums import NotificationChannel, SeverityLevel
from app.models.escalation_policy import EscalationPolicy
from app.models.event import Event


@dataclass(slots=True)
class NotificationPlan:
    channel: str
    contact_id: str | None
    contact_name: str
    targets: list[str]
    escalation_step: int
    stage: str


class RoutingEngine:
    def build_plans(
        self,
        event: Event,
        policy: EscalationPolicy,
        stage: str,
    ) -> list[NotificationPlan]:
        contact: Contact | None
        escalation_step = 0
        if stage in {"initial", "first_escalation"}:
            contact = policy.primary_contact
            escalation_step = 0 if stage == "initial" else 1
        else:
            contact = policy.secondary_contact
            escalation_step = 2

        if contact is None or not contact.is_active:
            return []

        channels = self._channels_for(policy, SeverityLevel(event.severity))
        return self._plans_for_contact(contact, channels, escalation_step, stage)

    def _channels_for(self, policy: EscalationPolicy, severity: SeverityLevel) -> list[str]:
        if severity == SeverityLevel.INFO:
            return policy.info_channels
        if severity == SeverityLevel.WARNING:
            return policy.warning_channels
        if severity == SeverityLevel.CRITICAL:
            return policy.critical_channels
        return policy.p0_channels

    def _plans_for_contact(
        self,
        contact: Contact,
        channels: list[str],
        escalation_step: int,
        stage: str,
    ) -> list[NotificationPlan]:
        plans: list[NotificationPlan] = []
        for channel in channels:
            if channel == NotificationChannel.APPRISE.value and contact.apprise_targets:
                plans.append(
                    NotificationPlan(
                        channel=channel,
                        contact_id=contact.id,
                        contact_name=contact.name,
                        targets=contact.apprise_targets,
                        escalation_step=escalation_step,
                        stage=stage,
                    )
                )
            if channel in {
                NotificationChannel.SMS_FALLBACK.value,
                NotificationChannel.VOICE_CALL.value,
            } and contact.phone_number:
                plans.append(
                    NotificationPlan(
                        channel=channel,
                        contact_id=contact.id,
                        contact_name=contact.name,
                        targets=[contact.phone_number],
                        escalation_step=escalation_step,
                        stage=stage,
                    )
                )
        return plans
