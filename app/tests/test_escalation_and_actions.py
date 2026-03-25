from app.models.event import Event
from app.workers.tasks import process_second_contact_task


def test_second_contact_task_persists_notifications_timeline_and_level(client) -> None:
    response = client.post(
        "/api/v1/events/ingest",
        json={
            "source": "quant-engine",
            "event_type": "liquidation_risk",
            "title": "Liquidation risk rising",
            "message": "All positions are close to maintenance margin.",
            "severity_hint": "p0",
            "metadata": {"strategy_id": "BTC_PERP_01", "exchange": "Binance"},
            "suggested_actions": ["pause_strategy", "close_positions"],
        },
    )
    event_id = response.json()["id"]

    escalated = process_second_contact_task(event_id)
    assert escalated is True

    detail = client.get(f"/api/v1/events/{event_id}")
    assert detail.status_code == 200
    payload = detail.json()

    assert payload["escalation_level"] == 2
    assert any(
        notification["escalation_step"] == 2 and "+61000000001" in (notification["target"] or "")
        for notification in payload["notifications"]
    )
    assert "escalation.second_triggered" in [item["action"] for item in payload["timeline"]]
    assert any(
        item["action"] == "notification.dispatched"
        and item["details"]["stage"] == "second_contact"
        for item in payload["timeline"]
    )
    timeline = client.get(f"/api/v1/events/{event_id}/timeline")
    assert timeline.status_code == 200
    assert "escalation.second_triggered" in [item["action"] for item in timeline.json()["timeline"]]


def test_second_contact_skip_writes_explicit_timeline_reason(client, db_session) -> None:
    response = client.post(
        "/api/v1/events/ingest",
        json={
            "source": "quant-engine",
            "event_type": "liquidation_risk",
            "title": "Secondary contact missing",
            "message": "This case should be skipped with an explicit audit record.",
            "severity_hint": "p0",
            "metadata": {"strategy_id": "ETH_PERP_01", "exchange": "Binance"},
            "suggested_actions": ["pause_strategy", "close_positions"],
        },
    )
    event_id = response.json()["id"]

    event = db_session.get(Event, event_id)
    assert event is not None
    event.escalation_policy.secondary_contact_id = None
    event.escalation_policy.secondary_contact = None
    db_session.commit()

    escalated = process_second_contact_task(event_id)
    assert escalated is False

    detail = client.get(f"/api/v1/events/{event_id}")
    assert detail.status_code == 200
    payload = detail.json()

    assert payload["escalation_level"] == 0
    assert not any(notification["escalation_step"] == 2 for notification in payload["notifications"])
    skipped_entries = [item for item in payload["timeline"] if item["action"] == "escalation.second_skipped"]
    assert skipped_entries
    assert skipped_entries[-1]["details"]["reason"] == "missing_secondary_contact"
    timeline = client.get(f"/api/v1/events/{event_id}/timeline")
    assert timeline.status_code == 200
    assert any(item["action"] == "escalation.second_skipped" for item in timeline.json()["timeline"])


def test_restart_service_action_runs_in_dry_run_mode(client) -> None:
    response = client.post(
        "/api/v1/events/manual",
        json={
            "source": "crawler-runtime",
            "event_type": "service_down",
            "title": "Crawler service unavailable",
            "message": "crawler-daemon has been unreachable for 200 seconds",
            "severity_hint": "warning",
            "metadata": {"service_name": "crawler-daemon", "outage_seconds": 200},
            "suggested_actions": ["restart_service"],
        },
    )
    event_id = response.json()["id"]

    action = client.post(
        f"/api/v1/events/{event_id}/actions/restart_service",
        json={"actor": "operator", "parameters": {"reason": "auto-remediation"}},
    )
    assert action.status_code == 200
    payload = action.json()
    assert payload["status"] == "succeeded"
    assert payload["result_payload"]["mode"] == "dry_run"

    detail = client.get(f"/api/v1/events/{event_id}")
    assert detail.status_code == 200
    detail_payload = detail.json()
    assert any(action_run["action_name"] == "restart_service" for action_run in detail_payload["action_runs"])
    assert any(item["action"] == "action.completed" for item in detail_payload["timeline"])

    timeline = client.get(f"/api/v1/events/{event_id}/timeline")
    assert timeline.status_code == 200
    assert any(item["action"] == "action.completed" for item in timeline.json()["timeline"])
