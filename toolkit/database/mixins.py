"""Module containing database mixins for common functionalities."""

from datetime import datetime

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column


class IdMixin:
    """Mixin class providing an auto-incrementing integer primary key attribute."""

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
        nullable=False,
        comment="Auto-incrementing primary key",
    )


class TimestampMixin:
    """A mixin class to add created_at and modified_at timestamp fields."""

    created_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True),
        server_default=sa.sql.func.now(),
        nullable=False,
        comment="Timestamp when the record was created",
    )
    modified_at: Mapped[datetime | None] = mapped_column(
        sa.DateTime(timezone=True),
        default=None,
        nullable=True,
        onupdate=sa.sql.func.now(),
        comment="Timestamp when the record was last modified",
    )


class CommonMixin(IdMixin, TimestampMixin):
    """A mixin providing common columns for SQLAlchemy models."""
