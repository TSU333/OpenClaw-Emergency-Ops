from app.models.enums import SeverityLevel, coerce_severity, max_severity
from app.rules.default_rules import keyword_severity, resolve_rule_severity
from app.schemas.event import EventIngestRequest


class SeverityEngine:
    def determine(self, payload: EventIngestRequest) -> SeverityLevel:
        hint = coerce_severity(payload.severity_hint)
        rule = resolve_rule_severity(payload.event_type, payload.metadata)
        keyword = keyword_severity(payload.title, payload.message)
        severity = max_severity(max_severity(hint, rule), keyword)
        return severity or SeverityLevel.INFO

