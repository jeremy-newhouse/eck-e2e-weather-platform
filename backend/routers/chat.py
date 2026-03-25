"""Chat router — POST /api/chat endpoint."""

from fastapi import APIRouter, Request

from backend.schemas.api import ChatRequest, ChatResponse
from backend.services import chat_service

router = APIRouter(tags=["chat"])


@router.post("/chat", response_model=ChatResponse)
async def chat(request_data: ChatRequest, request: Request) -> ChatResponse:
    """Send a message to the weather assistant and receive a reply.

    Args:
        request_data: Chat request body containing session_id, message, and city.
        request: FastAPI request used to access shared app-state clients.

    Returns:
        :class:`ChatResponse` with the assistant reply and session metadata.
    """
    return await chat_service.chat(request_data, request)
