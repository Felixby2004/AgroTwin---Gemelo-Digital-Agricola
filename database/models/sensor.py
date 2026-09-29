from datetime import (
    datetime,
)

from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    JSON,
    String,
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
)

from database.base import (
    Base,
)


class SensorModel(Base):

    __tablename__ = "sensors"


    id: Mapped[str] = mapped_column(
        String(100),
        primary_key=True,
    )


    parcel_id: Mapped[str] = mapped_column(
        ForeignKey(
            "parcels.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )


    name: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )


    sensor_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )


    variables: Mapped[list] = mapped_column(
        JSON,
        nullable=False,
        default=list,
    )


    latitude: Mapped[float | None] = (
        mapped_column(
            Float,
            nullable=True,
        )
    )


    longitude: Mapped[float | None] = (
        mapped_column(
            Float,
            nullable=True,
        )
    )


    manufacturer: Mapped[str | None] = (
        mapped_column(
            String(120),
            nullable=True,
        )
    )


    model_name: Mapped[str | None] = (
        mapped_column(
            "model",
            String(120),
            nullable=True,
        )
    )


    installed_at: Mapped[
        datetime | None
    ] = mapped_column(
        DateTime(
            timezone=True
        ),
        nullable=True,
    )


    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
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


    updated_at: Mapped[datetime] = (
        mapped_column(
            DateTime(
                timezone=True
            ),
            default=datetime.utcnow,
            onupdate=datetime.utcnow,
            nullable=False,
        )
    )
