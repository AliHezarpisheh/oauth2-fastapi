"""Module provides a health check endpoint for the FastAPI application."""

from typing import Any

from fastapi import APIRouter, status
from pydantic import BaseModel

from config.base import db
from toolkit.api.exceptions import ServiceUnavailableError

router = APIRouter(prefix="/health-check", tags=["Health Check"])


class HealthCheckResponse(BaseModel):
    """
    Model for health check response.

    Attributes
    ----------
    database : bool
        Indicates if the database is available.
    message : str
        Message indicating the health status.
    """

    database: bool
    message: str


@router.get(
    "",
    response_model=HealthCheckResponse,
    status_code=status.HTTP_200_OK,
    description="Perform a health check on the service.",
)
async def check_health() -> Any:
    """
    Perform a health check to ensure all the necessary connections are available.

    Returns
    -------
    Any
        JSON response indicating the health status of the database.

    Raises
    ------
    ServiceUnavailableError
        If the database connection is not available, raises a 503 HTTP error.
    """
    is_db_available = await db.test_connection()
    if not is_db_available:
        raise ServiceUnavailableError(message="Database not available")
    return {
        "database": is_db_available,
        "message": "Everything is Fine!",
    }
