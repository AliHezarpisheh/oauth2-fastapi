"""Module containing facade classes for scope-related operations."""

from sqlalchemy.ext.asyncio import AsyncSession, async_scoped_session

from app.oauth2.helpers.messages import ScopeMessages
from app.oauth2.models import Scope
from app.oauth2.schemas import (
    ScopeCreationRequestSchema,
    ScopeModificationRequestSchema,
)
from toolkit.api.annotations import APISuccessResponseDict
from toolkit.api.enums import HTTPStatusDoc, Status

from ..dal.scope import ScopeDataAccessLayer


class ScopeService:
    """Provide a service layer for scope-related business operations."""

    def __init__(self, db_session: async_scoped_session[AsyncSession]):
        """Initialize the service with a scoped asynchronous database session."""
        self.db_session = db_session
        self.scope_dal = ScopeDataAccessLayer(db_session=db_session)

    async def create_scope(
        self,
        scope_creation_input: ScopeCreationRequestSchema,
    ) -> APISuccessResponseDict[Scope]:
        """
        Create a scope and return a standardized success response.

        Parameters
        ----------
        scope_creation_input : ScopeCreationRequestSchema
            Validated data describing the scope to create. The input is
            expected to satisfy all schema validation rules.

        Returns
        -------
        APISuccessResponseDict[Scope]
            A success response containing the newly created scope, a creation
            status, a human-readable message, and the related HTTP
            documentation link.
        """
        scope = await self.scope_dal.create_scope(
            scope_creation_input=scope_creation_input
        )
        return {
            "status": Status.CREATED,
            "message": ScopeMessages.SUCCESSFUL_SCOPE_CREATION,
            "data": scope,
            "documentation_link": HTTPStatusDoc.HTTP_STATUS_201,
        }

    async def update_scope(
        self,
        scope_id: int,
        scope_modification_input: ScopeModificationRequestSchema,
    ) -> APISuccessResponseDict[Scope]:
        """
        Update an existing scope and return a standardized success response.

        Parameters
        ----------
        scope_id : int
            Identifier of the scope to update. It is assumed to reference an
            existing scope.
        scope_modification_input : ScopeModificationRequestSchema
            Validated attributes to modify. Only values permitted by the
            schema are accepted.

        Returns
        -------
        APISuccessResponseDict[Scope]
            A success response containing the updated scope, an update status,
            a human-readable message, and the related HTTP documentation
            link.
        """
        scope = await self.scope_dal.update_scope(
            scope_id=scope_id, scope_modification_input=scope_modification_input
        )
        return {
            "status": Status.UPDATED,
            "message": ScopeMessages.SUCCESSFUL_SCOPE_MODIFICATION,
            "data": scope,
            "documentation_link": HTTPStatusDoc.HTTP_STATUS_200,
        }

    async def delete_scope(
        self,
        scope_id: int,
    ) -> None:
        """
        Delete an existing scope.

        Parameters
        ----------
        scope_id : int
            Identifier of the scope to delete. It is assumed to reference an
            existing scope.

        Returns
        -------
        None
            Indicates that the deletion completed successfully.

        Side Effects
        ------------
        Permanently removes the referenced scope from the underlying data
        store.
        """
        await self.scope_dal.delete_scope(scope_id=scope_id)
