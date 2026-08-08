"""Module defining administrator routers for managing scopes."""

from typing import Annotated

from fastapi import APIRouter, Depends, Path, status

from app.oauth2.api.dependencies import get_scope_service
from app.oauth2.models import Scope
from app.oauth2.repository.services import ScopeService
from app.oauth2.schemas import (
    ScopeCreationRequestSchema,
    ScopeModificationRequestSchema,
    ScopeResponseData,
)
from toolkit.api.annotations import APISuccessResponseDict
from toolkit.api.enums import OpenAPITags
from toolkit.api.schemas import APISuccessResponse

router = APIRouter(prefix="/scopes", tags=[OpenAPITags.OAUTH2])


@router.post(
    "",
    response_model=APISuccessResponse[ScopeResponseData],
    response_model_exclude_none=True,
    status_code=status.HTTP_201_CREATED,
)
async def create_scope(
    scope_service: Annotated[ScopeService, Depends(get_scope_service)],
    scope_creation_input: ScopeCreationRequestSchema,
) -> APISuccessResponseDict[Scope]:
    """Create a new OAuth 2.0 scope."""
    return await scope_service.create_scope(scope_creation_input=scope_creation_input)


@router.patch(
    "/{scope_id}",
    response_model=APISuccessResponse[ScopeResponseData],
    response_model_exclude_none=True,
    status_code=status.HTTP_200_OK,
)
async def update_scope(
    scope_id: Annotated[int, Path()],
    scope_modification_input: ScopeModificationRequestSchema,
    scope_service: Annotated[ScopeService, Depends(get_scope_service)],
) -> APISuccessResponseDict[Scope]:
    """Update an existing OAuth 2.0 scope by id."""
    return await scope_service.update_scope(
        scope_id=scope_id,
        scope_modification_input=scope_modification_input,
    )


@router.delete(
    "/{scope_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_scope(
    scope_id: Annotated[int, Path()],
    scope_service: Annotated[ScopeService, Depends(get_scope_service)],
) -> None:
    """Delete an OAuth2 scope by id."""
    await scope_service.delete_scope(scope_id=scope_id)
