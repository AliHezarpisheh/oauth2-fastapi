"""Module containing facade classes for confidential clients operations."""

import secrets
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession, async_scoped_session

from app.oauth2.schemas.client import ClientRegistrationRequestSchema

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
        client_secret = secrets.token_urlsafe(32)
        client, scopes = await self.client_dal.create_client(
            client_secret=client_secret,
            client_registration_input=client_registration_input,
        )
        return {
            **{key: getattr(client, key) for key in client.__table__.columns.keys()},
            "client_secret_expires_at": 0,
            "scopes": scopes,
        }
