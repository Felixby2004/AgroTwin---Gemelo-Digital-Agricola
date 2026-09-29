from datetime import date

from engines.scenario import ScenarioEngine
from tests.test_simulation import build_weather_series
from tests.test_water_balance import build_test_state


def test_compare_scenarios():
    state = build_test_state()

    weather_series = build_weather_series(
        days=7
    )

    engine = ScenarioEngine()

    result = engine.compare_irrigation_scenarios(
        initial_state=state,
        weather_series=weather_series,
        irrigation_options_mm=[
            0,
            10,
            20,
            30,
        ],
        irrigation_day=date(
            2026,
            9,
            8,
        ),
    )

    assert result.scenario_count == 4

    assert (
        result.get_by_irrigation(20)
        is not None
    )


def test_more_irrigation_reduces_depletion():
    state = build_test_state()

    weather_series = build_weather_series(
        days=5
    )

    engine = ScenarioEngine()

    result = engine.compare_irrigation_scenarios(
        initial_state=state,
        weather_series=weather_series,
        irrigation_options_mm=[
            0,
            20,
            30,
        ],
    )

    no_irrigation = result.get_by_irrigation(0)

    irrigation_20 = result.get_by_irrigation(20)

    irrigation_30 = result.get_by_irrigation(30)

    assert (
        irrigation_20.final_root_zone_depletion_mm
        <
        no_irrigation.final_root_zone_depletion_mm
    )

    assert (
        irrigation_30.final_root_zone_depletion_mm
        <=
        irrigation_20.final_root_zone_depletion_mm
    )


def test_more_irrigation_increases_soil_moisture():
    state = build_test_state()

    weather_series = build_weather_series(
        days=3
    )

    engine = ScenarioEngine()

    result = engine.compare_irrigation_scenarios(
        initial_state=state,
        weather_series=weather_series,
        irrigation_options_mm=[
            0,
            10,
            20,
            30,
        ],
    )

    scenarios = sorted(
        result.scenarios,
        key=lambda scenario: scenario.irrigation_mm,
    )

    for previous, current in zip(
        scenarios,
        scenarios[1:],
    ):
        assert (
            current.final_soil_moisture
            >=
            previous.final_soil_moisture
        )


def test_scenario_status_exists():
    state = build_test_state()

    weather_series = build_weather_series(
        days=5
    )

    engine = ScenarioEngine()

    result = engine.compare_irrigation_scenarios(
        initial_state=state,
        weather_series=weather_series,
        irrigation_options_mm=[
            0,
            20,
            40,
        ],
    )

    for scenario in result.scenarios:
        assert scenario.technical_status in {
            "SEVERE_STRESS",
            "MODERATE_STRESS",
            "ACCEPTABLE",
            "EXCESS",
        }