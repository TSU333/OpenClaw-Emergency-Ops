from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog


class AuditService:
    def record(
        self,
        session: Session,
        action: str,
        actor: str,
        details: dict | None = None,
        event_id: str | None = None,
    ) -> AuditLog:
        entry = AuditLog(
            event_id=event_id,
            actor=actor,
            action=action,
            details=details or {},
        )
        session.add(entry)
        session.flush()
        return entry

