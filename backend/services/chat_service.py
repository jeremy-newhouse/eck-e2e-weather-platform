"""Chat service — Claude API calls with PostgreSQL persistence."""

from datetime import datetime, timezone
from typing import Optional
import uuid

from fastapi import Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.postgres import ChatMessage, ChatSession
from backend.schemas.api import ChatRequest, ChatResponse


async def chat(request_data: ChatRequest, request: Request) -> ChatResponse:
    """Process a chat message: load history, call Claude, persist messages.

    Args:
        request_data: Validated request containing session_id, message, and city.
        request: FastAPI request carrying ``app.state.pg_session_factory`` and
            ``app.state.anthropic_client``.

    Returns:
        :class:`ChatResponse` with the assistant reply and session metadata.
    """
    pg_session_factory = request.app.state.pg_session_factory
    anthropic_client = request.app.state.anthropic_client

    async with pg_session_factory() as session:
        # Resolve or create session
        db_session = await _get_or_create_session(request_data.session_id, session)

        # Load message history
        result = await session.execute(
            select(ChatMessage)
            .where(ChatMessage.session_id == db_session.id)
            .order_by(ChatMessage.created_at.asc())
        )
        history = result.scalars().all()
        messages = [{"role": m.role, "content": m.content} for m in history]

        # Fetch weather context
        city = request_data.city or "London"
        weather_context = await _get_weather_context(city, request)

        system_prompt = (
            f"You are a helpful weather assistant.\n"
            f"Current weather in {weather_context['city']}: "
            f"{weather_context['temperature']:.1f}°C, "
            f"{weather_context['description']}, "
            f"humidity {weather_context['humidity']:.0f}%, "
            f"wind {weather_context['wind_speed']:.1f} m/s."
        )

        # Append current user message
        messages.append({"role": "user", "content": request_data.message})

        # Claude API call
        response = await anthropic_client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=1024,
            system=system_prompt,
            messages=messages,
        )
        assistant_content: str = response.content[0].text

        # Persist user + assistant messages
        now = datetime.now(tz=timezone.utc)
        session.add_all(
            [
                ChatMessage(
                    session_id=db_session.id,
                    role="user",
                    content=request_data.message,
                    created_at=now,
                ),
                ChatMessage(
                    session_id=db_session.id,
                    role="assistant",
                    content=assistant_content,
                    created_at=now,
                ),
            ]
        )
        await session.commit()

        return ChatResponse(
            session_id=str(db_session.id),
            role="assistant",
            content=assistant_content,
            created_at=now,
        )


async def _get_or_create_session(
    session_id: Optional[str], db_session: AsyncSession
) -> ChatSession:
    """Look up an existing session by UUID or create a new one.

    Args:
        session_id: Optional UUID string provided by the client.
        db_session: Open SQLAlchemy async session.

    Returns:
        Existing or newly-created :class:`ChatSession`.
    """
    if session_id:
        try:
            sid = uuid.UUID(session_id)
            result = await db_session.execute(
                select(ChatSession).where(ChatSession.id == sid)
            )
            existing = result.scalar_one_or_none()
            if existing:
                return existing
        except (ValueError, Exception):
            pass

    # Create new session
    new_session = ChatSession()
    db_session.add(new_session)
    await db_session.flush()  # Assign PK without committing
    return new_session


async def _get_weather_context(city: str, request: Request) -> dict[str, object]:
    """Fetch current weather for use in the system prompt.

    Falls back to zero-value defaults when the weather service is unavailable,
    so the chat endpoint continues to work independently.

    Args:
        city: City name to look up.
        request: FastAPI request forwarded to the weather service.

    Returns:
        Dict with keys city, temperature, humidity, wind_speed, description.
    """
    try:
        from backend.services.weather_service import get_weather  # noqa: PLC0415

        weather = await get_weather(city, request)
        return {
            "city": weather.city,
            "temperature": weather.temperature,
            "humidity": weather.humidity,
            "wind_speed": weather.wind_speed,
            "description": weather.description,
        }
    except Exception:
        # Graceful fallback so chat still works even if weather is unavailable
        return {
            "city": city,
            "temperature": 0.0,
            "humidity": 0.0,
            "wind_speed": 0.0,
            "description": "unavailable",
        }
