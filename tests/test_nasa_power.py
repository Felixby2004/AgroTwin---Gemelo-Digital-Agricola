from integrations.nasa_power import (
    NASAPowerClient,
)
from datetime import datetime
from twin import WeatherState


def test_parse_daily_response():

    payload = {
        "properties": {
            "parameter": {
                "T2M": {
                    "20260901": 25.4,
                    "20260902": 26.1,
                },
                "T2M_MIN": {
                    "20260901": 20.1,
                    "20260902": 20.6,
                },
                "T2M_MAX": {
                    "20260901": 31.2,
                    "20260902": 32.0,
                },
                "RH2M": {
                    "20260901": 65.0,
                    "20260902": 63.0,
                },
                "PRECTOTCORR": {
                    "20260901": 2.4,
                    "20260902": 0.0,
                },
                "WS2M": {
                    "20260901": 2.1,
                    "20260902": 2.5,
                },
                "ALLSKY_SFC_SW_DWN": {
                    "20260901": 18.5,
                    "20260902": 19.2,
                },
            }
        }
    }

    client = NASAPowerClient()

    result = client._parse_daily_response(
        payload
    )

    assert len(result) == 2

    assert (
        result[0].temperature_c
        ==
        25.4
    )

    assert (
        result[0].rainfall_mm
        ==
        2.4
    )

    assert (
        result[0].source
        ==
        "NASA_POWER"
    )


def test_missing_value_is_none():

    payload = {
        "properties": {
            "parameter": {
                "T2M": {
                    "20260901": 25.4,
                },
                "T2M_MIN": {
                    "20260901": -999.0,
                },
                "T2M_MAX": {
                    "20260901": 31.2,
                },
                "RH2M": {
                    "20260901": 65.0,
                },
                "PRECTOTCORR": {
                    "20260901": 0.0,
                },
                "WS2M": {
                    "20260901": 2.1,
                },
                "ALLSKY_SFC_SW_DWN": {
                    "20260901": 18.5,
                },
            }
        }
    }

    client = NASAPowerClient()

    result = client._parse_daily_response(
        payload
    )

    assert (
        result[0].temperature_min_c
        is None
    )


import pytest


def test_invalid_latitude():

    client = NASAPowerClient()

    with pytest.raises(ValueError):
        client._validate_coordinates(
            100,
            -79,
        )


def test_invalid_longitude():

    client = NASAPowerClient()

    with pytest.raises(ValueError):
        client._validate_coordinates(
            -6,
            -190,
        )


def test_add_et0():

    client = NASAPowerClient()

    weather = WeatherState(
        timestamp=datetime(
            2026,
            8,
            1,
        ),

        temperature_c=25.5,

        temperature_min_c=20.0,
        temperature_max_c=31.0,

        relative_humidity_pct=65.0,

        rainfall_mm=0.0,

        solar_radiation_mj_m2_day=18.5,

        wind_speed_m_s=2.0,

        source="NASA_POWER",
    )

    result = client.add_et0(
        weather_series=[
            weather
        ],
        latitude=-6.77,
        elevation_m=30.0,
    )

    assert len(result) == 1

    assert (
        result[0].et0_mm_day
        is not None
    )

    assert (
        result[0].et0_mm_day
        > 0
    )

    assert (
        result[0].quality_flag
        ==
        "ET0_FAO56_ESTIMATED"
    )