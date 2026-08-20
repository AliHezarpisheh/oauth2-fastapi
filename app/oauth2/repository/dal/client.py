"""Module defining data access layer components related to clients."""

from datetime import UTC, datetime, timedelta
from typing import NoReturn

from fastapi import BackgroundTasks
from sqlalchemy import delete, insert, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession, async_scoped_session

from app.oauth2.helpers.exceptions import (
    ClientDuplicateError,
    InvalidScopeError,
    InvalidTokenError,
)
from app.oauth2.helpers.messages import ClientMessages, InitialAccessTokenMessages
from app.oauth2.models import Client, ClientScope, InitialAccessToken, Scope
from app.oauth2.schemas import (
    ClientInitialAccessTokenRequestSchemas,
    ClientRegistrationRequestSchema,
)


class ClientDataAccessLayer:
    """Provide database access operations for OAuth2 clients."""

    def __init__(self, db_session: async_scoped_session[AsyncSession]) -> None:
        """Initialize the data access layer with a database session."""
        self.db_session = db_session

    async def create_client(
        self,
        client_registration_input: ClientRegistrationRequestSchema,
        client_secret: str,
    ) -> tuple[Client, set[str]]:
        """
        Create a client and associate it with its requested scopes.

        Parameters
        ----------
        client_registration_input
            Registration data for the client, including its requested scopes.
            All requested scopes must exist before the client can be created.
        client_secret
            Secret to associate with the newly registered client.

        Returns
        -------
        tuple[Client, set[str]]
            The created client and the set of scope names associated with it.

        Raises
        ------
        InvalidScopeError
            If one or more requested scopes do not exist.
        ClientDuplicateError
            If a client with the requested name already exists.
        IntegrityError
            If an unhandled database integrity constraint is violated.
        """
        client_creation_stmt = (
            insert(Client)
            .values(
                client_secret=client_secret,
                client_name=client_registration_input.client_name,
                client_uri=str(client_registration_input.client_uri),
                logo_uri=str(client_registration_input.logo_uri),
                tos_uri=str(client_registration_input.tos_uri),
                policy_uri=str(client_registration_input.policy_uri),
                client_email=client_registration_input.client_email,
                software_id=client_registration_input.software_id,
                software_version=client_registration_input.software_version,
                token_endpoint_auth_method=client_registration_input.token_endpoint_auth_method,
                grant_types=client_registration_input.grant_types,
                redirect_uris=[
                    str(uri) for uri in client_registration_input.redirect_uris
                ],
                response_types=client_registration_input.response_types,
            )
            .returning(Client)
        )

        async with self.db_session.begin():
            available_scopes_id, available_scope_names = await self.get_scopes_id(
                client_scopes=client_registration_input.scopes
            )

            try:
                result = await self.db_session.execute(client_creation_stmt)
                client = result.scalar_one()

                await self.db_session.execute(
                    insert(ClientScope),
                    [
                        {"client_id": client.id, "scope_id": scope_id}
                        for scope_id in available_scopes_id
                    ],
                )
            except IntegrityError as exc:
                self.handle_client_integrity_error(
                    exc=exc, client_name=client_registration_input.client_name
                )
            else:
                return client, available_scope_names

    async def create_initial_access_token(
        self,
        initial_access_token_input: ClientInitialAccessTokenRequestSchemas,
        token_hash: str,
    ) -> InitialAccessToken:
        """
        Create and persist an initial access token with its registration limits.

        Parameters
        ----------
        initial_access_token_input
            Token configuration, including its lifetime, registration limit, and
            optional note.
        token_hash
            Hash of the token to persist instead of the plaintext token.

        Returns
        -------
        InitialAccessToken
            The newly created token record, including its expiration time and
            registration limit.
        """
        stmt = (
            insert(InitialAccessToken)
            .values(
                token_hash=token_hash,
                expires_at=(
                    datetime.now(UTC)
                    + timedelta(seconds=initial_access_token_input.expires_in)
                ),
                max_registration=initial_access_token_input.max_registration,
                note=initial_access_token_input.note,
            )
            .returning(InitialAccessToken)
        )

        async with self.db_session.begin():
            result = await self.db_session.execute(stmt)
            initial_access_token = result.scalar_one()
            return initial_access_token

    async def check_initial_access_token(
        self,
        token_hash: str,
        background_tasks: BackgroundTasks | None = None,
    ) -> None:
        """
        Validate an initial access token and consume one registration attempt.

        Parameters
        ----------
        token_hash
            Hash of the initial access token to validate.
        background_tasks
            Optional task manager used to defer deletion of an invalid token.

        Raises
        ------
        InvalidTokenError
            If the token does not exist or has expired.
        InvalidTokenError
            If the token violates an integrity constraint during consumption.

        Notes
        -----
        A successful validation increments the token's registration count.
        Invalid or expired tokens are deleted immediately or in the background,
        depending on whether background tasks are available.
        """
        stmt = (
            update(InitialAccessToken)
            .values(registrations_used=InitialAccessToken.registrations_used + 1)
            .where(
                InitialAccessToken.token_hash == token_hash,
                InitialAccessToken.expires_at > datetime.now(UTC),
            )
        )

        try:
            async with self.db_session.begin():
                result = await self.db_session.execute(stmt)
                if result.rowcount == 0:  # type: ignore[attr-defined]
                    raise InvalidTokenError(
                        InitialAccessTokenMessages.INVALID_TOKEN.value
                    )
        except IntegrityError as exc:
            # Remove the token in background if it exists but in an invalid/expired
            # state.
            if background_tasks is not None:
                background_tasks.add_task(
                    self.delete_initial_access_token_by_token_hash,
                    token_hash=token_hash,
                )
            else:
                await self.delete_initial_access_token_by_token_hash(
                    token_hash=token_hash
                )

            # Response to user by handling the integrity error.
            self.handle_initial_access_token_integrity_error(exc=exc)

    async def delete_initial_access_token_by_token_hash(
        self,
        token_hash: str,
    ) -> None:
        """
        Delete an initial access token identified by its hash.

        Parameters
        ----------
        token_hash
            Hash of the initial access token to delete.

        Notes
        -----
        No error is raised when no token matches the provided hash.
        """
        async with self.db_session.begin():
            await self.db_session.execute(
                delete(InitialAccessToken).where(
                    InitialAccessToken.token_hash == token_hash
                )
            )

    # TODO: Application scopes don't change too much, so it is better to cache them.
    async def get_scopes_id(
        self, client_scopes: list[str]
    ) -> tuple[list[int], set[str]]:
        """
        Validate requested scopes and return their identifiers and names.

        Parameters
        ----------
        client_scopes
            Scope names requested by the client. Every requested name must
            correspond to an existing scope.

        Returns
        -------
        tuple[list[int], set[str]]
            The identifiers and names of all requested scopes.

        Raises
        ------
        InvalidScopeError
            If one or more requested scope names do not exist.
        """
        scopes = (
            await self.db_session.execute(
                select(Scope.id, Scope.scope_name).where(
                    Scope.scope_name.in_(client_scopes)
                )
            )
        ).all()

        found_scopes = {row.scope_name for row in scopes}
        invalid_scopes = set(client_scopes) - found_scopes
        if invalid_scopes:
            raise InvalidScopeError(
                f"All or some requested scopes are invalid: {invalid_scopes}"
            )

        return [row.id for row in scopes], found_scopes

    @staticmethod
    def handle_client_integrity_error(
        exc: IntegrityError, client_name: str
    ) -> NoReturn:
        """
        Translate a duplicate client-name violation into a domain error.

        Parameters
        ----------
        exc
            Integrity error raised by the database operation.
        client_name
            Name of the client involved in the failed operation.

        Raises
        ------
        ClientDuplicateError
            If the error indicates that the client name already exists.
        IntegrityError
            The original exception if it represents another integrity
            constraint violation.
        """
        if (
            'duplicate key value violates unique constraint "client_client_name_key"'
            in str(exc)
        ):
            raise ClientDuplicateError(
                ClientMessages.CLIENT_ALREADY_EXIST.format(client_name=client_name)
            )

        raise exc

    @staticmethod
    def handle_initial_access_token_integrity_error(
        exc: IntegrityError,
    ) -> NoReturn:
        """
        Translate token-related integrity violations into a domain error.

        Parameters
        ----------
        exc
            Integrity error raised while creating or consuming an access token.

        Raises
        ------
        InvalidTokenError
            If the error represents an invalid or expired initial access token.
        IntegrityError
            The original exception if it represents another integrity
            constraint violation.
        """
        if 'violates check constraint "initial_access_token_check"' in str(
            exc
        ) or 'violates check constraint "initial_access_token_expires_at_check"' in str(
            exc
        ):
            raise InvalidTokenError(InitialAccessTokenMessages.INVALID_TOKEN.value)

        raise exc
