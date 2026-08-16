"""Module containing database models related to initial access tokens."""

from datetime import datetime
from typing import TYPE_CHECKING

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

from toolkit.database import Base, CommonMixin
from toolkit.database.annotations import str255, text

if TYPE_CHECKING:
    from .client import Client
else:
    Client = "Client"


class InitialAccessToken(CommonMixin, Base):
    """Model representing initial access tokens needed for client registration."""

    # Configuration
    __tablename__ = "initial_access_token"
    __table_args__ = (
        sa.Index(None, "token_hash", unique=True),
        sa.Index(None, "expires_at"),
        sa.CheckConstraint("max_registration >= registrations_used"),
        sa.CheckConstraint("expires_at > now()"),
        {"schema": "oauth2"},
    )

    # Columns
    token_hash: Mapped[str255] = mapped_column(
        nullable=False,
        comment="Hashed initial access token, included in client registration request.",
    )
    expires_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True),
        nullable=False,
        comment="Set a expiration time for token, avoiding long-term abuse.",
    )
    max_registration: Mapped[int] = mapped_column(
        nullable=False,
        server_default=sa.text("1"),
        comment="A limit for the times user can use the token to create clients.",
    )
    registrations_used: Mapped[int] = mapped_column(
        nullable=False,
        server_default=sa.text("0"),
        comment=(
            "Times user has used the token. It should never get above "
            "`max_registration`."
        ),
    )
    note: Mapped[text] = mapped_column(
        nullable=True,
        comment="A note helping the admin or the end-user itself.",
    )
