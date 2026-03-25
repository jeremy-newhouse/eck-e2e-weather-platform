"""Tests for the chat service (AC-7, AC-8)."""

from datetime import datetime, timezone
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch
import uuid

import pytest
from fastapi import FastAPI, Request

from backend.schemas.api import ChatRequest, ChatResponse
from backend.services import chat_service


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_anthropic_response(text: str) -> MagicMock:
    """Build a minimal fake Anthropic messages.create response."""
    content_block = MagicMock()
    content_block.text = text
    response = MagicMock()
    response.content = [content_block]
    return response


def _make_chat_message(role: str, content: str, session_id: uuid.UUID) -> MagicMock:
    """Build a minimal fake ChatMessage ORM object."""
    msg = MagicMock()
    msg.role = role
    msg.content = content
    msg.session_id = session_id
    msg.created_at = datetime(2026, 3, 25, 12, 0, 0, tzinfo=timezone.utc)
    return msg


def _make_chat_session(session_id: uuid.UUID | None = None) -> MagicMock:
    """Build a minimal fake ChatSession ORM object."""
    sess = MagicMock()
    sess.id = session_id or uuid.uuid4()
    return sess


def _make_request(pg_session_factory: Any, anthropic_client: Any) -> Request:
    """Build a FastAPI Request whose app.state carries the two clients."""
    app = FastAPI()
    app.state.pg_session_factory = pg_session_factory
    app.state.anthropic_client = anthropic_client
    scope = {
        "type": "http",
        "method": "POST",
        "path": "/api/chat",
        "query_string": b"",
        "headers": [],
        "app": app,
    }
    return Request(scope)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def anthropic_client() -> MagicMock:
    client = MagicMock()
    client.messages = MagicMock()
    client.messages.create = AsyncMock(
        return_value=_make_anthropic_response("Looks sunny today!")
    )
    return client


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestGetOrCreateSession:
    """Unit tests for _get_or_create_session (AC-8)."""

    async def test_creates_new_session_when_session_id_is_none(self) -> None:
        """A new ChatSession is persisted when no session_id is provided."""
        new_session = _make_chat_session()
        db_session = MagicMock()
        db_session.execute = AsyncMock(
            return_value=MagicMock(scalar_one_or_none=MagicMock(return_value=None))
        )
        db_session.flush = AsyncMock()
        db_session.add = MagicMock()

        with patch(
            "backend.services.chat_service.ChatSession", return_value=new_session
        ):
            result = await chat_service._get_or_create_session(None, db_session)

        db_session.add.assert_called_once_with(new_session)
        db_session.flush.assert_awaited_once()
        assert result is new_session

    async def test_creates_new_session_when_session_id_invalid_uuid(self) -> None:
        """A new session is created when session_id is not a valid UUID."""
        new_session = _make_chat_session()
        db_session = MagicMock()
        db_session.flush = AsyncMock()
        db_session.add = MagicMock()

        with patch(
            "backend.services.chat_service.ChatSession", return_value=new_session
        ):
            result = await chat_service._get_or_create_session("not-a-uuid", db_session)

        db_session.add.assert_called_once_with(new_session)
        assert result is new_session

    async def test_returns_existing_session_when_found(self) -> None:
        """Existing ChatSession is returned when session_id matches a DB row."""
        existing_id = uuid.uuid4()
        existing_session = _make_chat_session(existing_id)

        scalar_result = MagicMock()
        scalar_result.scalar_one_or_none = MagicMock(return_value=existing_session)
        db_session = MagicMock()
        db_session.execute = AsyncMock(return_value=scalar_result)

        result = await chat_service._get_or_create_session(str(existing_id), db_session)

        assert result is existing_session
        db_session.add.assert_not_called()

    async def test_creates_new_session_when_uuid_not_in_db(self) -> None:
        """New session is created when UUID is valid but not found in DB."""
        new_session = _make_chat_session()
        unknown_id = uuid.uuid4()

        scalar_result = MagicMock()
        scalar_result.scalar_one_or_none = MagicMock(return_value=None)
        db_session = MagicMock()
        db_session.execute = AsyncMock(return_value=scalar_result)
        db_session.flush = AsyncMock()
        db_session.add = MagicMock()

        with patch(
            "backend.services.chat_service.ChatSession", return_value=new_session
        ):
            result = await chat_service._get_or_create_session(
                str(unknown_id), db_session
            )

        db_session.add.assert_called_once_with(new_session)
        assert result is new_session


