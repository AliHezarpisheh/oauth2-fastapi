"""Module holding abstract base classes for the application."""

from abc import ABC, abstractmethod
from typing import ClassVar

from toolkit.api.enums import HTTPStatusDoc, Status


class APIException(ABC, Exception):
    """Base exception for all API-related errors, handled in exception handlers."""

    default_http_headers: ClassVar[dict[str, str] | None] = None

    def __init__(
        self,
        message: str,
        http_headers: dict[str, str] | None = None,
        field: str | None = None,
        reason: str | None = None,
    ) -> None:
        """
        Initialize an `APIException` object.

        Both of the `field` and `reason` should be set, or both should be leaved unset.
        If one of them is set and the other is unset, an `ValueError` will be
        raised.
        """
        if bool(field) ^ bool(reason):
            raise ValueError("`field` and `reason` should be both set or unset.")

        self.message = message
        self.field = field
        self.reason = reason
        self._http_headers = http_headers
        super().__init__(message)

    @property
    @abstractmethod
    def status_code(self) -> int:
        """HTTP status code associated with the exception."""

    @property
    @abstractmethod
    def status(self) -> Status:
        """Short status message for the exception."""

    @property
    @abstractmethod
    def documentation_link(self) -> HTTPStatusDoc:
        """URL to relevant documentation."""

    @property
    def http_headers(self) -> dict[str, str] | None:
        """
        Return the effective HTTP headers for the response.

        Notes
        -----
        If you set same headers/keys on both instance and class levels, the instance
        level will be included in the final return value.
        """
        if self._http_headers is None and self.default_http_headers is None:
            return None
        if self._http_headers is not None and self.default_http_headers is not None:
            return {**self.default_http_headers, **self._http_headers}
        return (
            self._http_headers
            if self._http_headers is not None
            else self.default_http_headers
        )

    def to_jsonable_dict(self) -> dict[str, str | dict[str, str]]:
        """Return error data as a jsonable dictionary."""
        error_data: dict[str, str | dict[str, str]] = {
            "status": self.status.value,
            "message": self.message,
            "documentationLink": self.documentation_link.value,
        }
        if self.field and self.reason:
            error_data.update({"details": {"field": self.field, "reason": self.reason}})
        return error_data
