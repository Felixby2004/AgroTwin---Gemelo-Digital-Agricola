from datetime import datetime

from sqlalchemy import (
    String,
    DateTime,
    ForeignKey,
    JSON,
    UniqueConstraint,
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
)

from database.base import Base


class UserModel(
    Base
):

    __tablename__ = "users"


    id: Mapped[str] = mapped_column(
        String,
        primary_key=True,
    )


    email: Mapped[str] = mapped_column(
        String,
        nullable=False,
        unique=True,
        index=True,
    )


    full_name: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )


    password_hash: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )


    system_role: Mapped[str] = mapped_column(
        String,
        nullable=False,
        default="USER",
    )


    status: Mapped[str] = mapped_column(
        String,
        nullable=False,
        default="ACTIVE",
    )


    created_at: Mapped[datetime] = mapped_column(
        DateTime(
            timezone=True
        ),
        nullable=False,
    )


    metadata_json: Mapped[
        dict | None
    ] = mapped_column(
        JSON,
        nullable=True,
    )


class ParcelMembershipModel(
    Base
):

    __tablename__ = (
        "parcel_memberships"
    )


    __table_args__ = (

        UniqueConstraint(
            "parcel_id",
            "user_id",
            name=(
                "uq_parcel_membership_"
                "parcel_user"
            ),
        ),
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


    user_id: Mapped[str] = mapped_column(
        String,
        ForeignKey(
            "users.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )


    role: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )


    created_at: Mapped[datetime] = mapped_column(
        DateTime(
            timezone=True
        ),
        nullable=False,
    )


    metadata_json: Mapped[
        dict | None
    ] = mapped_column(
        JSON,
        nullable=True,
    )