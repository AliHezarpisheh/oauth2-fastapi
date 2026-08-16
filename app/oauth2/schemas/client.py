"""Module defining schemas for client-related operations."""

from datetime import datetime
from typing import Annotated

from pydantic import EmailStr, Field, HttpUrl, field_validator

from app.oauth2.helpers.enums import (
    ClientTokenEndpointAuthMethodEnum,
    GrantTypeEnum,
    ResponseTypeEnum,
)
from app.oauth2.helpers.exceptions import InvalidScopeError
from toolkit.api.schemas import BaseSchema, CommonMixins


class ClientBase(BaseSchema):
    """Schema holding common shared attributes between client schemas."""

    client_name: str
    client_uri: HttpUrl
    logo_uri: HttpUrl
    tos_uri: HttpUrl
    policy_uri: HttpUrl
    client_email: EmailStr
    software_id: str
    software_version: str
    token_endpoint_auth_method: ClientTokenEndpointAuthMethodEnum
    grant_types: list[GrantTypeEnum]
    redirect_uris: list[HttpUrl]
    response_types: list[ResponseTypeEnum]

    scopes: list[str]

    @field_validator("scopes")
    @classmethod
    def check_scope_format(cls, v: list[str]) -> list[str]:
        """
        Validate that each scope follows the required resource:action format.

        Parameters
        ----------
        v : list[str]
            Scope identifiers to validate. Each scope must contain exactly one
            colon (`:`) separating a resource name from an action name.

        Returns
        -------
        list[str]
            The original list of scopes when every scope satisfies the required
            format.

        Raises
        ------
        ValueError
            If any scope does not contain a colon or contains more than one
            colon.

        Notes
        -----
        Validation preserves the order and contents of the input list. Empty
        lists are considered valid.
        """
        # Set variables to prevent use of magic values.
        SEPARATOR = ":"
        SCOPE_SECTIONS = 2

        for scope in v:
            if SEPARATOR not in scope:
                raise InvalidScopeError(
                    f"Invalid scope: `{scope}`. You should separate resource and "
                    f"action using `{SEPARATOR}`."
                )

            if len(scope.split(SEPARATOR)) != SCOPE_SECTIONS:
                raise InvalidScopeError(
                    f"Invalid scope: `{scope}`. It should have only one `{SEPARATOR}`."
                )

        return v


class ClientRegistrationRequestSchema(ClientBase):
    """Request schema for client registration."""


class ClientRegistrationResponseSchema(CommonMixins, ClientBase):
    """Response schema for client registration, mirroring attributes back."""

    client_secret: str
    client_secret_expires_at: int


# Client initial access token


class ClientInitialAccessTokenBase(BaseSchema):
    """Schema holding common shared attributes between client IAT schemas."""

    max_registration: Annotated[
        int,
        Field(
            ge=1,
            le=10_000,
            default=1,
        ),
    ]
    note: Annotated[
        str | None,
        Field(
            description=(
                "A note helping the end-user or admin with no business logic impaction."
            ),
        ),
    ] = None


class ClientInitialAccessTokenRequestSchemas(ClientInitialAccessTokenBase):
    """Request schema for granting initial access token for client registration."""

    expires_in: Annotated[
        int,
        Field(
            ge=0,
            le=43200,
            description=(
                "How many more seconds later the token should expire? 0 means never "
                "expires and the maximum is set to 12 hours."
            ),
        ),
    ]


class ClientInitialAccessTokenResponseData(CommonMixins, BaseSchema):
    """Response data schema for granting initial access token on client registration."""

    token: str
    expires_at: datetime
