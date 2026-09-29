import json

from sqlalchemy import (
    text,
)

from sqlalchemy.orm import (
    Session,
)

from database.models.parcel import (
    ParcelModel,
)


class ParcelRepository:

    def __init__(
        self,
        session: Session,
    ):

        self.session = session


    # ==================================================
    # CREATE
    # ==================================================

    def create(
        self,
        name: str,
        crop_type: str | None = None,
        area_ha: float | None = None,
        geometry=None,
    ) -> ParcelModel:

        item = ParcelModel(
            name=name,
            crop_type=crop_type,
            area_ha=area_ha,
            geometry=geometry,
        )

        self.session.add(
            item
        )

        self.session.flush()

        return item


    # ==================================================
    # GET BY ID
    # ==================================================

    def get_by_id(
        self,
        parcel_id: str,
    ) -> ParcelModel | None:

        return self.session.get(
            ParcelModel,
            parcel_id,
        )


    # ==================================================
    # LIST ALL
    # ==================================================

    def list_all(
        self,
    ) -> list[
        ParcelModel
    ]:

        return (
            self.session
            .query(
                ParcelModel
            )
            .order_by(
                ParcelModel
                .created_at
                .desc()
            )
            .all()
        )


    # ==================================================
    # UPDATE DETAILS
    # ==================================================

    def update_details(
        self,
        parcel_id: str,
        name: str,
        crop_type: str | None = None,
        area_ha: float | None = None,
    ) -> ParcelModel | None:

        item = self.get_by_id(
            parcel_id
        )

        if item is None:
            return None

        item.name = (
            name.strip()
        )

        item.crop_type = (
            crop_type.strip()
            if crop_type
            else None
        )

        item.area_ha = (
            area_ha
        )

        self.session.flush()

        return item


    # ==================================================
    # GET ONE GEOMETRY AS GEOJSON
    # ==================================================

    def get_geometry_geojson(
        self,
        parcel_id: str,
    ) -> dict | None:

        result = (
            self.session
            .execute(
                text(
                    """
                    SELECT
                        ST_AsGeoJSON(
                            CASE
                                WHEN ST_SRID(geometry) = 0
                                    THEN ST_SetSRID(
                                        geometry,
                                        4326
                                    )

                                WHEN ST_SRID(geometry) = 4326
                                    THEN geometry

                                ELSE ST_Transform(
                                    geometry,
                                    4326
                                )
                            END
                        ) AS geometry_geojson

                    FROM parcels

                    WHERE id = :parcel_id
                    """
                ),
                {
                    "parcel_id":
                        parcel_id,
                },
            )
            .scalar_one_or_none()
        )

        if result is None:

            return None

        return json.loads(
            result
        )


    # ==================================================
    # LIST PARCELS WITH GEOMETRY
    # ==================================================

    def list_with_geometry(
        self,
    ) -> list[dict]:

        rows = (
            self.session
            .execute(
                text(
                    """
                    SELECT
                        id,
                        name,
                        crop_type,
                        area_ha,

                        ST_AsGeoJSON(
                            CASE
                                WHEN ST_SRID(geometry) = 0
                                    THEN ST_SetSRID(
                                        geometry,
                                        4326
                                    )

                                WHEN ST_SRID(geometry) = 4326
                                    THEN geometry

                                ELSE ST_Transform(
                                    geometry,
                                    4326
                                )
                            END
                        ) AS geometry_geojson

                    FROM parcels

                    WHERE geometry IS NOT NULL
                      AND NOT ST_IsEmpty(
                          geometry
                      )

                    ORDER BY created_at DESC
                    """
                )
            )
            .mappings()
            .all()
        )

        result: list[
            dict
        ] = []

        for row in rows:

            geometry_raw = (
                row[
                    "geometry_geojson"
                ]
            )

            if geometry_raw is None:
                continue

            geometry = json.loads(
                geometry_raw
            )

            result.append(
                {
                    "id":
                        str(
                            row["id"]
                        ),

                    "name":
                        row["name"],

                    "crop_type":
                        row[
                            "crop_type"
                        ],

                    "area_ha":
                        (
                            float(
                                row[
                                    "area_ha"
                                ]
                            )
                            if row[
                                "area_ha"
                            ]
                            is not None
                            else None
                        ),

                    "geometry":
                        geometry,
                }
            )

        return result


    # ==================================================
    # UPDATE PARCEL GEOMETRY
    # ==================================================

    def update_geometry_geojson(
        self,
        parcel_id: str,
        geometry: dict,
    ) -> bool:

        geometry_type = (
            geometry.get(
                "type"
            )
        )


        if geometry_type != "Polygon":

            raise ValueError(
                "Only GeoJSON Polygon "
                "geometry is supported."
            )


        coordinates = (
            geometry.get(
                "coordinates"
            )
        )


        if (
            not isinstance(
                coordinates,
                list,
            )
            or
            len(coordinates) == 0
        ):

            raise ValueError(
                "Polygon coordinates "
                "are required."
            )


        exterior_ring = (
            coordinates[0]
        )


        if (
            not isinstance(
                exterior_ring,
                list,
            )
            or
            len(exterior_ring) < 4
        ):

            raise ValueError(
                "A polygon must contain "
                "at least three vertices "
                "plus the closing vertex."
            )


        geometry_json = json.dumps(
            geometry
        )


        validation = (
            self.session
            .execute(
                text(
                    """
                    SELECT
                        ST_IsValid(
                            ST_SetSRID(
                                ST_GeomFromGeoJSON(
                                    :geometry_json
                                ),
                                4326
                            )
                        ) AS is_valid,

                        ST_IsValidReason(
                            ST_SetSRID(
                                ST_GeomFromGeoJSON(
                                    :geometry_json
                                ),
                                4326
                            )
                        ) AS reason,

                        ST_GeometryType(
                            ST_SetSRID(
                                ST_GeomFromGeoJSON(
                                    :geometry_json
                                ),
                                4326
                            )
                        ) AS geometry_type
                    """
                ),
                {
                    "geometry_json":
                        geometry_json,
                },
            )
            .mappings()
            .one()
        )


        if (
            validation[
                "geometry_type"
            ]
            != "ST_Polygon"
        ):

            raise ValueError(
                "Geometry must be "
                "a Polygon."
            )


        if not validation[
            "is_valid"
        ]:

            raise ValueError(
                "Invalid polygon: "
                f"{validation['reason']}"
            )


        result = (
            self.session
            .execute(
                text(
                    """
                    UPDATE parcels

                    SET geometry =
                        ST_SetSRID(
                            ST_GeomFromGeoJSON(
                                :geometry_json
                            ),
                            4326
                        )

                    WHERE id =
                        :parcel_id

                    RETURNING id
                    """
                ),
                {
                    "parcel_id":
                        parcel_id,

                    "geometry_json":
                        geometry_json,
                },
            )
            .scalar_one_or_none()
        )


        return (
            result is not None
        )


    # ==================================================
    # REMOVE GEOMETRY
    # ==================================================

    def remove_geometry(
        self,
        parcel_id: str,
    ) -> bool:

        result = (
            self.session
            .execute(
                text(
                    """
                    UPDATE parcels

                    SET geometry = NULL

                    WHERE id =
                        :parcel_id

                    RETURNING id
                    """
                ),
                {
                    "parcel_id":
                        parcel_id,
                },
            )
            .scalar_one_or_none()
        )


        return (
            result is not None
        )