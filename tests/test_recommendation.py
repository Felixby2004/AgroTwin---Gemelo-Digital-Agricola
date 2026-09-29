from engines.recommendation import (
    RecommendationEngine,
)
from engines.scenario import ScenarioEngine
from tests.test_simulation import build_weather_series
from tests.test_water_balance import build_test_state


def test_recommendation_is_generated():
    state = build_test_state()

    weather_series = build_weather_series(
        days=5
    )

    scenario_engine = ScenarioEngine()

    comparison = (
        scenario_engine.compare_irrigation_scenarios(
            initial_state=state,
            weather_series=weather_series,
            irrigation_options_mm=[
                0,
                10,
                20,
                30,
                40,
                50,
                60,
                70,
                80,
            ],
        )
    )

    recommendation_engine = (
        RecommendationEngine()
    )

    recommendation = (
        recommendation_engine.recommend(
            comparison
        )
    )

    assert recommendation is not None

    assert (
        recommendation.recommended_irrigation_mm
        >= 0
    )

    assert recommendation.selected_scenario_id

    assert recommendation.reason_codes


def test_recommendation_belongs_to_scenarios():
    state = build_test_state()

    weather_series = build_weather_series(
        days=5
    )

    comparison = (
        ScenarioEngine()
        .compare_irrigation_scenarios(
            initial_state=state,
            weather_series=weather_series,
            irrigation_options_mm=[
                0,
                20,
                40,
                60,
                80,
            ],
        )
    )

    recommendation = (
        RecommendationEngine()
        .recommend(comparison)
    )

    valid_ids = {
        scenario.scenario_id
        for scenario in comparison.scenarios
    }

    assert (
        recommendation.selected_scenario_id
        in valid_ids
    )


def test_selects_minimum_acceptable_irrigation():
    state = build_test_state()

    weather_series = build_weather_series(
        days=3
    )

    comparison = (
        ScenarioEngine()
        .compare_irrigation_scenarios(
            initial_state=state,
            weather_series=weather_series,
            irrigation_options_mm=[
                0,
                10,
                20,
                30,
                40,
                50,
                60,
                70,
                80,
                90,
            ],
        )
    )

    engine = RecommendationEngine()

    recommendation = engine.recommend(
        comparison
    )

    acceptable = [
        scenario
        for scenario in comparison.scenarios
        if (
            scenario.final_water_stress_index
            <= engine.acceptable_stress_threshold
            and
            scenario.deep_percolation_mm
            <= engine.max_deep_percolation_mm
        )
    ]

    if acceptable:

        expected = min(
            acceptable,
            key=lambda scenario: (
                scenario.irrigation_mm,
                scenario.deep_percolation_mm,
                scenario.final_water_stress_index,
            ),
        )

        assert (
            recommendation.recommended_irrigation_mm
            ==
            expected.irrigation_mm
        )


def test_no_irrigation_when_not_required():
    state = build_test_state()

    state = state.model_copy(
        update={
            "soil_moisture": 0.32
        }
    )

    weather_series = build_weather_series(
        days=1
    )

    comparison = (
        ScenarioEngine()
        .compare_irrigation_scenarios(
            initial_state=state,
            weather_series=weather_series,
            irrigation_options_mm=[
                0,
                10,
                20,
                30,
            ],
        )
    )

    recommendation = (
        RecommendationEngine()
        .recommend(comparison)
    )

    assert (
        recommendation.recommended_irrigation_mm
        ==
        0
    )

    assert (
        recommendation.decision_type
        ==
        "NO_IRRIGATION_REQUIRED"
    )


def test_best_available_when_no_scenario_is_acceptable():
    state = build_test_state()

    weather_series = build_weather_series(
        days=7
    )

    comparison = (
        ScenarioEngine()
        .compare_irrigation_scenarios(
            initial_state=state,
            weather_series=weather_series,
            irrigation_options_mm=[
                0,
                5,
                10,
            ],
        )
    )

    recommendation = (
        RecommendationEngine()
        .recommend(comparison)
    )

    assert (
        recommendation.decision_type
        ==
        "BEST_AVAILABLE"
    )

    assert (
        "NO_FULLY_ACCEPTABLE_SCENARIO"
        in recommendation.reason_codes
    )