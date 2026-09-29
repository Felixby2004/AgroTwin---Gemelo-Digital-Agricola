from datetime import date, datetime, timedelta

from engines.simulation import TemporalSimulator
from tests.test_water_balance import build_test_state
from twin import WeatherState

def build_weather_series(days: int = 7):
    start = datetime(2026, 9, 8, 8, 0)

    weather_series = []

    for i in range(days):
        weather_series.append(
            WeatherState(
                timestamp=start + timedelta(days=i),
                temperature_c=30.0,
                relative_humidity_pct=60.0,
                rainfall_mm=0.0,
                solar_radiation_mj_m2_day=21.0,
                wind_speed_m_s=2.0,
                et0_mm_day=5.5,
            )
        )

    return weather_series


def test_simulate_seven_days():
    initial_state = build_test_state()

    weather_series = build_weather_series(
        days=7
    )

    simulator = TemporalSimulator()

    result = simulator.simulate(
        initial_state=initial_state,
        weather_series=weather_series,
    )

    assert result.days_simulated == 7

    assert len(result.records) == 7

    assert (
        result.final_state.soil_moisture
        <
        initial_state.soil_moisture
    )


def test_irrigation_schedule():
    initial_state = build_test_state()

    weather_series = build_weather_series(
        days=7
    )

    simulator = TemporalSimulator()

    irrigation_schedule = {
        date(2026, 9, 10): 20.0,
    }

    result = simulator.simulate(
        initial_state=initial_state,
        weather_series=weather_series,
        irrigation_schedule=(
            irrigation_schedule
        ),
    )

    assert result.total_irrigation_mm == 20.0

    irrigation_days = [
        record
        for record in result.records
        if record.irrigation_mm > 0
    ]

    assert len(irrigation_days) == 1

    assert irrigation_days[0].day == date(
        2026,
        9,
        10,
    )


def test_irrigation_changes_trajectory():
    initial_state = build_test_state()

    weather_series = build_weather_series(
        days=7
    )

    simulator = TemporalSimulator()

    without_irrigation = simulator.simulate(
        initial_state=initial_state,
        weather_series=weather_series,
    )

    with_irrigation = simulator.simulate(
        initial_state=initial_state,
        weather_series=weather_series,
        irrigation_schedule={
            date(2026, 9, 10): 20.0,
        },
    )

    assert (
        with_irrigation.final_state.soil_moisture
        >
        without_irrigation.final_state.soil_moisture
    )

    assert (
        with_irrigation.final_state.root_zone_depletion_mm
        <
        without_irrigation.final_state.root_zone_depletion_mm
    )


def test_days_since_irrigation():
    initial_state = build_test_state()

    weather_series = build_weather_series(
        days=5
    )

    simulator = TemporalSimulator()

    result = simulator.simulate(
        initial_state=initial_state,
        weather_series=weather_series,
        irrigation_schedule={
            date(2026, 9, 10): 20.0,
        },
    )

    assert (
        result.final_state.days_since_irrigation
        == 2
    )