from __future__ import annotations

from datetime import (
    datetime,
)

from sqlalchemy import (
    or_,
    select,
)

from sqlalchemy.orm import (
    Session,
)

from database.models.evidence import (
    MachineEvidenceModel,
)


class MachineEvidenceRepository:

    def __init__(
        self,
        session: Session,
    ) -> None:

        self.session = session


    # ==================================================
    # PARCEL HISTORY
    # ==================================================

    def list_parcel_history(
        self,
        parcel_id: str,
        *,
        start_at: datetime | None = None,
        end_at: datetime | None = None,
        variables: list[str] | None = None,
        active_only: bool = True,
    ) -> list[MachineEvidenceModel]:

        statement = (
            select(
                MachineEvidenceModel
            )
            .where(
                MachineEvidenceModel.parcel_id
                == parcel_id
            )
        )


        if active_only:

            statement = statement.where(
                MachineEvidenceModel.status
                == "ACTIVE"
            )


        if start_at is not None:

            statement = statement.where(
                MachineEvidenceModel.observed_at
                >= start_at
            )


        if end_at is not None:

            statement = statement.where(
                MachineEvidenceModel.observed_at
                <= end_at
            )


        if variables:

            statement = statement.where(
                MachineEvidenceModel.variable
                .in_(
                    variables
                )
            )


        statement = statement.order_by(
            MachineEvidenceModel.observed_at.asc()
        )


        return list(
            self.session
            .scalars(
                statement
            )
            .all()
        )


    # ==================================================
    # LATEST OBSERVATION
    # ==================================================

    def get_latest(
        self,
        parcel_id: str,
        variable: str,
    ) -> MachineEvidenceModel | None:

        statement = (
            select(
                MachineEvidenceModel
            )
            .where(
                MachineEvidenceModel.parcel_id
                == parcel_id
            )
            .where(
                MachineEvidenceModel.variable
                == variable
            )
            .where(
                MachineEvidenceModel.status
                == "ACTIVE"
            )
            .where(
                MachineEvidenceModel.observed_at
                .is_not(None)
            )
            .order_by(
                MachineEvidenceModel.observed_at.desc()
            )
            .limit(1)
        )


        return (
            self.session
            .scalars(
                statement
            )
            .first()
        )


    # ==================================================
    # SENSOR HISTORY
    # ==================================================

    def list_sensor_history(
        self,
        sensor_id: str,
        *,
        limit: int = 100,
    ) -> list[MachineEvidenceModel]:

        statement = (
            select(
                MachineEvidenceModel
            )
            .where(
                or_(
                    MachineEvidenceModel
                    .metadata_json[
                        "sensor_id"
                    ]
                    .as_string()
                    == sensor_id,

                    MachineEvidenceModel
                    .provenance[
                        "source_id"
                    ]
                    .as_string()
                    == sensor_id,
                )
            )
            .order_by(
                MachineEvidenceModel
                .observed_at
                .desc()
            )
            .limit(
                limit
            )
        )


        return list(
            self.session
            .scalars(
                statement
            )
            .all()
        )


    def get_sensor_latest(
        self,
        sensor_id: str,
    ) -> MachineEvidenceModel | None:

        history = (
            self.list_sensor_history(
                sensor_id,
                limit=1,
            )
        )

        return (
            history[0]
            if history
            else None
        )
