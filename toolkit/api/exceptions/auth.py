"""Custom exceptions related to auth operations."""

from typing import ClassVar

import fastapi

from toolkit.api.enums import HTTPStatusDoc, Status

from .abc import APIException


class BearerAuthenticationFailedError(APIException):
    """Exception raised when request fails bearer authentication protocols."""

    status_code = fastapi.status.HTTP_401_UNAUTHORIZED
    status = Status.UNAUTHENTICATED
    documentation_link = HTTPStatusDoc.HTTP_STATUS_401

    default_http_headers: ClassVar = {"WWW-Authenticate": "Bearer"}
