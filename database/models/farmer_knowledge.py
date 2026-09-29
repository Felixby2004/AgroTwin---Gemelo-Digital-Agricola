from datetime import datetime

from sqlalchemy import (
    DateTime,
    Float,
    ForeignKey,
    JSON,
    String,
    Text,
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
)

from database.base import (
    Base,
)


class FarmerKnowledgeModel(Base):

    __tablename__ = (
        "farmer_knowledge"
    )


    id: Mapped[str] = mapped_column(
        String(100),
        primary_key=True,
    )


    parcel_id: Mapped[str | None] = (
        mapped_column(
            ForeignKey(
                "parcels.id",
                ondelete="CASCADE",
            ),
            nullable=True,
        )
    )


    knowledge_type: Mapped[str] = (
        mapped_column(
            String(50),
            nullable=False,
            index=True,
        )
    )


    source_id: Mapped[str] = (
        mapped_column(
            String(100),
            nullable=False,
        )
    )


    source_role: Mapped[str] = (
        mapped_column(
            String(100),
            nullable=False,
        )
    )


    payload: Mapped[dict] = (
        mapped_column(
            JSON,
            nullable=False,
        )
    )


    created_at: Mapped[datetime] = (
        mapped_column(
            DateTime(
                timezone=True
            ),
            nullable=False,
        )
    )


    valid_from: Mapped[
        datetime | None
    ] = mapped_column(
        DateTime(
            timezone=True
        ),
        nullable=True,
    )


    valid_until: Mapped[
        datetime | None
    ] = mapped_column(
        DateTime(
            timezone=True
        ),
        nullable=True,
    )


    reported_confidence: Mapped[
        float | None
    ] = mapped_column(
        Float,
        nullable=True,
    )


    validation_status: Mapped[str] = (
        mapped_column(
            String(50),
            nullable=False,
        )
    )


    constraint_type: Mapped[
        str | None
    ] = mapped_column(
        String(50),
        nullable=True,
    )


    affects: Mapped[list | None] = (
        mapped_column(
            JSON,
            nullable=True,
        )
    )


    rationale: Mapped[
        str | None
    ] = mapped_column(
        Text,
        nullable=True,
    )


    metadata_json: Mapped[
        dict | None
    ] = mapped_column(
        "metadata",
        JSON,
        nullable=True,
    )