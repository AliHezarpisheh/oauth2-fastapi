"""Module defining schemas for scope-related operations."""

from typing import Self

from pydantic import model_validator

from toolkit.api.schemas import BaseSchema, CommonMixins


class ScopeBaseSchema(BaseSchema):
    """Schema holding common shared attributes between scope schemas."""

    description: str


class ScopeCreationRequestSchema(ScopeBaseSchema):
    """Request schema for scope creation."""

    resource: str
    action: str


class ScopeResponseData(CommonMixins, ScopeBaseSchema):
    """Response schema data for scope creation."""

    scope_name: str


class ScopeModificationRequestSchema(BaseSchema):
    """Request schema for scope modification."""

    resource: str | None = None
    action: str | None = None
    description: str | None = None

    @model_validator(mode="after")
    def are_resource_and_action_both_available(self) -> Self:
        """
        Ensure resource and action are either both provided or both omitted.

        Raises
        ------
        ValueError
            If exactly one of resource or action is provided.
        """
        if (not self.resource) != (not self.action):
            raise ValueError("Both resource and action should be available.")
        return self
