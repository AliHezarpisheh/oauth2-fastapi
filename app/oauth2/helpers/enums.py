"""Module holding enumerations for oauth2 related components."""

from enum import StrEnum


class ClientStatusEnum(StrEnum):
    """Enumeration of oauth 2.0 confidential client status."""

    ACTIVE = "active"
    DISABLED = "disabled"


class ClientTokenEndpointAuthMethod(StrEnum):
    """Enumeration of ways a confidential client can authenticate itself."""

    CLIENT_SECRET_BASIC = "client_secret_basic"
    CLIENT_SECRET_POST = "client_secret_post"
