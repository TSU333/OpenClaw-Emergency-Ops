from app.models.enums import SeverityLevel
from app.schemas.event import EventIngestRequest
from app.services.severity_engine import SeverityEngine


def test_drawdown_breach_resolves_to_critical() -> None:
    payload = EventIngestRequest(
        source="quant-engine",
        event_type="max_drawdown_breach",
        title="Max drawdown exceeded threshold",
        message="Strategy BTC_PERP_01 breached max drawdown limit",
        severity_hint="warning",
        metadata={"drawdown_pct": 8.7},
        suggested_actions=["pause_strategy", "close_positions"],
    )

    severity = SeverityEngine().determine(payload)

    assert severity == SeverityLevel.CRITICAL


def test_keyword_rule_can_raise_p0() -> None:
    payload = EventIngestRequest(
        source="infra",
        event_type="heartbeat_missing",
        title="Exchange disconnected",
        message="Potential liquidation risk due to exchange disconnected state",
        metadata={"outage_seconds": 20},
    )

    severity = SeverityEngine().determine(payload)

    assert severity == SeverityLevel.P0

