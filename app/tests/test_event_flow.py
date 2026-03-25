from app.models.notification import Notification
from app.services.escalation_engine import EscalationEngine


SAMPLE_EVENT = {
    "source": "quant-engine",
    "event_type": "max_drawdown_breach",
    "title": "Max drawdown exceeded threshold",
    "message": "Strategy BTC_PERP_01 breached max drawdown limit",
    "severity_hint": "critical",
    "metadata": {
        "strategy_id": "BTC_PERP_01",
        "exchange": "Binance",
        "drawdown_pct": 8.7,
        "pnl": -1240.55,
    },
    "suggested_actions": ["pause_strategy", "close_positions"],
}


def test_ingest_event_generates_summary_and_timeline(client) -> None:
    response = client.post("/api/v1/events/ingest", json=SAMPLE_EVENT)

    assert response.status_code == 201
    payload = response.json()
    assert payload["severity"] == "critical"
    assert payload["ai_summary"]["recommend_immediate_stop_loss"] is True
    assert "strategy_id=BTC_PERP_01" in payload["ai_summary"]["impact_scope"]

    timeline = client.get(f"/api/v1/events/{payload['id']}/timeline")
    assert timeline.status_code == 200
    actions = [item["action"] for item in timeline.json()["timeline"]]
    assert "event.ingested" in actions
    assert "notification.dispatched" in actions
    assert "escalation.initialized" in actions


def test_post_events_alias_ingests_event(client) -> None:
    response = client.post("/api/v1/events", json=SAMPLE_EVENT)

    assert response.status_code == 201
    payload = response.json()
    assert payload["severity"] == "critical"
    assert payload["source"] == SAMPLE_EVENT["source"]


def test_acknowledged_event_will_not_escalate(client, db_session) -> None:
    response = client.post("/api/v1/events/ingest", json=SAMPLE_EVENT)
    event_id = response.json()["id"]

    ack = client.post(
        f"/api/v1/events/{event_id}/acknowledge",
        json={"actor": "alice", "note": "Taking ownership"},
    )
    assert ack.status_code == 200
    assert ack.json()["status"] == "acknowledged"

    initial_count = db_session.query(Notification).filter(Notification.event_id == event_id).count()
    escalated = EscalationEngine().process_first_escalation(db_session, event_id)
    post_count = db_session.query(Notification).filter(Notification.event_id == event_id).count()

    assert escalated is False
    assert initial_count == post_count
