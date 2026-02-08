"""Module defining integration tests for healthcheck API."""

from unittest import mock

import pytest
from fastapi import status
from httpx import AsyncClient

from config.database import AsyncDatabaseConnection
from toolkit.api.enums import HTTPStatusDoc, Status


@pytest.mark.order(1)
@pytest.mark.asyncio
@pytest.mark.smoke
async def test_health_check_everything_available(
    async_api_client: AsyncClient,
    db: AsyncDatabaseConnection,
) -> None:
    """Verify that the health check passes when all dependencies are available."""
    # Arrange
    endpoint = "/health-check"
    with (
        mock.patch("app.healthcheck.db", db),
    ):
        # Act
        response = await async_api_client.get(endpoint)

        # Assert
        actual_status_code = response.status_code
        expected_status_code = status.HTTP_200_OK
        assert actual_status_code == expected_status_code

        actual_json = {
            "database": True,
            "message": "Everything is Fine!",
        }
        expected_json = response.json()
        assert actual_json == expected_json


@pytest.mark.asyncio
async def test_health_check_db_unavailable(
    async_api_client: AsyncClient,
) -> None:
    """Verify that the health check fails when the database is unavailable."""
    # Arrange
    endpoint = "/health-check"
    mock_db = mock.AsyncMock(spec_set=AsyncDatabaseConnection)
    mock_db.test_connection.return_value = False
    with (
        mock.patch("app.healthcheck.db", mock_db),
    ):
        # Act
        response = await async_api_client.get(endpoint)

        # Assert
        actual_status_code = response.status_code
        expected_status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        assert actual_status_code == expected_status_code

        actual_json = {
            "status": Status.FAILURE.value,
            "message": "Database not available",
            "documentationLink": HTTPStatusDoc.HTTP_STATUS_503,
        }
        expected_json = response.json()
        assert actual_json == expected_json
