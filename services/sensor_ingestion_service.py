from datetime import (
    datetime,
    timezone,
)

from uuid import uuid4

from api.schemas.sensor import (
    SensorReadingCreate,
    SensorVariable,
)


class SensorIngestionService:

    # =====================================================
    # CANONICAL UNITS
    # =====================================================

    CANONICAL_UNITS = {
        SensorVariable.SOIL_MOISTURE:
            "m3/m3",

        SensorVariable.AIR_TEMPERATURE:
            "degC",

        SensorVariable.RELATIVE_HUMIDITY:
            "%",

        SensorVariable.RAINFALL:
            "mm",

        SensorVariable.FLOW_RATE:
            "L/min",
    }


    # =====================================================
    # FRESHNESS THRESHOLDS
    #
    # Operational defaults.
    # Later they can become configurable
    # per sensor / crop / deployment.
    # =====================================================

    FRESHNESS_HOURS = {
        SensorVariable.SOIL_MOISTURE:
            6,

        SensorVariable.AIR_TEMPERATURE:
            3,

        SensorVariable.RELATIVE_HUMIDITY:
            3,

        SensorVariable.RAINFALL:
            24,

        SensorVariable.FLOW_RATE:
            6,
    }


    # =====================================================
    # UNIT ALIASES
    # =====================================================

    UNIT_ALIASES = {

        # Soil moisture
        "m3/m3": "m3/m3",
        "m³/m³": "m3/m3",

        # Temperature
        "c": "degC",
        "°c": "degC",
        "degc": "degC",

        # Relative humidity
        "%": "%",

        # Rainfall
        "mm": "mm",

        # Flow
        "l/min": "L/min",
        "lpm": "L/min",
    }


    # =====================================================
    # NORMALIZE ONE READING
    # =====================================================

    def normalize(
        self,
        reading: SensorReadingCreate,
        now: datetime | None = None,
    ) -> dict:

        variable = (
            reading.variable
        )

        normalized_unit = (
            self._normalize_unit(
                reading.unit
            )
        )

        expected_unit = (
            self.CANONICAL_UNITS[
                variable
            ]
        )


        if (
            normalized_unit
            != expected_unit
        ):
            raise ValueError(
                f"Invalid unit for "
                f"{variable.value}. "
                f"Expected {expected_unit}, "
                f"received {reading.unit}."
            )


        self._validate_value(
            variable=variable,
            value=reading.value,
        )


        observed_at = (
            self._ensure_timezone(
                reading.observed_at
            )
        )


        if now is None:

            now = datetime.now(
                timezone.utc
            )

        else:

            now = (
                self._ensure_timezone(
                    now
                )
            )


        # Small clock differences between
        # sensor and server are tolerated.
        future_seconds = (
            observed_at
            - now
        ).total_seconds()

        if future_seconds > 600:

            raise ValueError(
                "observed_at cannot be "
                "more than 10 minutes "
                "in the future."
            )


        status = (
            self._determine_status(
                variable=variable,
                observed_at=observed_at,
                now=now,
            )
        )


        canonical_variable = (
            self._canonical_variable(
                variable
            )
        )


        canonical_value = (
            self._canonical_value(
                variable=variable,
                value=reading.value,
            )
        )


        evidence_id = (
            "EV-IOT-"
            + uuid4().hex[
                :12
            ].upper()
        )


        spatial_scope = None

        if (
            reading.latitude
            is not None
            and
            reading.longitude
            is not None
        ):

            spatial_scope = {
                "latitude":
                    reading.latitude,

                "longitude":
                    reading.longitude,
            }


        age_hours = max(
            0.0,
            (
                now
                - observed_at
            ).total_seconds()
            / 3600.0,
        )


        provenance = {
            "source_type":
                "MEASURED",

            "source_name":
                "IOT_SENSOR",

            "source_id":
                reading.sensor_id,

            "source_version":
                None,

            "generated_at":
                observed_at.isoformat(),

            "valid_at":
                observed_at.isoformat(),

            "spatial_scope":
                spatial_scope,

            "transformation":
                (
                    "IoT sensor reading "
                    "normalized to canonical "
                    "digital twin variable."
                ),

            "parent_ids":
                [],

            "metadata": {
                "input_variable":
                    variable.value,

                "input_unit":
                    reading.unit,

                "age_hours":
                    age_hours,

                "freshness_threshold_hours":
                    self.FRESHNESS_HOURS[
                        variable
                    ],

                **reading.metadata,
            },
        }


        return {
            "evidence_id":
                evidence_id,

            "parcel_id":
                reading.parcel_id,

            "sensor_id":
                reading.sensor_id,

            "input_variable":
                variable.value,

            "canonical_variable":
                canonical_variable,

            "value":
                canonical_value,

            "unit":
                expected_unit,

            "observed_at":
                observed_at,

            "status":
                status,

            "quality_score":
                reading.quality_score,

            "uncertainty":
                None,

            "provenance":
                provenance,

            "metadata": {
                "sensor_id":
                    reading.sensor_id,

                "ingestion_type":
                    "IOT",

                "age_hours":
                    age_hours,

                "freshness_threshold_hours":
                    self.FRESHNESS_HOURS[
                        variable
                    ],

                **reading.metadata,
            },
        }


    # =====================================================
    # NORMALIZE BATCH
    # =====================================================

    def normalize_batch(
        self,
        readings: list[
            SensorReadingCreate
        ],
        now: datetime | None = None,
    ) -> list[dict]:

        if now is None:

            now = datetime.now(
                timezone.utc
            )


        results = []

        for reading in readings:

            results.append(
                self.normalize(
                    reading=reading,
                    now=now,
                )
            )

        return results


    # =====================================================
    # STATUS
    # =====================================================

    def _determine_status(
        self,
        variable: SensorVariable,
        observed_at: datetime,
        now: datetime,
    ) -> str:

        age_hours = (
            now
            - observed_at
        ).total_seconds() / 3600.0


        threshold = (
            self.FRESHNESS_HOURS[
                variable
            ]
        )


        if age_hours > threshold:

            return "STALE"


        return "ACTIVE"


    # =====================================================
    # TIMEZONE
    # =====================================================

    def _ensure_timezone(
        self,
        value: datetime,
    ) -> datetime:

        if value.tzinfo is None:

            return value.replace(
                tzinfo=timezone.utc
            )

        return value.astimezone(
            timezone.utc
        )


    # =====================================================
    # CANONICAL VARIABLE
    # =====================================================

    def _canonical_variable(
        self,
        variable: SensorVariable,
    ) -> str:

        if (
            variable
            == SensorVariable.SOIL_MOISTURE
        ):
            return "soil_water_state"

        return variable.value


    # =====================================================
    # CANONICAL VALUE
    # =====================================================

    def _canonical_value(
        self,
        variable: SensorVariable,
        value: float,
    ):

        if (
            variable
            == SensorVariable.SOIL_MOISTURE
        ):
            return {
                "soil_moisture":
                    value,
            }

        return value


    # =====================================================
    # UNIT NORMALIZATION
    # =====================================================

    def _normalize_unit(
        self,
        unit: str,
    ) -> str:

        normalized = (
            unit
            .strip()
            .lower()
        )

        if (
            normalized
            not in self.UNIT_ALIASES
        ):
            raise ValueError(
                f"Unsupported unit: "
                f"{unit}."
            )

        return (
            self.UNIT_ALIASES[
                normalized
            ]
        )


    # =====================================================
    # PHYSICAL VALIDATION
    # =====================================================

    def _validate_value(
        self,
        variable: SensorVariable,
        value: float,
    ) -> None:

        if (
            variable
            == SensorVariable.SOIL_MOISTURE
        ):

            if not (
                0.0
                <= value
                <= 1.0
            ):
                raise ValueError(
                    "soil_moisture must "
                    "be between 0 and 1 m3/m3."
                )


        elif (
            variable
            == SensorVariable.RELATIVE_HUMIDITY
        ):

            if not (
                0.0
                <= value
                <= 100.0
            ):
                raise ValueError(
                    "relative_humidity must "
                    "be between 0 and 100%."
                )


        elif (
            variable
            == SensorVariable.RAINFALL
        ):

            if value < 0:

                raise ValueError(
                    "rainfall cannot "
                    "be negative."
                )


        elif (
            variable
            == SensorVariable.FLOW_RATE
        ):

            if value < 0:

                raise ValueError(
                    "flow_rate cannot "
                    "be negative."
                )


        elif (
            variable
            == SensorVariable.AIR_TEMPERATURE
        ):

            if not (
                -60.0
                <= value
                <= 70.0
            ):

                raise ValueError(
                    "air_temperature is "
                    "outside supported "
                    "physical limits."
                )