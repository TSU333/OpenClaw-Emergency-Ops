from app.core.celery_app import celery_app
from app.core.database import session_scope
from app.services.escalation_engine import EscalationEngine


@celery_app.task(name="app.workers.tasks.process_first_escalation")
def process_first_escalation_task(event_id: str) -> bool:
    with session_scope() as session:
        engine = EscalationEngine()
        return engine.process_first_escalation(session, event_id)


@celery_app.task(name="app.workers.tasks.process_second_contact")
def process_second_contact_task(event_id: str) -> bool:
    with session_scope() as session:
        engine = EscalationEngine()
        return engine.process_second_contact(session, event_id)

