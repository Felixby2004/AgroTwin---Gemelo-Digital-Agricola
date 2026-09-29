from datetime import datetime

from sqlalchemy import (
    String,
    DateTime,
    ForeignKey,
    JSON,
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
)

from database.base import (
    Base,
)


class DataConsentModel(
    Base
):

    __tablename__ = (
        "data_consents"
    )


    id: Mapped[str] = mapped_column(
        String,
        primary_key=True,
    )


    parcel_id: Mapped[str] = mapped_column(
        String,
        ForeignKey(
            "parcels.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )


    subject_id: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )


    purposes: Mapped[list] = mapped_column(
        JSON,
        nullable=False,
    )


    permissions: Mapped[list] = mapped_column(
        JSON,
        nullable=False,
    )


    allowed_data_categories: Mapped[
        list
    ] = mapped_column(
        JSON,
        nullable=False,
    )


    created_at: Mapped[
        datetime
    ] = mapped_column(
        DateTime(
            timezone=True
        ),
        nullable=False,
    )


    valid_until: Mapped[
        datetime | None
    ] = mapped_column(
        DateTime(
            timezone=True
        ),
        nullable=True,
    )


    status: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )


    metadata_json: Mapped[
        dict | None
    ] = mapped_column(
        JSON,
        nullable=True,
    )