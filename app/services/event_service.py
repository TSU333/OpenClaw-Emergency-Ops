from datetime import timedelta

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.acknowledgement import Acknowledgement
from app.models.base import utc_now
from app.models.enums import AcknowledgementAction, EventStatus
from app.models.escalation_policy import EscalationPolicy
from app.models.event import Event
from app.rules.default_rules import default_actions_for
from app.schemas.acknowledgement import AcknowledgeRequest, SnoozeRequest
from app.schemas.event import EventIngestRequest
from app.services.audit_service import AuditService
from app.services.bootstrap_service import BootstrapService
from app.services.escalation_engine import EscalationEngine
from app.services.severity_engine import SeverityEngine
from app.services.summary_service import SummaryService


class EventService:
    def __init__(self) -> None:
        self.audit_service = AuditService()
        self.bootstrap_service = BootstrapService()
        self.escalation_engine = EscalationEngine()
        self.severity_engine = SeverityEngine()
        self.summary_service = SummaryService()

    def ingest(self, session: Session, payload: EventIngestRequest) -> Event:
        policy = self.bootstrap_service.ensure_default_policy(session, source=payload.source)
        severity = self.severity_engine.determine(payload)
        suggested_actions = payload.suggested_actions or default_actions_for(
            payload.event_type,
            severity,
        )
        summary = self.summary_service.generate(payload, severity)

        event = Event(
            source=payload.source,
            event_type=payload.event_type,
            title=payload.title,
            message=payload.message,
            severity_hint=payload.severity_hint,
            severity=severity.value,
            status=EventStatus.OPEN.value,
            event_metadata=payload.metadata,
            suggested_actions=suggested_actions,
            ai_summary=summary.model_dump(),
            primary_contact_id=policy.primary_contact_id,
            secondary_contact_id=policy.secondary_contact_id,
            escalation_policy_id=policy.id,
            escalation_policy=policy,
        )
        session.add(event)
        session.flush()
        self.audit_service.record(
            session,
            action="event.ingested",
            actor=payload.source,
            event_id=event.id,
            details={
                "event_type": payload.event_type,
                "severity": severity.value,
                "suggested_actions": suggested_actions,
            },
        )
        self.escalation_engine.dispatch_initial(session, event)
        session.commit()
        return self.get_or_404(session, event.id)

    def acknowledge(self, session: Session, event_id: str, payload: AcknowledgeRequest) -> Event:
        event = self.get_or_404(session, event_id)
        event.status = EventStatus.ACKNOWLEDGED.value
        event.acknowledged_at = event.acknowledged_at or utc_now()
        ack = Acknowledgement(
            event_id=event.id,
            contact_id=payload.contact_id,
            actor=payload.actor,
            action=AcknowledgementAction.ACKNOWLEDGE.value,
            note=payload.note,
        )
        session.add(ack)
        self.audit_service.record(
            session,
            action="event.acknowledged",
            actor=payload.actor,
            event_id=event.id,
            details={"note": payload.note, "contact_id": payload.contact_id},
        )
        session.commit()
        return self.get_or_404(session, event.id)

    def snooze(self, session: Session, event_id: str, payload: SnoozeRequest) -> Event:
        event = self.get_or_404(session, event_id)
        snooze_until = payload.until or (utc_now() + timedelta(minutes=payload.minutes or 30))
        event.status = EventStatus.SNOOZED.value
        event.snooze_until = snooze_until
        ack = Acknowledgement(
            event_id=event.id,
            contact_id=payload.contact_id,
            actor=payload.actor,
            action=AcknowledgementAction.SNOOZE.value,
            note=payload.note,
            snooze_until=snooze_until,
        )
        session.add(ack)
        self.audit_service.record(
            session,
            action="event.snoozed",
            actor=payload.actor,
            event_id=event.id,
            details={
                "note": payload.note,
                "contact_id": payload.contact_id,
                "snooze_until": snooze_until.isoformat(),
            },
        )
        session.commit()
        return self.get_or_404(session, event.id)

    def list_events(self, session: Session) -> list[Event]:
        statement = (
            select(Event)
            .options(
                selectinload(Event.notifications),
                selectinload(Event.action_runs),
                selectinload(Event.audit_logs),
                selectinload(Event.escalation_policy).selectinload(EscalationPolicy.primary_contact),
                selectinload(Event.escalation_policy).selectinload(EscalationPolicy.secondary_contact),
            )
            .order_by(Event.created_at.desc())
        )
        return list(session.scalars(statement).all())

    def get_or_404(self, session: Session, event_id: str) -> Event:
        statement = (
            select(Event)
            .options(
                selectinload(Event.notifications),
                selectinload(Event.action_runs),
                selectinload(Event.audit_logs),
                selectinload(Event.escalation_policy).selectinload(EscalationPolicy.primary_contact),
                selectinload(Event.escalation_policy).selectinload(EscalationPolicy.secondary_contact),
            )
            .where(Event.id == event_id)
        )
        event = session.scalar(statement)
        if event is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Event {event_id} not found.",
            )
        return event
