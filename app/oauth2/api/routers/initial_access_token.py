"""Module defining routers for retrieving and managing initial access tokens for DCR."""

from typing import Annotated, Any

from fastapi import APIRouter, Depends, status

from app.oauth2.api.dependencies import get_client_service
from app.oauth2.repository.services import ClientService
from app.oauth2.schemas import (
    ClientInitialAccessTokenRequestSchemas,
    ClientInitialAccessTokenResponseData,
)
from toolkit.api.annotations import APISuccessResponseDict
from toolkit.api.enums import OpenAPITags
from toolkit.api.schemas import APISuccessResponse

router = APIRouter(prefix="/admin", tags=[OpenAPITags.OAUTH2])


@router.post(
    "/initial-access-tokens",
    response_model=APISuccessResponse[ClientInitialAccessTokenResponseData],
    response_model_exclude_none=True,
    status_code=status.HTTP_201_CREATED,
)
async def grant_initial_access_token(
    initial_access_token_input: ClientInitialAccessTokenRequestSchemas,
    client_service: Annotated[ClientService, Depends(get_client_service)],
) -> APISuccessResponseDict[dict[str, Any]]:
    """Create an initial access token for dynamic client registration."""
    return await client_service.grant_initial_access_token(
        initial_access_token_input=initial_access_token_input
    )
