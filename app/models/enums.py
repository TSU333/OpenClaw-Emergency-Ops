from enum import StrEnum


class SeverityLevel(StrEnum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    P0 = "p0"


class EventStatus(StrEnum):
    OPEN = "open"
    ACKNOWLEDGED = "acknowledged"
    SNOOZED = "snoozed"
    RESOLVED = "resolved"


class NotificationChannel(StrEnum):
    APPRISE = "apprise"
    SMS_FALLBACK = "sms_fallback"
    VOICE_CALL = "voice_call"


class NotificationStatus(StrEnum):
    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"
    SKIPPED = "skipped"


class AcknowledgementAction(StrEnum):
    ACKNOWLEDGE = "acknowledge"
    SNOOZE = "snooze"


class ActionStatus(StrEnum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"


SEVERITY_RANK = {
    SeverityLevel.INFO: 0,
    SeverityLevel.WARNING: 1,
    SeverityLevel.CRITICAL: 2,
    SeverityLevel.P0: 3,
}


def coerce_severity(value: str | SeverityLevel | None) -> SeverityLevel | None:
    if value is None:
        return None
    if isinstance(value, SeverityLevel):
        return value
    normalized = value.strip().lower()
    for severity in SeverityLevel:
        if severity.value == normalized:
            return severity
    return None


def max_severity(
    left: SeverityLevel | None,
    right: SeverityLevel | None,
) -> SeverityLevel | None:
    if left is None:
        return right
    if right is None:
        return left
    return left if SEVERITY_RANK[left] >= SEVERITY_RANK[right] else right

