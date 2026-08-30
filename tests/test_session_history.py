from types import SimpleNamespace
from unittest.mock import MagicMock

from app.api.routes.sessions import get_session


def test_get_session_uses_current_generation():
    session = SimpleNamespace(
        id="test-session-id",
        model="gpt-5.6",
        generation=2,
        created_at=None,
        updated_at=None,
    )

    old_message = SimpleNamespace(
        id="old-message",
        role="user",
        content="Старе повідомлення",
        model="gpt-5.6",
        input_tokens=10,
        output_tokens=20,
        total_tokens=30,
        cost=0.01,
        created_at=None,
    )

    db = MagicMock()

    db.query.return_value.filter.return_value.first.return_value = session

    db.query.return_value.filter.return_value.order_by.return_value.all.return_value = []

    result = get_session(
        session_id="test-session-id",
        db=db,
    )

    assert result["session_id"] == "test-session-id"
    assert result["messages"] == []
    assert result["total_tokens"] == 0
    assert result["total_cost"] == 0