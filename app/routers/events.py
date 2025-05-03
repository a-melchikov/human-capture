import json

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from app.lifespan import app_state

router = APIRouter(tags=["SSE"])


async def event_generator():
    while True:
        event_data = await app_state.event_queue.get()
        yield f"data: {json.dumps(event_data)}\n\n"


@router.get(
    "/events",
    summary="Server-Sent Events",
    description="Позволяет получать события о новых добавленных фотографиях через SSE (Server-Sent Events)",
    response_class=StreamingResponse,
)
async def events() -> StreamingResponse:
    return StreamingResponse(event_generator(), media_type="text/event-stream")
