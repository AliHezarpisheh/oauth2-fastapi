"""Module for client registration and management endpoints."""

from typing import Annotated, Any

from fastapi import APIRouter, BackgroundTasks, Depends, Header, status

from app.oauth2.api.dependencies import get_client_service
from app.oauth2.repository.services import ClientService
from app.oauth2.schemas import (
    ClientRegistrationRequestSchema,
    ClientRegistrationResponseSchema,
)
from toolkit.api.enums import OpenAPITags

router = APIRouter(prefix="/register", tags=[OpenAPITags.OAUTH2])


@router.post(
    "",
    response_model=ClientRegistrationResponseSchema,
    response_model_exclude_none=True,
    status_code=status.HTTP_201_CREATED,
)
async def register_client(
    bearer_token: Annotated[str, Header(alias="Authorization")],
    client_registration_input: ClientRegistrationRequestSchema,
    background_tasks: BackgroundTasks,
    client_service: Annotated[ClientService, Depends(get_client_service)],
) -> dict[str, Any]:
    """Register a new OAuth2 client application."""
    await client_service.check_initial_access_token(
        bearer_token=bearer_token,
        background_tasks=background_tasks,
    )
    return await client_service.register_client(
        client_registration_input=client_registration_input
    )
