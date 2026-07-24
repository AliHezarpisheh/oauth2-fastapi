"""Module defining scope model."""

from typing import TYPE_CHECKING

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship

from toolkit.database import Base, CommonMixin
from toolkit.database.annotations import str255, text

if TYPE_CHECKING:
    from .client import Client
else:
    Client = "Client"


class Scope(CommonMixin, Base):
    """Model storing space-delimited scopes."""

    # Configuration
    __tablename__ = "scope"
    __table_args__ = (
        sa.Index("scope_scope_name_idx", "scope_name"),
        {"schema": "oauth2"},
    )

    # Columns
    scope_name: Mapped[str255] = mapped_column(
        nullable=False,
        unique=True,
        comment="Space-delimited and case-sensitive. e.g. article:read.",
    )
    description: Mapped[text] = mapped_column(
        nullable=True,
        unique=False,
        comment="Human-readable explanation of the scope, for future UI admin.",
    )

    # Relationships
    clients: Mapped[list[Client]] = relationship(
        secondary="oauth2.client",
        back_populates="scopes",
    )
