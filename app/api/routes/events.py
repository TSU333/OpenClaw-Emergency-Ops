from fastapi import APIRouter

from app.core.deps import SessionDep
from app.schemas.acknowledgement import AcknowledgeRequest, SnoozeRequest
from app.schemas.action import ActionRunRequest, ActionRunResponse
from app.schemas.event import (
    EventDetailResponse,
    EventIngestRequest,
    EventResponse,
    EventTimelineResponse,
    build_event_detail_response,
    build_event_response,
)
from app.services.action_executor import ActionExecutor
from app.services.event_service import EventService
from app.services.timeline_service import TimelineService


router = APIRouter()
event_service = EventService()
timeline_service = TimelineService()
action_executor = ActionExecutor()


def _ingest_event(payload: EventIngestRequest, session: SessionDep) -> EventResponse:
    event = event_service.ingest(session, payload)
    return build_event_response(event)


@router.post("", response_model=EventResponse, status_code=201)
def ingest_event_alias(payload: EventIngestRequest, session: SessionDep) -> EventResponse:
    return _ingest_event(payload, session)


@router.post("/ingest", response_model=EventResponse, status_code=201)
def ingest_event(payload: EventIngestRequest, session: SessionDep) -> EventResponse:
    return _ingest_event(payload, session)


@router.post("/manual", response_model=EventResponse, status_code=201)
def create_event(payload: EventIngestRequest, session: SessionDep) -> EventResponse:
    event = event_service.ingest(session, payload)
    return build_event_response(event)


@router.get("", response_model=list[EventResponse])
def list_events(session: SessionDep) -> list[EventResponse]:
    return [build_event_response(event) for event in event_service.list_events(session)]


@router.get("/{event_id}", response_model=EventDetailResponse)
def get_event(event_id: str, session: SessionDep) -> EventDetailResponse:
    event = event_service.get_or_404(session, event_id)
    return build_event_detail_response(event)


@router.get("/{event_id}/timeline", response_model=EventTimelineResponse)
def get_event_timeline(event_id: str, session: SessionDep) -> EventTimelineResponse:
    timeline = timeline_service.list_for_event(session, event_id)
    return EventTimelineResponse(event_id=event_id, timeline=timeline)


@router.post("/{event_id}/acknowledge", response_model=EventResponse)
def acknowledge_event(
    event_id: str,
    payload: AcknowledgeRequest,
    session: SessionDep,
) -> EventResponse:
    event = event_service.acknowledge(session, event_id, payload)
    return build_event_response(event)


@router.post("/{event_id}/snooze", response_model=EventResponse)
def snooze_event(
    event_id: str,
    payload: SnoozeRequest,
    session: SessionDep,
) -> EventResponse:
    event = event_service.snooze(session, event_id, payload)
    return build_event_response(event)


@router.post("/{event_id}/actions/{action_name}", response_model=ActionRunResponse)
def execute_action(
    event_id: str,
    action_name: str,
    payload: ActionRunRequest,
    session: SessionDep,
) -> ActionRunResponse:
    event = event_service.get_or_404(session, event_id)
    action_run = action_executor.execute(
        session=session,
        event=event,
        action_name=action_name,
        actor=payload.actor,
        parameters=payload.parameters,
    )
    return ActionRunResponse.model_validate(action_run)
