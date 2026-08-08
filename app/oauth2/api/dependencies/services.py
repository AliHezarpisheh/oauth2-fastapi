"""Module containing dependency functions for the oauth 2.0 endpoints."""

from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession, async_scoped_session

from app.oauth2.repository.services import ClientService, ScopeService
from toolkit.api.dependencies import get_async_db_session


async def get_client_service(
    db_session: Annotated[
        async_scoped_session[AsyncSession], Depends(get_async_db_session)
    ],
) -> ClientService:
    """Return `ClientService` by injecting the database session."""
    return ClientService(db_session=db_session)


async def get_scope_service(
    db_session: Annotated[
        async_scoped_session[AsyncSession], Depends(get_async_db_session)
    ],
) -> ScopeService:
    """Return `ScopeService` by injecting the database session."""
    return ScopeService(db_session=db_session)
