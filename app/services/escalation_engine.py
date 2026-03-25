from datetime import timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.core.config import get_settings
from app.models.base import utc_now
from app.models.enums import EventStatus
from app.models.escalation_policy import EscalationPolicy
from app.models.event import Event
from app.services.audit_service import AuditService
from app.services.notification_service import NotificationService
from app.services.routing_engine import RoutingEngine


settings = get_settings()


class EscalationEngine:
    def __init__(self) -> None:
        self.routing_engine = RoutingEngine()
        self.notification_service = NotificationService()
        self.audit_service = AuditService()

    def schedule_follow_ups(self, event_id: str, first_wait: int, second_wait: int) -> None:
        if not settings.enable_background_escalation or settings.celery_task_always_eager:
            return
        from app.workers.tasks import process_first_escalation_task, process_second_contact_task

        process_first_escalation_task.apply_async(args=[event_id], countdown=first_wait)
        process_second_contact_task.apply_async(args=[event_id], countdown=second_wait)

    def dispatch_initial(self, session: Session, event: Event) -> None:
        policy = event.escalation_policy
        if policy is None:
            return
        plans = self.routing_engine.build_plans(event, policy, stage="initial")
        self.notification_service.dispatch(session, event, plans)
        event.next_escalation_at = utc_now() + timedelta(seconds=policy.first_wait_seconds)
        event.second_contact_due_at = utc_now() + timedelta(seconds=policy.second_wait_seconds)
        self.audit_service.record(
            session,
            action="escalation.initialized",
            actor="system",
            event_id=event.id,
            details={
                "policy_id": policy.id,
                "first_wait_seconds": policy.first_wait_seconds,
                "second_wait_seconds": policy.second_wait_seconds,
            },
        )
        self.schedule_follow_ups(event.id, policy.first_wait_seconds, policy.second_wait_seconds)

    def process_first_escalation(self, session: Session, event_id: str) -> bool:
        event = self._get_event(session, event_id)
        if not event or not self._ready_for_escalation(session, event, "first_escalation"):
            return False
        policy = event.escalation_policy
        if policy is None:
            return self._record_skip(session, event, "first_escalation", "missing_policy")

        plans = self.routing_engine.build_plans(event, policy, stage="first_escalation")
        if not plans:
            return self._record_skip(
                session,
                event,
                "first_escalation",
                "no_deliverable_primary_routes",
            )

        event.escalation_level = max(event.escalation_level, 1)
        notifications = self.notification_service.dispatch(session, event, plans)
        self.audit_service.record(
            session,
            action="escalation.first_triggered",
            actor="system",
            event_id=event.id,
            details={
                "escalation_level": event.escalation_level,
                "notification_ids": [notification.id for notification in notifications],
            },
        )
        session.flush()
        session.commit()
        return True

    def process_second_contact(self, session: Session, event_id: str) -> bool:
        event = self._get_event(session, event_id)
        if not event or not self._ready_for_escalation(session, event, "second_contact"):
            return False
        policy = event.escalation_policy
        if policy is None:
            return self._record_skip(session, event, "second_contact", "missing_policy")
        if policy.secondary_contact is None:
            return self._record_skip(session, event, "second_contact", "missing_secondary_contact")
        if not policy.secondary_contact.is_active:
            return self._record_skip(session, event, "second_contact", "inactive_secondary_contact")

        plans = self.routing_engine.build_plans(event, policy, stage="second_contact")
        if not plans:
            return self._record_skip(
                session,
                event,
                "second_contact",
                "no_deliverable_secondary_routes",
            )

        event.escalation_level = max(event.escalation_level, 2)
        notifications = self.notification_service.dispatch(session, event, plans)
        self.audit_service.record(
            session,
            action="escalation.second_triggered",
            actor="system",
            event_id=event.id,
            details={
                "escalation_level": event.escalation_level,
                "contact_id": policy.secondary_contact_id,
                "notification_ids": [notification.id for notification in notifications],
            },
        )
        session.flush()
        session.commit()
        return True

    def _ready_for_escalation(self, session: Session, event: Event, stage: str) -> bool:
        if event.status in {EventStatus.ACKNOWLEDGED.value, EventStatus.RESOLVED.value}:
            return self._record_skip(session, event, stage, f"status={event.status}")

        now = utc_now()
        if event.snooze_until and event.snooze_until > now:
            self.audit_service.record(
                session,
                action="escalation.rescheduled_for_snooze",
                actor="system",
                event_id=event.id,
                details={"stage": stage, "snooze_until": event.snooze_until.isoformat()},
            )
            if settings.enable_background_escalation and not settings.celery_task_always_eager:
                from app.workers.tasks import (
                    process_first_escalation_task,
                    process_second_contact_task,
                )

                if stage == "first_escalation":
                    process_first_escalation_task.apply_async(args=[event.id], eta=event.snooze_until)
                else:
                    process_second_contact_task.apply_async(args=[event.id], eta=event.snooze_until)
            session.commit()
            return False

        if event.status == EventStatus.SNOOZED.value and (
            event.snooze_until is None or event.snooze_until <= now
        ):
            event.status = EventStatus.OPEN.value
            self.audit_service.record(
                session,
                action="event.snooze_expired",
                actor="system",
                event_id=event.id,
                details={},
            )
        return True

    def _record_skip(
        self,
        session: Session,
        event: Event,
        stage: str,
        reason: str,
    ) -> bool:
        action = "escalation.second_skipped" if stage == "second_contact" else "escalation.first_skipped"
        self.audit_service.record(
            session,
            action=action,
            actor="system",
            event_id=event.id,
            details={"stage": stage, "reason": reason},
        )
        session.flush()
        session.commit()
        return False

    def _get_event(self, session: Session, event_id: str) -> Event | None:
        statement = (
            select(Event)
            .options(
                selectinload(Event.notifications),
                selectinload(Event.audit_logs),
                selectinload(Event.escalation_policy).selectinload(EscalationPolicy.primary_contact),
                selectinload(Event.escalation_policy).selectinload(EscalationPolicy.secondary_contact),
            )
            .where(Event.id == event_id)
        )
        return session.scalar(statement)
