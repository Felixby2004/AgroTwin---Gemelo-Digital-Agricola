from datetime import datetime

from sqlalchemy import (
    String,
    DateTime,
    ForeignKey,
    JSON,
    Boolean,
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
)

from database.base import Base


class DataAuditEventModel(
    Base
):

    __tablename__ = "data_audit_events"


    id: Mapped[str] = mapped_column(
        String,
        primary_key=True,
    )


    parcel_id: Mapped[str | None] = mapped_column(
        String,
        ForeignKey(
            "parcels.id",
            ondelete="SET NULL",
        ),
        nullable=True,
        index=True,
    )


    actor_id: Mapped[str] = mapped_column(
        String,
        nullable=False,
        index=True,
    )


    action: Mapped[str] = mapped_column(
        String,
        nullable=False,
        index=True,
    )


    allowed: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
    )


    consent_id: Mapped[str | None] = mapped_column(
        String,
        nullable=True,
    )


    purpose: Mapped[str | None] = mapped_column(
        String,
        nullable=True,
    )


    data_category: Mapped[str | None] = mapped_column(
        String,
        nullable=True,
    )


    created_at: Mapped[datetime] = mapped_column(
        DateTime(
            timezone=True
        ),
        nullable=False,
        index=True,
    )


    details: Mapped[dict | None] = mapped_column(
        JSON,
        nullable=True,
    )