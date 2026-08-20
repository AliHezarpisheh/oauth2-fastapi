"""Define enumeration constants for status messages."""

from enum import StrEnum


class Status(StrEnum):
    """Enumeration of status messages used in API responses."""

    # General
    SUCCESS = "success"
    GRANTED = "granted"
    FAILURE = "failure"
    ERROR = "error"
    VALIDATION_ERROR = "validation_error"
    NOT_FOUND = "not_found"
    UNAUTHENTICATED = "unauthenticated"
    UNAUTHORIZED = "unauthorized"
    FORBIDDEN = "forbidden"
    CONFLICT = "conflict"
    CREATED = "created"
    UPDATED = "updated"
    DELETED = "deleted"

    # App specific
    INVALID_SCOPE = "invalid_scope"
    INVALID_TOKEN = "invalid_token"  # noqa: S105
    INVALID_CLIENT_METADATA = "invalid_client_metadata"
