from datetime import date, datetime

from engines.water_balance import WaterBalanceEngine
from twin import Crop, Parcel, Soil, TwinState, WeatherState


def build_test_state():
    parcel = Parcel(
        parcel_id="P001",
        name="Parcela Piloto",
        latitude=-6.77,
        longitude=-79.84,
        area_ha=2.5,
    )

    soil = Soil(
        soil_type="loam",
        sand_pct=40,
        silt_pct=40,
        clay_pct=20,
        field_capacity=0.32,
        wilting_point=0.15,
        saturation=0.45,
        root_zone_depth_m=0.60,
    )

    crop = Crop(
        crop_name="maize",
        planting_date=date(2026, 7, 1),
        growth_stage="mid-season",
        kc=1.15,
        root_depth_m=0.60,
        depletion_fraction_p=0.50,
    )

    weather = WeatherState(
        timestamp=datetime(2026, 9, 7, 8, 0),
        temperature_c=30.5,
        relative_humidity_pct=58,
        rainfall_mm=0,
        et0_mm_day=5.5,
    )

    return TwinState(
        timestamp=datetime(2026, 9, 7, 8, 0),
        parcel=parcel,
        soil=soil,
        crop=crop,
        weather=weather,
        soil_moisture=0.22,
    )


def test_calculate_etc():
    state = build_test_state()

    engine = WaterBalanceEngine()

    etc = engine.calculate_etc(state)

    assert round(etc, 3) == 6.325


def test_taw():
    state = build_test_state()

    engine = WaterBalanceEngine()

    taw = engine.calculate_taw(state)

    assert round(taw, 2) == 102.0


def test_raw():
    state = build_test_state()

    engine = WaterBalanceEngine()

    raw = engine.calculate_raw(state)

    assert round(raw, 2) == 51.0


def test_water_balance_without_irrigation():
    state = build_test_state()

    engine = WaterBalanceEngine()

    result = engine.step(
        state,
        irrigation_mm=0,
    )

    assert result.final_soil_moisture < state.soil_moisture
    assert result.etc_mm > 0
    assert result.root_zone_depletion_mm > 0


def test_irrigation_increases_final_moisture():
    state = build_test_state()

    engine = WaterBalanceEngine()

    no_irrigation = engine.step(
        state,
        irrigation_mm=0,
    )

    with_irrigation = engine.step(
        state,
        irrigation_mm=20,
    )

    assert (
        with_irrigation.final_soil_moisture
        >
        no_irrigation.final_soil_moisture
    )


def test_update_twin_state():
    state = build_test_state()

    engine = WaterBalanceEngine()

    result = engine.step(
        state,
        irrigation_mm=20,
    )

    new_state = engine.update_state(
        state,
        result,
    )

    assert (
        new_state.previous_soil_moisture
        ==
        state.soil_moisture
    )

    assert (
        new_state.soil_moisture
        ==
        result.final_soil_moisture
    )

    assert new_state.etc_mm_day is not None