"""Define enumeration constants for OpenAPI tags."""

from enum import StrEnum


class OpenAPITags(StrEnum):
    """Enumeration of OpenAPI tags."""

    OAUTH2 = "OAuth 2.0"
    OIDC = "OpenID Connect"
    PROTECTED = "Protected Endpoints"
    HEALTH_CHECK = "Health Check"
