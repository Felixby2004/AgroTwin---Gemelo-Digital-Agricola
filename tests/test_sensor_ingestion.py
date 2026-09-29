from datetime import (
    datetime,
    timezone,
)

import pytest


from api.schemas.sensor import (
    SensorReadingCreate,
    SensorVariable,
)

from services.sensor_ingestion_service import (
    SensorIngestionService,
)


service = SensorIngestionService()


def test_soil_moisture_mapping():

    reading = SensorReadingCreate(
        parcel_id="PARCEL-TEST",
        sensor_id="SM-001",
        variable=(
            SensorVariable
            .SOIL_MOISTURE
        ),
        value=0.21,
        unit="m3/m3",
        observed_at=(
            datetime.now(
                timezone.utc
            )
        ),
        quality_score=0.95,
    )


    result = service.normalize(
        reading
    )


    assert (
        result[
            "canonical_variable"
        ]
        ==
        "soil_water_state"
    )

    assert (
        result["value"][
            "soil_moisture"
        ]
        ==
        0.21
    )

    assert (
        result["provenance"][
            "source_type"
        ]
        ==
        "MEASURED"
    )


def test_invalid_soil_moisture():

    reading = SensorReadingCreate(
        parcel_id="PARCEL-TEST",
        sensor_id="SM-001",
        variable=(
            SensorVariable
            .SOIL_MOISTURE
        ),
        value=1.4,
        unit="m3/m3",
        observed_at=(
            datetime.now(
                timezone.utc
            )
        ),
    )


    with pytest.raises(
        ValueError
    ):

        service.normalize(
            reading
        )


def test_relative_humidity():

    reading = SensorReadingCreate(
        parcel_id="PARCEL-TEST",
        sensor_id="RH-001",
        variable=(
            SensorVariable
            .RELATIVE_HUMIDITY
        ),
        value=65.0,
        unit="%",
        observed_at=(
            datetime.now(
                timezone.utc
            )
        ),
    )


    result = service.normalize(
        reading
    )

    assert (
        result[
            "canonical_variable"
        ]
        ==
        "relative_humidity"
    )

    assert (
        result["value"]
        ==
        65.0
    )


def test_invalid_sensor_unit():

    reading = SensorReadingCreate(
        parcel_id="PARCEL-TEST",
        sensor_id="SM-001",
        variable=(
            SensorVariable
            .SOIL_MOISTURE
        ),
        value=0.20,
        unit="kg",
        observed_at=(
            datetime.now(
                timezone.utc
            )
        ),
    )


    with pytest.raises(
        ValueError
    ):

        service.normalize(
            reading
        )




from datetime import timedelta


def test_old_soil_moisture_is_stale():

    now = datetime(
        2026,
        9,
        15,
        12,
        0,
        tzinfo=timezone.utc,
    )

    reading = SensorReadingCreate(
        parcel_id="PARCEL-TEST",
        sensor_id="SM-OLD-001",

        variable=(
            SensorVariable
            .SOIL_MOISTURE
        ),

        value=0.18,

        unit="m3/m3",

        observed_at=(
            now
            - timedelta(
                hours=8
            )
        ),
    )


    result = service.normalize(
        reading,
        now=now,
    )


    assert (
        result["status"]
        ==
        "STALE"
    )


def test_recent_soil_moisture_is_active():

    now = datetime(
        2026,
        9,
        15,
        12,
        0,
        tzinfo=timezone.utc,
    )

    reading = SensorReadingCreate(
        parcel_id="PARCEL-TEST",
        sensor_id="SM-NEW-001",

        variable=(
            SensorVariable
            .SOIL_MOISTURE
        ),

        value=0.22,

        unit="m3/m3",

        observed_at=(
            now
            - timedelta(
                hours=2
            )
        ),
    )


    result = service.normalize(
        reading,
        now=now,
    )


    assert (
        result["status"]
        ==
        "ACTIVE"
    )


def test_sensor_batch():

    now = datetime(
        2026,
        9,
        15,
        12,
        0,
        tzinfo=timezone.utc,
    )


    readings = [

        SensorReadingCreate(
            parcel_id="PARCEL-TEST",
            sensor_id="SM-001",

            variable=(
                SensorVariable
                .SOIL_MOISTURE
            ),

            value=0.23,

            unit="m3/m3",

            observed_at=(
                now
                - timedelta(
                    hours=1
                )
            ),
        ),


        SensorReadingCreate(
            parcel_id="PARCEL-TEST",
            sensor_id="TEMP-001",

            variable=(
                SensorVariable
                .AIR_TEMPERATURE
            ),

            value=25.0,

            unit="degC",

            observed_at=(
                now
                - timedelta(
                    hours=1
                )
            ),
        ),


        SensorReadingCreate(
            parcel_id="PARCEL-TEST",
            sensor_id="RAIN-OLD",

            variable=(
                SensorVariable
                .RAINFALL
            ),

            value=2.0,

            unit="mm",

            observed_at=(
                now
                - timedelta(
                    hours=30
                )
            ),
        ),
    ]


    results = (
        service.normalize_batch(
            readings,
            now=now,
        )
    )


    assert len(
        results
    ) == 3

    assert (
        results[0]["status"]
        ==
        "ACTIVE"
    )

    assert (
        results[1]["status"]
        ==
        "ACTIVE"
    )

    assert (
        results[2]["status"]
        ==
        "STALE"
    )


def test_future_reading_is_rejected():

    now = datetime(
        2026,
        9,
        15,
        12,
        0,
        tzinfo=timezone.utc,
    )

    reading = SensorReadingCreate(
        parcel_id="PARCEL-TEST",
        sensor_id="SM-FUTURE",

        variable=(
            SensorVariable
            .SOIL_MOISTURE
        ),

        value=0.20,

        unit="m3/m3",

        observed_at=(
            now
            + timedelta(
                hours=1
            )
        ),
    )


    with pytest.raises(
        ValueError
    ):

        service.normalize(
            reading,
            now=now,
        )