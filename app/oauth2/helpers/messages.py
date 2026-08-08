"""Module holding enumerations related to response messages."""

from enum import StrEnum


class ClientMessages(StrEnum):
    """Enumeration of client-related messages, used in API responses."""

    SUCCESSFUL_CLIENT_REGISTRATION = "Client registered successfully."


class ScopeMessages(StrEnum):
    """Enumeration of scope-related messages, used in API responses."""

    SUCCESSFUL_SCOPE_CREATION = "Scope created successfully."
    SUCCESSFUL_SCOPE_MODIFICATION = "Scope modified successfully."
    SCOPE_ALREADY_EXIST_WITH_SCOPE = "Scope {scope} already exist in the system."
    SCOPE_ALREADY_EXIST_WITHOUT_SCOPE = "Scope already exist in the system."
    SCOPE_DOES_NOT_EXISTS = "Scope doesn't exist in the system."
    SCOPE_CAN_NOT_BE_DELETED = (
        "Selected scope can not be deleted, because it is assigned to a client."
    )
