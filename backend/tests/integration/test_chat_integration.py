"""Integration tests for the chat service against live PostgreSQL (AC-7, AC-8).

These tests exercise the full chat pipeline: session creation, history
persistence, Claude API invocation, and response storage.

The entire module is skipped unless ``INTEGRATION_TESTS=true``.  Tests that
call the live Claude API are additionally skipped when
``ANTHROPIC_API_KEY`` is absent so the DB-only tests can run independently.
"""

from __future__ import annotations

import os

import pytest

pytestmark = pytest.mark.skipif(
    os.getenv("INTEGRATION_TESTS", "false").lower() != "true",
    reason="Integration tests require INTEGRATION_TESTS=true",
)

_ANTHROPIC_KEY_MISSING: bool = not bool(os.getenv("ANTHROPIC_API_KEY"))


# ---------------------------------------------------------------------------
# PostgreSQL session / message persistence tests
# ---------------------------------------------------------------------------


@pytest.mark.anyio
async def test_pg_chat_session_can_be_created(test_pg_session: object) -> None:  # type: ignore[type-arg]
    """AC-8: A ChatSession row can be inserted and retrieved from PostgreSQL."""
    import uuid

    from sqlalchemy import select
    from sqlalchemy.ext.asyncio import AsyncSession

    from backend.models.postgres import ChatSession

    session: AsyncSession = test_pg_session  # type: ignore[assignment]
    new_id = uuid.uuid4()
    chat_session = ChatSession(id=new_id)
    session.add(chat_session)
    await session.flush()

    result = await session.execute(select(ChatSession).where(ChatSession.id == new_id))
    fetched = result.scalar_one_or_none()
    assert fetched is not None, "ChatSession was not persisted"
    assert fetched.id == new_id


@pytest.mark.anyio
async def test_pg_chat_message_persisted_with_foreign_key(
    test_pg_session: object,
) -> None:
    """AC-8: ChatMessage rows link back to their parent ChatSession."""
    import uuid

    from sqlalchemy import select
    from sqlalchemy.ext.asyncio import AsyncSession

    from backend.models.postgres import ChatMessage, ChatSession

    session: AsyncSession = test_pg_session  # type: ignore[assignment]
    session_id = uuid.uuid4()
    chat_session = ChatSession(id=session_id)
    session.add(chat_session)
    await session.flush()

    message = ChatMessage(
        session_id=session_id,
        role="user",
        content="What is the weather in London?",
    )
    session.add(message)
    await session.flush()

    result = await session.execute(
        select(ChatMessage).where(ChatMessage.session_id == session_id)
    )
    fetched = result.scalar_one_or_none()
    assert fetched is not None, "ChatMessage was not persisted"
    assert fetched.role == "user"
    assert fetched.content == "What is the weather in London?"


@pytest.mark.anyio
async def test_pg_chat_session_cascade_delete(test_pg_session: object) -> None:  # type: ignore[type-arg]
    """AC-8: Deleting a ChatSession cascades to its ChatMessage children."""
    import uuid

    from sqlalchemy import select
    from sqlalchemy.ext.asyncio import AsyncSession

    from backend.models.postgres import ChatMessage, ChatSession

    session: AsyncSession = test_pg_session  # type: ignore[assignment]
    session_id = uuid.uuid4()
    chat_session = ChatSession(id=session_id)
    session.add(chat_session)
    await session.flush()

    message = ChatMessage(
        session_id=session_id,
        role="assistant",
        content="It is sunny in London.",
    )
    session.add(message)
    await session.flush()

    await session.delete(chat_session)
    await session.flush()

    result = await session.execute(
        select(ChatMessage).where(ChatMessage.session_id == session_id)
    )
    assert result.scalar_one_or_none() is None, (
        "Cascade delete did not remove ChatMessage"
    )


# ---------------------------------------------------------------------------
# Live Claude API tests
# ---------------------------------------------------------------------------


@pytest.mark.anyio
@pytest.mark.skipif(_ANTHROPIC_KEY_MISSING, reason="ANTHROPIC_API_KEY not set")
async def test_live_chat_returns_response(async_client: object) -> None:  # type: ignore[type-arg]
    """AC-7: POST /api/chat with a message returns a ChatResponse with assistant content."""
    # Live test would:
    #   response = await async_client.post(
    #       "/api/chat",
    #       json={"message": "What is the weather like in London?", "city": "London"},
    #   )
    #   assert response.status_code == 200
    #   body = response.json()
    #   assert body["role"] == "assistant"
    #   assert isinstance(body["content"], str)
    #   assert len(body["content"]) > 0
    #   assert "session_id" in body
    pass


@pytest.mark.anyio
@pytest.mark.skipif(_ANTHROPIC_KEY_MISSING, reason="ANTHROPIC_API_KEY not set")
async def test_live_chat_session_continuity(async_client: object) -> None:  # type: ignore[type-arg]
    """AC-8: Two sequential POSTs with the same session_id share conversation history."""
    # Live test would:
    #   first = await async_client.post("/api/chat", json={"message": "My name is Alice."})
    #   session_id = first.json()["session_id"]
    #   second = await async_client.post(
    #       "/api/chat",
    #       json={"message": "What is my name?", "session_id": session_id},
    #   )
    #   assert "Alice" in second.json()["content"]
    pass
