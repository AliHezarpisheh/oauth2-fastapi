"""Module containing database models related to confidential clients."""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.oauth2.helpers.enums import ClientStatusEnum, ClientTokenEndpointAuthMethodEnum
from toolkit.database import Base, CommonMixin
from toolkit.database.annotations import str63, str255

if TYPE_CHECKING:
    from .scope import Scope
else:
    Scope = "Scope"


class Client(CommonMixin, Base):
    """Model representing confidential clients in Oauth 2.0 framework."""

    # Configuration
    __tablename__ = "client"
    __table_args__ = (
        sa.Index("client_client_id_status_idx", "client_id", "status"),
        {"schema": "oauth2"},
    )

    # Columns
    client_id: Mapped[uuid.UUID] = mapped_column(
        server_default=sa.text("gen_random_uuid()"),
        nullable=False,
        unique=True,
        comment="The identifier of the confidential client, different from the `id`.",
    )
    client_secret: Mapped[str255] = mapped_column(
        nullable=False,
        comment="Hashed secret of the client.",
    )
    client_name: Mapped[str63] = mapped_column(
        nullable=False,
        comment=(
            "Just a name for debugging purposes, no logic should be created upon it."
        ),
    )
    client_email: Mapped[str255] = mapped_column(
        nullable=False,
        comment="Needed to inform the client about events, e.g. password rotation.",
    )
    status: Mapped[ClientStatusEnum] = mapped_column(
        nullable=False,
        server_default=ClientStatusEnum.ACTIVE.name,
        comment="Can disable some clients.",
    )
    token_endpoint_auth_method: Mapped[ClientTokenEndpointAuthMethodEnum] = (
        mapped_column(
            nullable=False,
            server_default=ClientTokenEndpointAuthMethodEnum.CLIENT_SECRET_BASIC.name,
            comment=(
                "Specify different ways a confidential client can authenticate itself."
            ),
        )
    )
    last_secret_rotation: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True),
        nullable=True,
        comment=(
            "Recording the credential rotation time, as an security operational "
            "practice."
        ),
    )

    # Relationships
    scopes: Mapped[list[Scope]] = relationship(
        secondary="oauth2.client_scope", back_populates="clients"
    )
