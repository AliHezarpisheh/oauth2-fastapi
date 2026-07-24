"""Module holding enumerations for oauth2 related components."""

from enum import StrEnum


class GrantTypesEnum(StrEnum):
    """Enumeration of supported grant types."""

    CLIENT_CREDENTIALS = "client_credentials"


class ClientStatusEnum(StrEnum):
    """Enumeration of oauth 2.0 confidential client status."""

    ACTIVE = "active"
    DISABLED = "disabled"


class ClientTokenEndpointAuthMethodEnum(StrEnum):
    """Enumeration of ways a confidential client can authenticate itself."""

    CLIENT_SECRET_BASIC = "client_secret_basic"
    CLIENT_SECRET_POST = "client_secret_post"
