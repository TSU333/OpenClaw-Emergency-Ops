import uuid

from sqlalchemy import Boolean, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class Contact(Base, TimestampMixin):
    __tablename__ = "contacts"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(64), default="operator", nullable=False)
    phone_number: Mapped[str | None] = mapped_column(String(64), nullable=True)
    apprise_targets: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_secondary: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    primary_policies: Mapped[list["EscalationPolicy"]] = relationship(
        "EscalationPolicy",
        foreign_keys="EscalationPolicy.primary_contact_id",
        back_populates="primary_contact",
    )
    secondary_policies: Mapped[list["EscalationPolicy"]] = relationship(
        "EscalationPolicy",
        foreign_keys="EscalationPolicy.secondary_contact_id",
        back_populates="secondary_contact",
    )

