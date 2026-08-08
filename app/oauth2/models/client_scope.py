"""Module defining the association table for client and scope tables."""

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

from toolkit.database import Base, CommonMixin


class ClientScope(CommonMixin, Base):
    """Association table made for connecting clients and scopes."""

    # Configuration
    __tablename__ = "client_scope"
    __table_args__ = (
        sa.UniqueConstraint("client_id", "scope_id", name="client_scope_ids_uix"),
        {"schema": "oauth2"},
    )

    # Columns
    client_id: Mapped[int] = mapped_column(sa.ForeignKey("oauth2.client.id"))
    scope_id: Mapped[int] = mapped_column(
        sa.ForeignKey("oauth2.scope.id", ondelete="RESTRICT")
    )

    # Methods
    def __str__(self) -> str:
        """Return a human-readable string representation."""
        return f"Client {self.client_id} ↔ Scope {self.scope_id}"

    def __repr__(self) -> str:
        """Return a string representation for debugging and development."""
        return (
            f"{self.__class__.__name__}("
            f"id={self.id!r}, "
            f"client_id={self.client_id!r}, "
            f"scope_id={self.scope_id!r}"
            f")"
        )
