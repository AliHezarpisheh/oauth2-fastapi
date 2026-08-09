"""Module defining data access layer components related to scopes."""

from typing import Any, NoReturn

from sqlalchemy import delete, insert, update
from sqlalchemy.exc import IntegrityError, NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession, async_scoped_session

from app.oauth2.helpers.exceptions import (
    ScopeCanNotBeDeletedError,
    ScopeDoesNotExistError,
    ScopeDuplicateError,
)
from app.oauth2.helpers.messages import ScopeMessages
from app.oauth2.models import Scope
from app.oauth2.schemas import ScopeModificationRequestSchema
from app.oauth2.schemas.scope import ScopeCreationRequestSchema


class ScopeDataAccessLayer:
    """Provide database access operations for OAuth 2.0 scopes."""

    def __init__(self, db_session: async_scoped_session[AsyncSession]) -> None:
        """Initialize the data access layer with a database session."""
        self.db_session = db_session

    async def create_scope(
        self,
        scope_creation_input: ScopeCreationRequestSchema,
    ) -> Scope:
        """
        Create a scope using the resource and action from the input.

        Parameters
        ----------
        scope_creation_input
            Input containing the resource, action, and optional description.
            The resource and action are combined to form the scope name.

        Returns
        -------
        Scope
            The newly created scope, including its database-generated values.

        Raises
        ------
        ScopeDuplicateError
            If a scope with the resulting scope name already exists.
        IntegrityError
            If an integrity constraint other than the known duplicate-scope
            constraint is violated.
        """
        scope_name = self.format_scope_name(
            resource=scope_creation_input.resource,
            action=scope_creation_input.action,
        )
        stmt = (
            insert(Scope)
            .values(
                scope_name=scope_name,
                description=scope_creation_input.description,
            )
            .returning(Scope)
        )

        async with self.db_session.begin():
            try:
                result = await self.db_session.execute(stmt)
                scope = result.scalar_one()
            except IntegrityError as exc:
                self.handle_integrity_error(exc=exc, scope=scope_name)
            else:
                return scope

    async def update_scope(
        self,
        scope_id: int,
        scope_modification_input: ScopeModificationRequestSchema,
    ) -> Scope:
        """
        Update an existing scope with the supplied non-null values.

        Parameters
        ----------
        scope_id
            Identifier of the scope to update.
        scope_modification_input
            Modification data. Only supplied non-null values are applied.
            When both resource and action are supplied, they determine the
            resulting scope name.

        Returns
        -------
        Scope
            The updated scope with its current database values.

        Raises
        ------
        ScopeDoesNotExistError
            If no scope exists with the given identifier.
        ScopeDuplicateError
            If the resulting scope name conflicts with another scope.
        IntegrityError
            If an integrity constraint other than the known duplicate-scope
            constraint is violated.
        """
        cleaned_scope_present_values = self.clean_scope_on_update(
            scope_modification_input=scope_modification_input,
        )

        stmt = (
            update(Scope)
            .values(cleaned_scope_present_values)
            .where(Scope.id == scope_id)
            .returning(Scope)
        )

        async with self.db_session.begin():
            try:
                result = await self.db_session.execute(stmt)
                scope = result.scalar_one()
            except IntegrityError as exc:
                self.handle_integrity_error(exc=exc)
            except NoResultFound:
                self.handle_no_result_found_error()
            else:
                return scope

    async def delete_scope(
        self,
        scope_id: int,
    ) -> None:
        """
        Delete the scope identified by the given identifier.

        Parameters
        ----------
        scope_id
            Identifier of the scope to delete.

        Raises
        ------
        ScopeDoesNotExistError
            If the target scope does not exist.
        ScopeCanNotBeDeletedError
            If the scope is referenced by another entity and cannot be deleted.
        IntegrityError
            If a deletion constraint other than the known foreign-key
            restriction is violated.
        """
        stmt = delete(Scope).where(Scope.id == scope_id)

        async with self.db_session.begin():
            try:
                await self.db_session.execute(stmt)
            except IntegrityError as exc:
                self.handle_on_delete_restriction_error(exc=exc)
            except NoResultFound:
                self.handle_no_result_found_error()

    # Helper methods - not necessarily doing things with database.

    @staticmethod
    def format_scope_name(resource: str, action: str) -> str:
        """Construct a scope name from a resource and an action."""
        return f"{resource}:{action}"

    def clean_scope_on_update(
        self,
        scope_modification_input: ScopeModificationRequestSchema,
    ) -> dict[str, Any]:
        """
        Prepare supplied scope fields for an update operation.

        Parameters
        ----------
        scope_modification_input
            Modification data whose non-null fields should be applied.
            Resource and action, when both supplied, are represented by their
            combined scope name rather than as independent update fields.

        Returns
        -------
        dict[str, Any]
            Database fields and values that should be applied to the scope.
        """
        scope_present_values = scope_modification_input.model_dump(exclude_none=True)

        if not (scope_modification_input.resource and scope_modification_input.action):
            return scope_present_values

        scope_name = self.format_scope_name(
            resource=scope_present_values["resource"],
            action=scope_present_values["action"],
        )
        scope_present_values["scope_name"] = scope_name

        del scope_present_values["resource"]
        del scope_present_values["action"]
        return {**scope_present_values, "scope_name": scope_name}

    @staticmethod
    def handle_integrity_error(
        exc: IntegrityError, scope: str | None = None
    ) -> NoReturn:
        """
        Translate a known duplicate-scope violation into a domain error.

        Parameters
        ----------
        exc
            Integrity error raised by the database operation.
        scope: optional
            Scope name involved in the failed operation. If not provided, the name won't
            be in the response

        Raises
        ------
        ScopeDuplicateError
            If the database error represents a duplicate scope name.
        IntegrityError
            The original exception if it represents another integrity
            constraint violation.
        """
        if (
            'duplicate key value violates unique constraint "scope_scope_name_key"'
            in str(exc)
        ):
            msg = (
                ScopeMessages.SCOPE_ALREADY_EXIST_WITH_SCOPE.value.format(scope=scope)
                if scope
                else ScopeMessages.SCOPE_ALREADY_EXIST_WITHOUT_SCOPE.value
            )
            raise ScopeDuplicateError(msg)

        raise exc

    @staticmethod
    def handle_on_delete_restriction_error(exc: IntegrityError) -> NoReturn:
        """
        Translate a known scope deletion restriction into a domain error.

        Parameters
        ----------
        exc
            Integrity error raised while deleting a scope.

        Raises
        ------
        ScopeCanNotBeDeletedError
            If the scope is referenced by a client-scope relationship.
        IntegrityError
            The original exception if it represents another integrity
            constraint violation.
        """
        if (
            'update or delete on table "scope" violates foreign key constraint '
            '"client_scope_scope_id_fkey" on table "client_scope"' in str(exc)
        ):
            raise ScopeCanNotBeDeletedError(
                ScopeMessages.SCOPE_CAN_NOT_BE_DELETED.value
            )
        raise exc

    @staticmethod
    def handle_no_result_found_error() -> NoReturn:
        """
        Translate a missing scope result into a domain-specific error.

        Raises
        ------
        ScopeDoesNotExistError
            Always raised to indicate that the requested scope does not exist.
        """
        raise ScopeDoesNotExistError(ScopeMessages.SCOPE_DOES_NOT_EXISTS.value)
