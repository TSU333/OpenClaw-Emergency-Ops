from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog


class TimelineService:
    def list_for_event(self, session: Session, event_id: str) -> list[AuditLog]:
        statement = (
            select(AuditLog)
            .where(AuditLog.event_id == event_id)
            .order_by(AuditLog.created_at)
        )
        return list(session.scalars(statement).all())

