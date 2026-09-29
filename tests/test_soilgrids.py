import pytest

from integrations.soilgrids import (
    SoilGridsClient,
)


def build_soilgrids_payload():

    return {
        "properties": {
            "layers": [
                {
                    "name": "sand",
                    "depths": [
                        {
                            "label": "0-5cm",
                            "values": {
                                "mean": 450
                            },
                        },
                        {
                            "label": "5-15cm",
                            "values": {
                                "mean": 430
                            },
                        },
                        {
                            "label": "15-30cm",
                            "values": {
                                "mean": 400
                            },
                        },
                    ],
                },
                {
                    "name": "silt",
                    "depths": [
                        {
                            "label": "0-5cm",
                            "values": {
                                "mean": 350
                            },
                        },
                        {
                            "label": "5-15cm",
                            "values": {
                                "mean": 370
                            },
                        },
                        {
                            "label": "15-30cm",
                            "values": {
                                "mean": 390
                            },
                        },
                    ],
                },
                {
                    "name": "clay",
                    "depths": [
                        {
                            "label": "0-5cm",
                            "values": {
                                "mean": 200
                            },
                        },
                        {
                            "label": "5-15cm",
                            "values": {
                                "mean": 200
                            },
                        },
                        {
                            "label": "15-30cm",
                            "values": {
                                "mean": 210
                            },
                        },
                    ],
                },
                {
                    "name": "bdod",
                    "depths": [
                        {
                            "label": "0-5cm",
                            "values": {
                                "mean": 130
                            },
                        }
                    ],
                },
                {
                    "name": "soc",
                    "depths": [
                        {
                            "label": "0-5cm",
                            "values": {
                                "mean": 180
                            },
                        }
                    ],
                },
                {
                    "name": "phh2o",
                    "depths": [
                        {
                            "label": "0-5cm",
                            "values": {
                                "mean": 65
                            },
                        }
                    ],
                },
            ]
        }
    }


def test_parse_soilgrids():

    client = SoilGridsClient()

    result = client._parse_response(
        payload=build_soilgrids_payload(),
        latitude=-6.77,
        longitude=-79.84,
    )

    assert len(result.layers) == 3

    first = result.layers[0]

    assert first.sand_pct == 45.0

    assert first.silt_pct == 35.0

    assert first.clay_pct == 20.0

    assert (
        first.bulk_density_g_cm3
        ==
        1.30
    )

    assert (
        first.organic_carbon_g_kg
        ==
        18.0
    )

    assert first.ph_h2o == 6.5


def test_invalid_coordinates():

    client = SoilGridsClient()

    with pytest.raises(ValueError):
        client._validate_coordinates(
            120,
            -79,
        )


def test_soil_profile_summary():

    client = SoilGridsClient()

    profile = client._parse_response(
        payload=build_soilgrids_payload(),
        latitude=-6.77,
        longitude=-79.84,
    )

    summary = profile.summarize(
        max_depth_cm=30
    )

    assert summary.depth_cm == 30

    assert summary.sand_pct is not None

    assert summary.clay_pct is not None