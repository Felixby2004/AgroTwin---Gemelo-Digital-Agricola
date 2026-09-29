from datetime import date

import pytest

from engines.et0 import (
    ET0Calculator,
    ET0Input,
)


def build_et0_input():
    return ET0Input(
        calculation_date=date(
            2026,
            8,
            1,
        ),

        latitude_deg=-6.77,
        elevation_m=30.0,

        temperature_mean_c=25.5,
        temperature_min_c=20.0,
        temperature_max_c=31.0,

        relative_humidity_pct=65.0,

        solar_radiation_mj_m2_day=18.5,

        wind_speed_m_s=2.0,
    )


def test_et0_is_positive():

    calculator = ET0Calculator()

    result = calculator.calculate(
        build_et0_input()
    )

    assert result.et0_mm_day > 0


def test_vapor_pressure_deficit_is_non_negative():

    calculator = ET0Calculator()

    result = calculator.calculate(
        build_et0_input()
    )

    assert (
        result.vapor_pressure_deficit_kpa
        >= 0
    )


def test_net_radiation_is_calculated():

    calculator = ET0Calculator()

    result = calculator.calculate(
        build_et0_input()
    )

    assert (
        result.net_radiation_mj_m2_day
        > 0
    )


def test_invalid_temperature_range():

    data = build_et0_input()

    data.temperature_min_c = 35.0
    data.temperature_max_c = 20.0

    calculator = ET0Calculator()

    with pytest.raises(ValueError):
        calculator.calculate(
            data
        )


def test_invalid_humidity():

    data = build_et0_input()

    data.relative_humidity_pct = 120

    calculator = ET0Calculator()

    with pytest.raises(ValueError):
        calculator.calculate(
            data
        )