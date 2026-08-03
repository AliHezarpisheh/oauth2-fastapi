"""Module contains custom type annotations for API-related components."""

from typing import TypedDict

from toolkit.api.enums import HTTPStatusDoc, Status


class APIResponseDict(TypedDict):
    """
    Typed dict annotation for API responses.

    Type hint is created just because of type checkers. Most of the routers will return
    a Python dictionary holding attributes written below. The actual type conversion and
    checking is handled by fastapi and pydantic using `response_model_class` parameter
    at the router decorator.
    """

    status: Status
    message: str
    documentation_link: HTTPStatusDoc


class APISuccessResponseDict[T](APIResponseDict):
    """
    Typed dict annotation for successful API responses, holding additional data.

    Type hint is created just because of type checkers. Most of the routers will return
    a Python dictionary holding attributes written below. The actual type conversion and
    checking is handled by fastapi and pydantic using `response_model_class` parameter
    at the router decorator.
    """

    data: T


class ErrorDetailsDict(TypedDict):
    """Inner typed dict annotation error, demonstrating error's details."""

    field: str
    reason: str


class APIErrorResponse(APIResponseDict):
    """
    Typed dict annotation for error API responses, holding additional details.

    Type hint is created just because of type checkers. Most of the routers will return
    a Python dictionary holding attributes written below. The actual type conversion and
    checking is handled by fastapi and pydantic using `response_model_class` parameter
    at the router decorator.
    """

    details: ErrorDetailsDict
