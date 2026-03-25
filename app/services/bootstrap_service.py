from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.core.config import get_settings
from app.models.contact import Contact
from app.models.escalation_policy import EscalationPolicy
from app.services.audit_service import AuditService


settings = get_settings()


class BootstrapService:
    DEFAULT_POLICY_NAME = "default-emergency-ops-policy"

    def __init__(self) -> None:
        self.audit_service = AuditService()

    def ensure_default_policy(self, session: Session, source: str | None = None) -> EscalationPolicy:
        statement = (
            select(EscalationPolicy)
            .options(
                selectinload(EscalationPolicy.primary_contact),
                selectinload(EscalationPolicy.secondary_contact),
            )
            .where(EscalationPolicy.enabled.is_(True))
        )
        if source:
            source_policy = session.scalar(
                statement.where(EscalationPolicy.applies_to_source == source).limit(1)
            )
            if source_policy:
                return source_policy

        default_policy = session.scalar(
            statement.where(EscalationPolicy.name == self.DEFAULT_POLICY_NAME).limit(1)
        ) or session.scalar(statement.order_by(EscalationPolicy.created_at).limit(1))
        if default_policy:
            if default_policy.name == self.DEFAULT_POLICY_NAME:
                self._sync_default_policy(session, default_policy)
            return default_policy

        primary_contact = self._build_contact(is_secondary=False)
        session.add(primary_contact)
        session.flush()

        secondary_contact = None
        if self._has_secondary_config():
            secondary_contact = self._build_contact(is_secondary=True)
            session.add(secondary_contact)
            session.flush()

        policy = EscalationPolicy(
            name=self.DEFAULT_POLICY_NAME,
            description="Default policy for OpenClaw Emergency Ops MVP.",
            primary_contact_id=primary_contact.id,
            secondary_contact_id=secondary_contact.id if secondary_contact else None,
            first_wait_seconds=settings.escalation_first_wait_seconds,
            second_wait_seconds=settings.escalation_second_wait_seconds,
        )
        session.add(policy)
        session.flush()
        self.audit_service.record(
            session,
            action="bootstrap.default_policy_created",
            actor="system",
            details={
                "policy_id": policy.id,
                "primary_contact_id": primary_contact.id,
                "secondary_contact_id": secondary_contact.id if secondary_contact else None,
            },
        )
        return policy

    def _has_secondary_config(self) -> bool:
        return bool(
            settings.default_secondary_contact_name
            and (
                settings.default_secondary_phone_number
                or settings.default_secondary_apprise_targets
            )
        )

    def _build_contact(self, is_secondary: bool) -> Contact:
        if is_secondary:
            return Contact(
                name=settings.default_secondary_contact_name or "Secondary Operator",
                role=settings.default_secondary_contact_role,
                phone_number=settings.default_secondary_phone_number,
                apprise_targets=settings.default_secondary_apprise_targets,
                is_secondary=True,
            )
        return Contact(
            name=settings.default_primary_contact_name,
            role=settings.default_primary_contact_role,
            phone_number=settings.default_primary_phone_number,
            apprise_targets=settings.default_primary_apprise_targets,
            is_secondary=False,
        )

    def _sync_default_policy(self, session: Session, policy: EscalationPolicy) -> None:
        changed = False

        if policy.primary_contact is not None:
            changed = self._sync_contact(policy.primary_contact, is_secondary=False) or changed

        if self._has_secondary_config():
            if policy.secondary_contact is None:
                policy.secondary_contact = self._build_contact(is_secondary=True)
                session.add(policy.secondary_contact)
                session.flush()
                policy.secondary_contact_id = policy.secondary_contact.id
                changed = True
            else:
                changed = self._sync_contact(policy.secondary_contact, is_secondary=True) or changed

        if policy.first_wait_seconds != settings.escalation_first_wait_seconds:
            policy.first_wait_seconds = settings.escalation_first_wait_seconds
            changed = True
        if policy.second_wait_seconds != settings.escalation_second_wait_seconds:
            policy.second_wait_seconds = settings.escalation_second_wait_seconds
            changed = True

        if changed:
            session.flush()
            self.audit_service.record(
                session,
                action="bootstrap.default_policy_updated",
                actor="system",
                details={
                    "policy_id": policy.id,
                    "first_wait_seconds": policy.first_wait_seconds,
                    "second_wait_seconds": policy.second_wait_seconds,
                    "secondary_contact_id": policy.secondary_contact_id,
                },
            )

    def _sync_contact(self, contact: Contact, is_secondary: bool) -> bool:
        changed = False
        if is_secondary:
            desired_name = settings.default_secondary_contact_name or contact.name
            desired_role = settings.default_secondary_contact_role
            desired_phone = settings.default_secondary_phone_number
            desired_targets = settings.default_secondary_apprise_targets
        else:
            desired_name = settings.default_primary_contact_name
            desired_role = settings.default_primary_contact_role
            desired_phone = settings.default_primary_phone_number
            desired_targets = settings.default_primary_apprise_targets

        if contact.name != desired_name:
            contact.name = desired_name
            changed = True
        if contact.role != desired_role:
            contact.role = desired_role
            changed = True
        if contact.phone_number != desired_phone:
            contact.phone_number = desired_phone
            changed = True
        if contact.apprise_targets != desired_targets:
            contact.apprise_targets = desired_targets
            changed = True
        if contact.is_secondary != is_secondary:
            contact.is_secondary = is_secondary
            changed = True
        return changed
