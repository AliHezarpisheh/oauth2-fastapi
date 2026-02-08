"""Module defining unit tests for application lifespan contextmanager."""

from unittest import mock

from fastapi.testclient import TestClient

from app.main import app
from config.database import AsyncDatabaseConnection


def test_lifespan() -> None:
    """Verify that database connections close properly during app shutdown."""
    # Arrange
    mock_db = mock.AsyncMock(spec_set=AsyncDatabaseConnection)

    with mock.patch("app.lifespan.db", mock_db):
        # Act
        with TestClient(app=app):
            pass

        # Assert
        mock_db.close_engine.assert_awaited_once_with()
