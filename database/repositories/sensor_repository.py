from sqlalchemy import (
    select,
)

from sqlalchemy.orm import (
    Session,
)

from database.models.sensor import (
    SensorModel,
)


class SensorRepository:

    def __init__(
        self,
        session: Session,
    ) -> None:

        self.session = session


    def create(
        self,
        *,
        sensor_id: str,
        parcel_id: str,
        name: str,
        sensor_type: str,
        variables: list[str],
        latitude: float | None = None,
        longitude: float | None = None,
        manufacturer: str | None = None,
        model_name: str | None = None,
        installed_at=None,
        is_active: bool = True,
        metadata: dict | None = None,
    ) -> SensorModel:

        item = SensorModel(
            id=sensor_id,
            parcel_id=parcel_id,
            name=name,
            sensor_type=sensor_type,
            variables=variables,
            latitude=latitude,
            longitude=longitude,
            manufacturer=manufacturer,
            model_name=model_name,
            installed_at=installed_at,
            is_active=is_active,
            metadata_json=metadata or {},
        )

        self.session.add(
            item
        )

        self.session.flush()

        return item


    def get_by_id(
        self,
        sensor_id: str,
    ) -> SensorModel | None:

        return self.session.get(
            SensorModel,
            sensor_id,
        )


    def list_all(
        self,
    ) -> list[SensorModel]:

        statement = (
            select(
                SensorModel
            )
            .order_by(
                SensorModel
                .created_at
                .desc()
            )
        )

        return list(
            self.session
            .scalars(
                statement
            )
            .all()
        )


    def list_by_parcel(
        self,
        parcel_id: str,
    ) -> list[SensorModel]:

        statement = (
            select(
                SensorModel
            )
            .where(
                SensorModel.parcel_id
                == parcel_id
            )
            .order_by(
                SensorModel
                .name
                .asc()
            )
        )

        return list(
            self.session
            .scalars(
                statement
            )
            .all()
        )


    def update(
        self,
        item: SensorModel,
        *,
        name: str,
        sensor_type: str,
        variables: list[str],
        latitude: float | None,
        longitude: float | None,
        manufacturer: str | None,
        model_name: str | None,
        installed_at,
        is_active: bool,
        metadata: dict | None,
    ) -> SensorModel:

        item.name = name
        item.sensor_type = sensor_type
        item.variables = variables
        item.latitude = latitude
        item.longitude = longitude
        item.manufacturer = manufacturer
        item.model_name = model_name
        item.installed_at = installed_at
        item.is_active = is_active
        item.metadata_json = metadata or {}

        self.session.flush()

        return item


    def ensure_from_reading(
        self,
        *,
        sensor_id: str,
        parcel_id: str,
        variable: str,
        latitude: float | None,
        longitude: float | None,
    ) -> SensorModel:

        item = self.get_by_id(
            sensor_id
        )

        if item is None:

            return self.create(
                sensor_id=sensor_id,
                parcel_id=parcel_id,
                name=sensor_id,
                sensor_type="GENERIC_IOT",
                variables=[variable],
                latitude=latitude,
                longitude=longitude,
                metadata={
                    "auto_registered":
                        True,
                },
            )


        if (
            item.parcel_id
            != parcel_id
        ):

            raise ValueError(
                "Sensor is already registered "
                "to another parcel."
            )


        variables = list(
            item.variables
            or []
        )

        if (
            variable
            not in variables
        ):

            variables.append(
                variable
            )

            item.variables = (
                variables
            )


        if (
            item.latitude is None
            and latitude is not None
        ):

            item.latitude = latitude


        if (
            item.longitude is None
            and longitude is not None
        ):

            item.longitude = longitude


        self.session.flush()

        return item
