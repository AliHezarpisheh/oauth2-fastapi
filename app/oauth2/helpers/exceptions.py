"""Module defines exceptions related to Oauth 2.0 and OIDC operations."""

import fastapi

from toolkit.api.enums import HTTPStatusDoc, Status
from toolkit.api.exceptions import APIException, DoesNotExistError, DuplicateError


class InvalidScopeError(APIException):
    """Exception that should raised when a scope is invalid, unknown, or malformed."""

    status_code = fastapi.status.HTTP_400_BAD_REQUEST
    status = Status.INVALID_SCOPE
    documentation_link = HTTPStatusDoc.HTTP_STATUS_400


class ScopeCanNotBeDeletedError(APIException):
    """Exception raised when a scope is used by a client and can not be deleted."""

    status_code = fastapi.status.HTTP_409_CONFLICT
    status = Status.CONFLICT
    documentation_link = HTTPStatusDoc.HTTP_STATUS_409


class ScopeDoesNotExistError(DoesNotExistError):
    """Exception raised when a scope doesn't exist in the system."""


class ScopeDuplicateError(DuplicateError):
    """Exception raised when a scope already exist in the system."""
