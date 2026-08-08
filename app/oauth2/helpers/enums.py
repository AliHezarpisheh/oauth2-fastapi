"""Module holding enumerations for oauth2 related components."""

from enum import StrEnum


class GrantTypeEnum(StrEnum):
    """Enumeration of different grant types."""

    AUTHORIZATION_CODE = "authorization_code"
    CLIENT_CREDENTIALS = "client_credentials"
    IMPLICIT = "implicit"
    REFRESH_TOKEN = "refresh_token"  # noqa: S105


class ResponseTypeEnum(StrEnum):
    """Enumeration of different response artifacts and types the endpoint can return."""

    CODE = "code"
    TOKEN = "token"  # noqa: S105


class ClientStatusEnum(StrEnum):
    """Enumeration of oauth 2.0 confidential client status."""

    ACTIVE = "active"
    DISABLED = "disabled"


class ClientTokenEndpointAuthMethodEnum(StrEnum):
    """Enumeration of ways a confidential client can authenticate itself."""

    CLIENT_SECRET_BASIC = "client_secret_basic"  # noqa: S105
    CLIENT_SECRET_POST = "client_secret_post"  # noqa: S105
