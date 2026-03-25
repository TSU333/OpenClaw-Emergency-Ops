import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin
from app.models.enums import EventStatus, SeverityLevel


class Event(Base, TimestampMixin):
    __tablename__ = "events"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    source: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    event_type: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)

    severity_hint: Mapped[str | None] = mapped_column(String(32), nullable=True)
    severity: Mapped[str] = mapped_column(
        String(32),
        default=SeverityLevel.INFO.value,
        nullable=False,
        index=True,
    )
    status: Mapped[str] = mapped_column(
        String(32),
        default=EventStatus.OPEN.value,
        nullable=False,
        index=True,
    )

    event_metadata: Mapped[dict] = mapped_column("metadata", JSON, default=dict, nullable=False)
    suggested_actions: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    ai_summary: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)

    escalation_level: Mapped[int] = mapped_column(default=0, nullable=False)
    snooze_until: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    acknowledged_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    closed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    next_escalation_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    second_contact_due_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    primary_contact_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("contacts.id", ondelete="SET NULL"),
        nullable=True,
    )
    secondary_contact_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("contacts.id", ondelete="SET NULL"),
        nullable=True,
    )
    escalation_policy_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("escalation_policies.id", ondelete="SET NULL"),
        nullable=True,
    )

    escalation_policy: Mapped["EscalationPolicy | None"] = relationship(
        "EscalationPolicy",
        back_populates="events",
    )
    notifications: Mapped[list["Notification"]] = relationship(
        "Notification",
        back_populates="event",
        cascade="all, delete-orphan",
    )
    acknowledgements: Mapped[list["Acknowledgement"]] = relationship(
        "Acknowledgement",
        back_populates="event",
        cascade="all, delete-orphan",
    )
    action_runs: Mapped[list["ActionRun"]] = relationship(
        "ActionRun",
        back_populates="event",
        cascade="all, delete-orphan",
    )
    audit_logs: Mapped[list["AuditLog"]] = relationship(
        "AuditLog",
        back_populates="event",
        cascade="all, delete-orphan",
    )

