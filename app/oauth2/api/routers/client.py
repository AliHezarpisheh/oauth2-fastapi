"""Module for client registration and management endpoints."""

from typing import Annotated, Any

from fastapi import APIRouter, Depends, status

from app.oauth2.api.dependencies import get_client_service
from app.oauth2.repository.services import ClientService
from app.oauth2.schemas import (
    ClientRegistrationRequestSchema,
    ClientRegistrationResponseSchema,
)
from toolkit.api.annotations import APISuccessResponseDict
from toolkit.api.enums import OpenAPITags
from toolkit.api.schemas import APISuccessResponse

router = APIRouter(prefix="/register", tags=[OpenAPITags.OAUTH2])


@router.post(
    "",
    response_model=APISuccessResponse[ClientRegistrationResponseSchema],
    response_model_exclude_none=True,
    status_code=status.HTTP_201_CREATED,
)
async def register_client(
    client_registration_input: ClientRegistrationRequestSchema,
    client_service: Annotated[ClientService, Depends(get_client_service)],
) -> APISuccessResponseDict[dict[str, Any]]:
    """Register a new OAuth2 client application."""
    return await client_service.register_client(
        client_registration_input=client_registration_input
    )