class TestChatService:
    """Integration-style tests for chat() (AC-7, AC-8)."""

    def _make_pg_session_factory(
        self,
        db_session_mock: MagicMock,
    ) -> MagicMock:
        """Return a factory whose async context manager yields db_session_mock."""
        cm = MagicMock()
        cm.__aenter__ = AsyncMock(return_value=db_session_mock)
        cm.__aexit__ = AsyncMock(return_value=False)
        factory = MagicMock(return_value=cm)
        return factory

    def _make_db_session(
        self,
        chat_session: MagicMock,
        history: list[MagicMock],
    ) -> MagicMock:
        """Build a db_session mock that handles execute/add_all/commit."""
        session_scalar_result = MagicMock()
        session_scalar_result.scalar_one_or_none = MagicMock(return_value=chat_session)

        history_scalars = MagicMock()
        history_scalars.scalars = MagicMock(
            return_value=MagicMock(all=MagicMock(return_value=history))
        )

        # First execute() call → session lookup; second → history query
        db_session = MagicMock()
        db_session.execute = AsyncMock(
            side_effect=[session_scalar_result, history_scalars]
        )
        db_session.add = MagicMock()
        db_session.add_all = MagicMock()
        db_session.flush = AsyncMock()
        db_session.commit = AsyncMock()
        return db_session

    async def test_new_session_created_when_no_session_id(
        self, anthropic_client: MagicMock
    ) -> None:
        """AC-8: A new ChatSession is created when session_id is None."""
        new_session = _make_chat_session()
        new_session_for_create = _make_chat_session(new_session.id)

        # db_session: first execute returns None (session not found), second returns empty history
        none_result = MagicMock()
        none_result.scalar_one_or_none = MagicMock(return_value=None)

        history_result = MagicMock()
        history_result.scalars = MagicMock(
            return_value=MagicMock(all=MagicMock(return_value=[]))
        )

        db_session = MagicMock()
        db_session.execute = AsyncMock(side_effect=[none_result, history_result])
        db_session.add = MagicMock()
        db_session.add_all = MagicMock()
        db_session.flush = AsyncMock()
        db_session.commit = AsyncMock()

        factory = self._make_pg_session_factory(db_session)
        request = _make_request(factory, anthropic_client)
        request_data = ChatRequest(message="Hello")

        with (
            patch(
                "backend.services.chat_service.ChatSession",
                return_value=new_session_for_create,
            ),
            patch(
                "backend.services.chat_service._get_weather_context",
                new=AsyncMock(
                    return_value={
                        "city": "London",
                        "temperature": 15.0,
                        "humidity": 70.0,
                        "wind_speed": 3.0,
                        "description": "Cloudy",
                    }
                ),
            ),
        ):
            response = await chat_service.chat(request_data, request)

        db_session.add.assert_called()
        db_session.flush.assert_awaited()
        assert isinstance(response, ChatResponse)

    async def test_existing_session_loaded_when_session_id_provided(
        self, anthropic_client: MagicMock
    ) -> None:
        """AC-8: Existing ChatSession is loaded when a valid session_id is passed."""
        existing_id = uuid.uuid4()
        existing_session = _make_chat_session(existing_id)

        session_result = MagicMock()
        session_result.scalar_one_or_none = MagicMock(return_value=existing_session)

        history_result = MagicMock()
        history_result.scalars = MagicMock(
            return_value=MagicMock(all=MagicMock(return_value=[]))
        )

        db_session = MagicMock()
        db_session.execute = AsyncMock(side_effect=[session_result, history_result])
        db_session.add = MagicMock()
        db_session.add_all = MagicMock()
        db_session.flush = AsyncMock()
        db_session.commit = AsyncMock()

        factory = self._make_pg_session_factory(db_session)
        request = _make_request(factory, anthropic_client)
        request_data = ChatRequest(session_id=str(existing_id), message="Hi again")

        with patch(
            "backend.services.chat_service._get_weather_context",
            new=AsyncMock(
                return_value={
                    "city": "Paris",
                    "temperature": 10.0,
                    "humidity": 60.0,
                    "wind_speed": 2.0,
                    "description": "Clear",
                }
            ),
        ):
            response = await chat_service.chat(request_data, request)

        # add() was NOT called for a new session (existing session was reused)
        db_session.add.assert_not_called()
        assert response.session_id == str(existing_id)

    async def test_chat_history_passed_to_claude(
        self, anthropic_client: MagicMock
    ) -> None:
        """AC-7: Prior messages are loaded from DB and forwarded to Claude."""
        session_id = uuid.uuid4()
        existing_session = _make_chat_session(session_id)

        prior_user = _make_chat_message("user", "What's the weather?", session_id)
        prior_assistant = _make_chat_message("assistant", "It's sunny!", session_id)

        session_result = MagicMock()
        session_result.scalar_one_or_none = MagicMock(return_value=existing_session)

        history_result = MagicMock()
        history_result.scalars = MagicMock(
            return_value=MagicMock(
                all=MagicMock(return_value=[prior_user, prior_assistant])
            )
        )

        db_session = MagicMock()
        db_session.execute = AsyncMock(side_effect=[session_result, history_result])
        db_session.add = MagicMock()
        db_session.add_all = MagicMock()
        db_session.flush = AsyncMock()
        db_session.commit = AsyncMock()

        factory = self._make_pg_session_factory(db_session)
        request = _make_request(factory, anthropic_client)
        request_data = ChatRequest(
            session_id=str(session_id), message="Should I bring an umbrella?"
        )

        with patch(
            "backend.services.chat_service._get_weather_context",
            new=AsyncMock(
                return_value={
                    "city": "London",
                    "temperature": 12.0,
                    "humidity": 85.0,
                    "wind_speed": 5.0,
                    "description": "Rainy",
                }
            ),
        ):
            await chat_service.chat(request_data, request)

        call_args = anthropic_client.messages.create.call_args
        messages_sent = call_args.kwargs["messages"]

        # History (2) + current user message (1) = 3
        assert len(messages_sent) == 3
        assert messages_sent[0] == {"role": "user", "content": "What's the weather?"}
        assert messages_sent[1] == {"role": "assistant", "content": "It's sunny!"}
        assert messages_sent[2] == {
            "role": "user",
            "content": "Should I bring an umbrella?",
        }

    async def test_assistant_response_persisted(
        self, anthropic_client: MagicMock
    ) -> None:
        """AC-8: Both user and assistant messages are written to chat_messages."""
        session_id = uuid.uuid4()
        existing_session = _make_chat_session(session_id)

        session_result = MagicMock()
        session_result.scalar_one_or_none = MagicMock(return_value=existing_session)

        history_result = MagicMock()
        history_result.scalars = MagicMock(
            return_value=MagicMock(all=MagicMock(return_value=[]))
        )

        db_session = MagicMock()
        db_session.execute = AsyncMock(side_effect=[session_result, history_result])
        db_session.add = MagicMock()
        db_session.add_all = MagicMock()
        db_session.flush = AsyncMock()
        db_session.commit = AsyncMock()

        factory = self._make_pg_session_factory(db_session)
        request = _make_request(factory, anthropic_client)
        request_data = ChatRequest(
            session_id=str(session_id), message="Tell me about the weather"
        )

        with patch(
            "backend.services.chat_service._get_weather_context",
            new=AsyncMock(
                return_value={
                    "city": "Tokyo",
                    "temperature": 22.0,
                    "humidity": 55.0,
                    "wind_speed": 1.5,
                    "description": "Clear",
                }
            ),
        ):
            await chat_service.chat(request_data, request)

        db_session.add_all.assert_called_once()
        persisted_messages = db_session.add_all.call_args[0][0]
        assert len(persisted_messages) == 2
        roles = {m.role for m in persisted_messages}
        assert roles == {"user", "assistant"}
        db_session.commit.assert_awaited_once()

    async def test_chat_response_structure(self, anthropic_client: MagicMock) -> None:
        """ChatResponse fields are populated correctly from the Claude response."""
        session_id = uuid.uuid4()
        existing_session = _make_chat_session(session_id)

        session_result = MagicMock()
        session_result.scalar_one_or_none = MagicMock(return_value=existing_session)

        history_result = MagicMock()
        history_result.scalars = MagicMock(
            return_value=MagicMock(all=MagicMock(return_value=[]))
        )

        db_session = MagicMock()
        db_session.execute = AsyncMock(side_effect=[session_result, history_result])
        db_session.add = MagicMock()
        db_session.add_all = MagicMock()
        db_session.flush = AsyncMock()
        db_session.commit = AsyncMock()

        factory = self._make_pg_session_factory(db_session)
        request = _make_request(factory, anthropic_client)
        request_data = ChatRequest(session_id=str(session_id), message="Is it cold?")

        with patch(
            "backend.services.chat_service._get_weather_context",
            new=AsyncMock(
                return_value={
                    "city": "Berlin",
                    "temperature": 5.0,
                    "humidity": 75.0,
                    "wind_speed": 4.0,
                    "description": "Overcast",
                }
            ),
        ):
            response = await chat_service.chat(request_data, request)

        assert isinstance(response, ChatResponse)
        assert response.session_id == str(session_id)
        assert response.role == "assistant"
        assert response.content == "Looks sunny today!"
        assert isinstance(response.created_at, datetime)
        assert response.created_at.tzinfo is not None


class TestGetWeatherContext:
    """Unit tests for _get_weather_context fallback behavior."""

    async def test_returns_fallback_when_weather_service_unavailable(self) -> None:
        """Falls back to zero-value defaults when weather_service raises."""
        app = FastAPI()
        scope = {
            "type": "http",
            "method": "POST",
            "path": "/api/chat",
            "query_string": b"",
            "headers": [],
            "app": app,
        }
        request = Request(scope)

        with patch(
            "backend.services.chat_service.weather_service",
            side_effect=ImportError("no weather service"),
            create=True,
        ):
            result = await chat_service._get_weather_context("Unknown", request)

        assert result["city"] == "Unknown"
        assert result["temperature"] == 0.0
        assert result["description"] == "unavailable"
