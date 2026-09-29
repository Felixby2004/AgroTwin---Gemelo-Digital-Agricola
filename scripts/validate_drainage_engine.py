import sys
from pathlib import Path
from datetime import date, datetime, timedelta

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from twin import Crop, Parcel, Soil, TwinState, WeatherState
from engines.scenario import ScenarioEngine
from engines.recommendation import RecommendationEngine


def build_state(soil_moisture_pct: float) -> TwinState:
    soil = Soil(
        soil_type=None,
        sand_pct=40.0,
        silt_pct=40.0,
        clay_pct=20.0,
        field_capacity=0.30,
        wilting_point=0.12,
        saturation=0.45,
        bulk_density_g_cm3=None,
        root_zone_depth_m=0.60,
    )

    parcel = Parcel(
        parcel_id="TEST-DRAINAGE",
        name="Prueba drenaje",
        latitude=-6.77,
        longitude=-79.84,
        area_ha=2.5,
    )

    crop = Crop(
        crop_name="Maíz",
        planting_date=date(2026, 7, 1),
        growth_stage="mid-season",
        kc=1.15,
        root_depth_m=0.60,
        depletion_fraction_p=0.50,
    )

    weather = WeatherState(
        timestamp=datetime.now(),
        temperature_c=25.0,
        relative_humidity_pct=70.0,
        rainfall_mm=0.0,
        et0_mm_day=2.0,
    )

    return TwinState(
        timestamp=datetime.now(),
        parcel=parcel,
        soil=soil,
        crop=crop,
        weather=weather,
        soil_moisture=soil_moisture_pct / 100.0,
    )


def main():
    start = date.today()

    weather_series = [
        WeatherState(
            timestamp=datetime.combine(start, datetime.min.time()),
            temperature_c=25.0,
            relative_humidity_pct=70.0,
            rainfall_mm=0.0,
            et0_mm_day=2.0,
        )
    ]

    state = build_state(40.0)

    irrigation_options = list(range(0, 151, 10))

    comparison = ScenarioEngine().compare_irrigation_scenarios(
        initial_state=state,
        weather_series=weather_series,
        irrigation_options_mm=irrigation_options,
        irrigation_day=start,
    )

    recommendation = RecommendationEngine(
        acceptable_stress_threshold=0.30,
        max_deep_percolation_mm=1.0,
    ).recommend(comparison)

    rows = comparison.to_dicts()

    print("PRUEBA ESPECÍFICA DE DRENAJE PROFUNDO")
    print("Humedad inicial: 40% | Saturación: 45% | Horizonte: 1 día")
    print("ET0: 2.0 mm/d | Kc: 1.15 | Sin lluvia")
    print("Escenarios: 0..150 mm cada 10 mm")
    print()

    print(f"{'Riego':>7} | {'Hum.Final':>10} | {'Estrés':>8} | {'Drenaje':>10} | {'Estado':>18}")
    print("-" * 82)

    drainage_detected = False

    for row in rows:
        irrigation = float(row.get("irrigation_mm", 0))
        moisture = float(row.get("final_soil_moisture_pct", 0))
        stress = float(row.get("water_stress_index", 0))
        drainage = float(row.get("deep_percolation_mm", 0))
        status = str(row.get("technical_status", ""))

        if drainage > 0:
            drainage_detected = True

        print(
            f"{irrigation:7.1f} | "
            f"{moisture:10.2f} | "
            f"{stress:8.3f} | "
            f"{drainage:10.3f} | "
            f"{status:>18}"
        )

    print()
    print("RESULTADO DE LA PRUEBA")
    if drainage_detected:
        print("OK: el motor detectó drenaje profundo en al menos un escenario.")
    else:
        print(
            "REVISAR: no apareció drenaje profundo incluso con el suelo "
            "cerca de saturación y riegos de hasta 150 mm."
        )

    print()
    print("RECOMENDACIÓN DEL MOTOR")
    print("Riego recomendado:", recommendation.recommended_irrigation_mm, "mm")
    print("Estrés final:", recommendation.final_water_stress_index)
    print("Drenaje:", recommendation.deep_percolation_mm, "mm")
    print("Tipo:", recommendation.decision_type)
    print("Razones:", recommendation.reason_codes)


if __name__ == "__main__":
    main()
