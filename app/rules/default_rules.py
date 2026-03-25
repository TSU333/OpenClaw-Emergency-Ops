from app.models.enums import SeverityLevel


TRADING_ACTIONS = ["pause_strategy", "close_positions"]
SERVICE_ACTIONS = ["restart_service"]


def resolve_rule_severity(event_type: str, metadata: dict) -> SeverityLevel | None:
    event_type = event_type.lower()

    risk_score = float(metadata.get("risk_score", 0) or 0)
    if risk_score >= 90:
        return SeverityLevel.P0
    if risk_score >= 75:
        return SeverityLevel.CRITICAL
    if risk_score >= 50:
        return SeverityLevel.WARNING

    if event_type == "max_drawdown_breach":
        drawdown = float(metadata.get("drawdown_pct", 0) or 0)
        if drawdown >= 12:
            return SeverityLevel.P0
        if drawdown >= 8:
            return SeverityLevel.CRITICAL
        if drawdown >= 4:
            return SeverityLevel.WARNING
        return SeverityLevel.INFO

    if event_type in {"service_down", "heartbeat_missing"}:
        outage_seconds = float(
            metadata.get("outage_seconds", metadata.get("unavailable_seconds", 0)) or 0
        )
        if outage_seconds >= 600:
            return SeverityLevel.P0
        if outage_seconds >= 180:
            return SeverityLevel.CRITICAL
        if outage_seconds >= 30:
            return SeverityLevel.WARNING
        return SeverityLevel.INFO

    if event_type in {"latency_spike", "error_rate_breach", "order_reject_spike"}:
        error_rate = float(metadata.get("error_rate", 0) or 0)
        latency_ms = float(metadata.get("latency_ms", 0) or 0)
        if error_rate >= 20 or latency_ms >= 5_000:
            return SeverityLevel.CRITICAL
        if error_rate >= 5 or latency_ms >= 1_500:
            return SeverityLevel.WARNING
        return SeverityLevel.INFO

    if event_type in {"liquidation_risk", "margin_call"}:
        return SeverityLevel.P0

    return None


def keyword_severity(title: str, message: str) -> SeverityLevel | None:
    combined = f"{title} {message}".lower()
    if any(token in combined for token in ("liquidation", "all positions", "exchange disconnected")):
        return SeverityLevel.P0
    if any(token in combined for token in ("drawdown", "service unavailable", "failed repeatedly")):
        return SeverityLevel.CRITICAL
    if any(token in combined for token in ("warning", "degraded", "slow")):
        return SeverityLevel.WARNING
    return None


def default_actions_for(event_type: str, severity: SeverityLevel) -> list[str]:
    event_type = event_type.lower()
    if event_type in {"max_drawdown_breach", "liquidation_risk", "margin_call"}:
        return TRADING_ACTIONS.copy()
    if event_type in {"service_down", "heartbeat_missing"}:
        return SERVICE_ACTIONS.copy()
    if severity in {SeverityLevel.CRITICAL, SeverityLevel.P0}:
        return ["pause_strategy"]
    return []

