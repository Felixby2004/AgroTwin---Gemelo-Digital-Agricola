from datetime import date, datetime

from pydantic_core import ValidationError
import pytest

from twin import Crop, Parcel, Soil, TwinState, WeatherState


def test_create_twin_state():
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
        variety="pilot",
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
        solar_radiation_mj_m2_day=21.0,
        wind_speed_m_s=2.1,
        et0_mm_day=5.5,
    )

    state = TwinState(
        timestamp=datetime(2026, 9, 7, 8, 0),
        parcel=parcel,
        soil=soil,
        crop=crop,
        weather=weather,
        soil_moisture=0.22,
        last_irrigation_mm=0,
        days_since_irrigation=4,
        ndvi=0.72,
    )

    assert state.parcel.parcel_id == "P001"

    assert state.soil_moisture_pct == 22.0

    assert 0 <= state.available_water_fraction <= 1

def test_invalid_soil_properties():
    with pytest.raises(ValidationError):
        Soil(
            soil_type="invalid",
            field_capacity=0.15,
            wilting_point=0.25,
        )