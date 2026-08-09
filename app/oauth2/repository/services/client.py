"""Module containing facade classes for confidential clients operations."""

import secrets
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession, async_scoped_session

from app.oauth2.helpers.messages import ClientMessages
from app.oauth2.schemas.client import ClientRegistrationRequestSchema
from toolkit.api.annotations import APISuccessResponseDict
from toolkit.api.enums import HTTPStatusDoc, Status

from ..dal.client import ClientDataAccessLayer


class ClientService:
    """Service class for client-related operations."""

    def __init__(self, db_session: async_scoped_session[AsyncSession]) -> None:
        """Initialize the service with a scoped database session."""
        self.db_session = db_session
        self.client_dal = ClientDataAccessLayer(db_session=db_session)

    async def register_client(
        self, client_registration_input: ClientRegistrationRequestSchema
    ) -> APISuccessResponseDict[dict[str, Any]]:
        """
        Register a confidential client and return its registration details.

        Parameters
        ----------
        client_registration_input
            Registration data defining the client's identity, endpoints,
            authentication method, grant types, and requested scopes.

        Returns
        -------
        APISuccessResponseDict[dict[str, Any]]
            A successful creation response containing the registered client,
            its associated scopes, and the generated client secret.
        """
        client_secret = secrets.token_urlsafe(32)
        client, scopes = await self.client_dal.create_client(
            client_secret=client_secret,
            client_registration_input=client_registration_input,
        )
        return {
            "status": Status.CREATED,
            "message": ClientMessages.SUCCESSFUL_CLIENT_REGISTRATION,
            "data": {
                **{
                    key: getattr(client, key) for key in client.__table__.columns.keys()
                },
                "scopes": scopes,
            },
            "documentation_link": HTTPStatusDoc.HTTP_STATUS_201,
        }
