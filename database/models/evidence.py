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


class MachineEvidenceModel(Base):

    __tablename__ = (
        "machine_evidence"
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


    variable: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
        index=True,
    )


    value: Mapped[dict] = mapped_column(
        JSON,
        nullable=False,
    )


    unit: Mapped[str | None] = (
        mapped_column(
            String(50),
            nullable=True,
        )
    )


    observed_at: Mapped[
        datetime | None
    ] = mapped_column(
        DateTime(
            timezone=True
        ),
        nullable=True,
        index=True,
    )


    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )


    quality_score: Mapped[
        float | None
    ] = mapped_column(
        Float,
        nullable=True,
    )


    uncertainty: Mapped[
        dict | None
    ] = mapped_column(
        JSON,
        nullable=True,
    )


    provenance: Mapped[dict] = (
        mapped_column(
            JSON,
            nullable=False,
        )
    )


    metadata_json: Mapped[
        dict | None
    ] = mapped_column(
        "metadata",
        JSON,
        nullable=True,
    )


    created_at: Mapped[datetime] = (
        mapped_column(
            DateTime(
                timezone=True
            ),
            default=datetime.utcnow,
            nullable=False,
        )
    )