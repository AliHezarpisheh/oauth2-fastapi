"""Module holding enumerations related to the project's settings."""

from enum import StrEnum


class EnvEnum(StrEnum):
    """Enumeration of different environments."""

    DEVELOPMENT = "development"
    TESTING = "testing"
    PRODUCTION = "production"
