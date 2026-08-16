"""Module containing facade classes for confidential clients operations."""

from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession, async_scoped_session

import toolkit.security.crypto as toolkit_crypto
from app.oauth2.helpers.messages import InitialAccessTokenMessages
from app.oauth2.schemas import ClientInitialAccessTokenRequestSchemas
from app.oauth2.schemas.client import ClientRegistrationRequestSchema
from toolkit.api.annotations import APISuccessResponseDict
from toolkit.api.enums import HTTPStatusDoc, Status

from ..bll.client import ClientBusinessLogicLayer
from ..dal.client import ClientDataAccessLayer


class ClientService:
    """Service class for client-related operations."""

    def __init__(self, db_session: async_scoped_session[AsyncSession]) -> None:
        """Initialize the service with a scoped database session."""
        self.db_session = db_session
        self.client_dal = ClientDataAccessLayer(db_session=db_session)
        self.client_bll = ClientBusinessLogicLayer()

    async def register_client(
        self,
        client_registration_input: ClientRegistrationRequestSchema,
    ) -> dict[str, Any]:
        """
        Register a confidential client and return its registration details.

        Parameters
        ----------
        client_registration_input
            Registration data defining the client's identity, endpoints,
            authentication method, grant types, and requested scopes.

        Returns
        -------
        dict[str, Any]
            Echoing back the client requested metadata, with additional metadata such
            as `client_id` and `client_secret`.
        """
        self.client_bll.validate_grant_types_and_response_types(
            grant_types=client_registration_input.grant_types,
            response_types=client_registration_input.response_types,
        )
        client_secret = toolkit_crypto.generate_secret()
        client, scopes = await self.client_dal.create_client(
            client_secret=client_secret,
            client_registration_input=client_registration_input,
        )
        return {
            **{key: getattr(client, key) for key in client.__table__.columns.keys()},
            "client_secret_expires_at": 0,
            "scopes": scopes,
        }

    async def grant_initial_access_token(
        self,
        initial_access_token_input: ClientInitialAccessTokenRequestSchemas,
    ) -> APISuccessResponseDict[dict[str, Any]]:
        """
        Grant an initial access token for client registration.

        Parameters
        ----------
        initial_access_token_input
            Configuration for the initial access token, including its registration
            limit and expiration settings.

        Returns
        -------
        APISuccessResponseDict[dict[str, Any]]
            A successful response containing the generated plaintext token and
            its registration constraints. The stored token hash is excluded from
            the response.
        """
        token = toolkit_crypto.generate_secret()
        token_hash = toolkit_crypto.generate_text_hash(token)
        client_initial_access_token = await self.client_dal.create_initial_access_token(
            initial_access_token_input=initial_access_token_input,
            token_hash=token_hash,
        )
        return {
            "status": Status.GRANTED,
            "message": (
                InitialAccessTokenMessages.SUCCESSFUL_TOKEN_GRANT.format(
                    max_registration=client_initial_access_token.max_registration,
                    expiration_time=client_initial_access_token.expires_at,
                )
            ),
            "data": {
                **{
                    key: getattr(client_initial_access_token, key)
                    for key in client_initial_access_token.__table__.columns.keys()
                    if key != "token_hash"
                },
                "token": token,
            },
            "documentation_link": HTTPStatusDoc.HTTP_STATUS_201,
        }
