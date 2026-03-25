from app.models.enums import SeverityLevel
from app.rules.default_rules import default_actions_for
from app.schemas.common import AISummary
from app.schemas.event import EventIngestRequest


class SummaryService:
    RISK_LABELS = {
        SeverityLevel.INFO: "Low urgency. Monitor the signal and confirm whether it is transient.",
        SeverityLevel.WARNING: "Elevated risk. A human should review the event before it worsens.",
        SeverityLevel.CRITICAL: "High risk. Trading or service impact is plausible and rapid intervention is recommended.",
        SeverityLevel.P0: "Immediate risk. Potential capital loss or infrastructure outage requires urgent human response.",
    }

    def generate(
        self,
        payload: EventIngestRequest,
        severity: SeverityLevel,
    ) -> AISummary:
        impact_parts = []
        for key in ("strategy_id", "exchange", "service_name", "host", "region"):
            if payload.metadata.get(key):
                impact_parts.append(f"{key}={payload.metadata[key]}")
        impact_scope = ", ".join(impact_parts) if impact_parts else "Scope not explicitly provided."

        recommended_actions = payload.suggested_actions or default_actions_for(
            payload.event_type,
            severity,
        )
        recommend_stop_loss = severity in {SeverityLevel.CRITICAL, SeverityLevel.P0} and any(
            action in {"pause_strategy", "close_positions"} for action in recommended_actions
        )

        what_happened = (
            f"{payload.source} emitted {payload.event_type}: {payload.title}. "
            f"{payload.message}"
        )
        operator_brief = (
            f"Severity={severity.value}; "
            f"impact={impact_scope}; "
            f"actions={', '.join(recommended_actions) or 'manual review'}."
        )
        return AISummary(
            what_happened=what_happened,
            impact_scope=impact_scope,
            current_risk=self.RISK_LABELS[severity],
            recommended_actions=recommended_actions,
            recommend_immediate_stop_loss=recommend_stop_loss,
            operator_brief=operator_brief,
        )

