from sqlalchemy.orm import Session

from app.actions.handlers import get_action_handler
from app.models.action_run import ActionRun
from app.models.base import utc_now
from app.models.enums import ActionStatus
from app.models.event import Event
from app.services.audit_service import AuditService


class ActionExecutor:
    def __init__(self) -> None:
        self.audit_service = AuditService()

    def execute(
        self,
        session: Session,
        event: Event,
        action_name: str,
        actor: str,
        parameters: dict | None = None,
    ) -> ActionRun:
        handler = get_action_handler(action_name)
        parameters = parameters or {}
        action_run = ActionRun(
            event_id=event.id,
            action_name=action_name,
            requested_by=actor,
            status=ActionStatus.RUNNING.value,
            request_payload=parameters,
            started_at=utc_now(),
        )
        session.add(action_run)
        session.flush()
        self.audit_service.record(
            session,
            action="action.requested",
            actor=actor,
            event_id=event.id,
            details={"action_run_id": action_run.id, "action_name": action_name},
        )

        if handler is None:
            action_run.status = ActionStatus.FAILED.value
            action_run.error_message = f"Unsupported action: {action_name}"
            action_run.finished_at = utc_now()
            self.audit_service.record(
                session,
                action="action.failed",
                actor=actor,
                event_id=event.id,
                details={
                    "action_run_id": action_run.id,
                    "action_name": action_name,
                    "reason": action_run.error_message,
                },
            )
            session.commit()
            session.refresh(action_run)
            return action_run

        result = handler.execute(event, parameters)
        action_run.result_payload = result.result_payload
        action_run.finished_at = utc_now()
        if result.ok:
            action_run.status = ActionStatus.SUCCEEDED.value
            self.audit_service.record(
                session,
                action="action.completed",
                actor=actor,
                event_id=event.id,
                details={"action_run_id": action_run.id, "action_name": action_name},
            )
        else:
            action_run.status = ActionStatus.FAILED.value
            action_run.error_message = result.error_message
            self.audit_service.record(
                session,
                action="action.failed",
                actor=actor,
                event_id=event.id,
                details={
                    "action_run_id": action_run.id,
                    "action_name": action_name,
                    "reason": result.error_message,
                },
            )
        session.commit()
        session.refresh(action_run)
        return action_run

