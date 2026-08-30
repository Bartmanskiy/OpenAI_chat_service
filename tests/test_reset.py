from types import SimpleNamespace
from unittest.mock import MagicMock

from app.api.routes.sessions import reset_session


def test_reset_session():
    session = SimpleNamespace(
        id="test-session-id",
        generation=1,
    )

    db = MagicMock()

    db.query.return_value.filter.return_value.first.return_value = session

    result = reset_session(
        session_id="test-session-id",
        db=db,
    )

    assert result["session_id"] == "test-session-id"
    assert result["generation"] == 2

    assert session.generation == 2
    db.commit.assert_called_once()
    db.refresh.assert_called_once_with(session)