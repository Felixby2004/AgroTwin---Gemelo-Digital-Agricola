from datetime import (
    datetime,
    timezone,
    timedelta,
)

from services.sentinel2_service import (
    Sentinel2Service,
)


service = Sentinel2Service()


def test_ndvi():

    ndvi = service.calculate_ndvi(
        red=0.20,
        nir=0.60,
    )

    assert ndvi == 0.5


def test_ndmi():

    ndmi = service.calculate_ndmi(
        nir=0.60,
        swir=0.30,
    )

    assert ndmi == 0.333333


def test_sentinel_external_provenance():

    now = datetime.now(
        timezone.utc
    )

    result = service.build_evidence(
        parcel_id="PARCEL-001",

        scene_id="S2-TEST-001",

        acquired_at=now,

        red=0.20,

        nir=0.60,

        swir=0.30,

        cloud_cover_pct=5.0,

        source_url=None,

        processing_level="L2A",
    )


    assert len(
        result
    ) == 2

    assert (
        result[0][
            "provenance"
        ][
            "source_type"
        ]
        ==
        "EXTERNAL"
    )

    assert (
        result[0][
            "variable"
        ]
        ==
        "ndvi"
    )

    assert (
        result[1][
            "variable"
        ]
        ==
        "ndmi"
    )


def test_old_satellite_scene_is_stale():

    now = datetime(
        2026,
        9,
        15,
        tzinfo=timezone.utc,
    )

    acquired = (
        now
        - timedelta(
            days=20
        )
    )


    status = (
        service.determine_status(
            acquired_at=acquired,
            now=now,
        )
    )

    assert status == "STALE"


def test_cloud_quality():

    assert (
        service
        .quality_from_clouds(
            5.0
        )
        ==
        0.95
    )

    assert (
        service
        .quality_from_clouds(
            20.0
        )
        ==
        0.75
    )

    assert (
        service
        .quality_from_clouds(
            50.0
        )
        ==
        0.50
    )