import uuid

from sqlalchemy import Boolean, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class EscalationPolicy(Base, TimestampMixin):
    __tablename__ = "escalation_policies"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    applies_to_source: Mapped[str | None] = mapped_column(String(255), nullable=True)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    primary_contact_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("contacts.id", ondelete="RESTRICT"),
        nullable=False,
    )
    secondary_contact_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("contacts.id", ondelete="SET NULL"),
        nullable=True,
    )

    info_channels: Mapped[list[str]] = mapped_column(JSON, default=lambda: ["apprise"], nullable=False)
    warning_channels: Mapped[list[str]] = mapped_column(JSON, default=lambda: ["apprise"], nullable=False)
    critical_channels: Mapped[list[str]] = mapped_column(
        JSON,
        default=lambda: ["apprise", "sms_fallback"],
        nullable=False,
    )
    p0_channels: Mapped[list[str]] = mapped_column(
        JSON,
        default=lambda: ["apprise", "voice_call"],
        nullable=False,
    )

    first_wait_seconds: Mapped[int] = mapped_column(Integer, default=300, nullable=False)
    second_wait_seconds: Mapped[int] = mapped_column(Integer, default=600, nullable=False)

    primary_contact: Mapped["Contact"] = relationship(
        "Contact",
        foreign_keys=[primary_contact_id],
        back_populates="primary_policies",
    )
    secondary_contact: Mapped["Contact | None"] = relationship(
        "Contact",
        foreign_keys=[secondary_contact_id],
        back_populates="secondary_policies",
    )
    events: Mapped[list["Event"]] = relationship("Event", back_populates="escalation_policy")

