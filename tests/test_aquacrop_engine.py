from datetime import datetime

import pandas as pd
import pytest

from engines.aquacrop_engine import (
    AquaCropEngine,
    AquaCropEngineError,
)

from twin import (
    Soil,
    WeatherState,
)


def build_soil():

    return Soil(
        soil_type=None,

        sand_pct=61.37,
        silt_pct=18.95,
        clay_pct=19.68,

        field_capacity=0.252,
        wilting_point=0.096,

        saturation=None,

        bulk_density_g_cm3=1.35,

        root_zone_depth_m=0.30,
    )


def build_weather():

    return [
        WeatherState(
            timestamp=datetime(
                2026,
                8,
                2,
            ),

            temperature_c=22.84,
            temperature_min_c=21.69,
            temperature_max_c=24.39,

            relative_humidity_pct=82.4,

            rainfall_mm=0.02,

            solar_radiation_mj_m2_day=14.63,

            wind_speed_m_s=4.36,

            et0_mm_day=3.19,

            source="NASA_POWER",
        ),

        WeatherState(
            timestamp=datetime(
                2026,
                8,
                3,
            ),

            temperature_c=22.92,
            temperature_min_c=21.63,
            temperature_max_c=24.54,

            relative_humidity_pct=82.4,

            rainfall_mm=0.0,

            solar_radiation_mj_m2_day=15.64,

            wind_speed_m_s=4.09,

            et0_mm_day=3.28,

            source="NASA_POWER",
        ),
    ]


def test_map_soil():

    engine = AquaCropEngine()

    result = engine.map_soil(
        build_soil()
    )

    assert result.sand_pct == 61.37
    assert result.clay_pct == 19.68

    assert result.field_capacity == 0.252
    assert result.wilting_point == 0.096


def test_map_weather():

    engine = AquaCropEngine()

    df = engine.map_weather(
        build_weather()
    )

    assert list(
        df.columns
    ) == [
        "MinTemp",
        "MaxTemp",
        "Precipitation",
        "ReferenceET",
        "Date",
    ]

    assert len(df) == 2

    assert (
        df.iloc[0]["MinTemp"]
        ==
        21.69
    )

    assert (
        df.iloc[0]["ReferenceET"]
        ==
        3.19
    )

    assert pd.api.types.is_datetime64_any_dtype(
        df["Date"]
    )


def test_weather_without_min_temperature():

    weather = build_weather()

    weather[0].temperature_min_c = None

    engine = AquaCropEngine()

    with pytest.raises(
        AquaCropEngineError
    ):
        engine.map_weather(
            weather
        )