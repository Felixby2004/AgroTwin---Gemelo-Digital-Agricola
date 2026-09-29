from datetime import datetime
from uuid import uuid4

from sqlalchemy import (
    DateTime,
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


class DecisionTraceModel(Base):

    __tablename__ = (
        "decision_traces"
    )


    id: Mapped[str] = mapped_column(
        String(100),
        primary_key=True,
        default=lambda: str(
            uuid4()
        ),
    )


    parcel_id: Mapped[
        str | None
    ] = mapped_column(
        ForeignKey(
            "parcels.id",
            ondelete="CASCADE",
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


    evidence_ids: Mapped[list] = (
        mapped_column(
            JSON,
            nullable=False,
            default=list,
        )
    )


    knowledge_ids: Mapped[list] = (
        mapped_column(
            JSON,
            nullable=False,
            default=list,
        )
    )


    conflict_ids: Mapped[list] = (
        mapped_column(
            JSON,
            nullable=False,
            default=list,
        )
    )


    transformation_ids: Mapped[
        list
    ] = mapped_column(
        JSON,
        nullable=False,
        default=list,
    )


    feasible_scenarios: Mapped[
        list
    ] = mapped_column(
        JSON,
        nullable=False,
        default=list,
    )


    rejected_scenarios: Mapped[
        list
    ] = mapped_column(
        JSON,
        nullable=False,
        default=list,
    )


    ranking: Mapped[list] = (
        mapped_column(
            JSON,
            nullable=False,
            default=list,
        )
    )


    provisional_recommendation: (
        Mapped[dict | None]
    ) = mapped_column(
        JSON,
        nullable=True,
    )


    farmer_response: Mapped[
        dict | None
    ] = mapped_column(
        JSON,
        nullable=True,
    )


    outcome: Mapped[
        dict | None
    ] = mapped_column(
        JSON,
        nullable=True,
    )


    metadata_json: Mapped[
        dict | None
    ] = mapped_column(
        "metadata",
        JSON,
        nullable=True,
    )