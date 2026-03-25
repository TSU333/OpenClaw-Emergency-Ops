from app.services.bootstrap_service import BootstrapService, settings as bootstrap_settings


def test_default_policy_waits_sync_from_settings(db_session, monkeypatch) -> None:
    monkeypatch.setattr(bootstrap_settings, "escalation_first_wait_seconds", 10)
    monkeypatch.setattr(bootstrap_settings, "escalation_second_wait_seconds", 20)

    policy = BootstrapService().ensure_default_policy(db_session)
    db_session.commit()

    assert policy.first_wait_seconds == 10
    assert policy.second_wait_seconds == 20
