from datetime import datetime
from uuid import uuid4

from sqlalchemy import (
    DateTime,
    Float,
    String,
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
)

from geoalchemy2 import (
    Geometry,
)

from database.base import (
    Base,
)


class ParcelModel(Base):

    __tablename__ = "parcels"


    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(
            uuid4()
        ),
    )


    name: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )


    crop_type: Mapped[str | None] = (
        mapped_column(
            String(100),
            nullable=True,
        )
    )


    area_ha: Mapped[float | None] = (
        mapped_column(
            Float,
            nullable=True,
        )
    )


    geometry = mapped_column(
        Geometry(
            geometry_type="POLYGON",
            srid=4326,
            spatial_index=False,
        ),
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