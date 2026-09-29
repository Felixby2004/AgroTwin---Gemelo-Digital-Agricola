import sys
from pathlib import Path
from datetime import date, datetime, timedelta

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from twin import Crop, Parcel, Soil, TwinState, WeatherState
from engines.scenario import ScenarioEngine
from engines.recommendation import RecommendationEngine


def build_state(soil_moisture_pct: float, rainfall_mm: float) -> TwinState:
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
        parcel_id="TEST-RAIN",
        name="Prueba lluvia",
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
        temperature_c=28.0,
        relative_humidity_pct=65.0,
        rainfall_mm=rainfall_mm,
        et0_mm_day=5.0,
    )

    return TwinState(
        timestamp=datetime.now(),
        parcel=parcel,
        soil=soil,
        crop=crop,
        weather=weather,
        soil_moisture=soil_moisture_pct / 100.0,
    )


def run_case(name: str, rainfall_mm: float):
    print("\n" + "=" * 78)
    print(f"{name} | Lluvia diaria: {rainfall_mm:.1f} mm")
    print("=" * 78)

    start = date.today()

    weather_series = [
        WeatherState(
            timestamp=datetime.combine(
                start + timedelta(days=i),
                datetime.min.time(),
            ),
            temperature_c=28.0,
            relative_humidity_pct=65.0,
            rainfall_mm=rainfall_mm,
            et0_mm_day=5.0,
        )
        for i in range(5)
    ]

    state = build_state(
        soil_moisture_pct=22.0,
        rainfall_mm=rainfall_mm,
    )

    irrigation_options = list(range(0, 61, 10))

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

    print(
        f"{'Riego':>7} | "
        f"{'Hum.Final':>10} | "
        f"{'Estrés':>8} | "
        f"{'Lluvia':>8} | "
        f"{'Drenaje':>8} | "
        f"{'Estado':>18}"
    )
    print("-" * 90)

    for row in rows:
        print(
            f"{float(row.get('irrigation_mm', 0)):7.1f} | "
            f"{float(row.get('final_soil_moisture_pct', 0)):10.2f} | "
            f"{float(row.get('water_stress_index', 0)):8.3f} | "
            f"{float(row.get('total_rainfall_mm', 0)):8.1f} | "
            f"{float(row.get('deep_percolation_mm', 0)):8.3f} | "
            f"{str(row.get('technical_status', '')):>18}"
        )

    print("\nRECOMENDACIÓN")
    print("Riego recomendado:", recommendation.recommended_irrigation_mm, "mm")
    print("Humedad final:", recommendation.final_soil_moisture_pct, "%")
    print("Estrés final:", recommendation.final_water_stress_index)
    print("Drenaje:", recommendation.deep_percolation_mm, "mm")
    print("Tipo:", recommendation.decision_type)
    print("Razones:", recommendation.reason_codes)

    return {
        "name": name,
        "rainfall": rainfall_mm,
        "irrigation": recommendation.recommended_irrigation_mm,
        "stress": recommendation.final_water_stress_index,
        "drainage": recommendation.deep_percolation_mm,
    }


def main():
    print("VALIDACIÓN CONTROLADA DE RESPUESTA A LLUVIA")
    print("Humedad inicial = 22%")
    print("ET0 = 5.0 mm/d | Kc = 1.15")
    print("Horizonte = 5 días")
    print("Escenarios de riego = 0..60 mm cada 10 mm")
    print()

    results = [
        run_case("CASO 1 - SIN LLUVIA", 0.0),
        run_case("CASO 2 - LLUVIA MODERADA", 3.0),
        run_case("CASO 3 - LLUVIA ALTA", 8.0),
    ]

    print("\n" + "=" * 78)
    print("RESUMEN")
    print("=" * 78)

    for result in results:
        print(
            f"{result['name']}: "
            f"lluvia={result['rainfall']:.1f} mm/d | "
            f"riego recomendado={result['irrigation']} mm | "
            f"estrés={result['stress']:.3f} | "
            f"drenaje={result['drainage']:.3f}"
        )

    print("\nCRITERIOS ESPERADOS")
    print("1. Con más lluvia, la necesidad de riego no debería aumentar.")
    print("2. La humedad final debería aumentar o mantenerse con más lluvia.")
    print("3. El estrés debería reducirse o mantenerse con más lluvia.")
    print("4. Con lluvia suficiente, el riego recomendado debería disminuir.")
    print("5. Si el exceso de agua supera la capacidad de almacenamiento, debería aparecer drenaje.")


if __name__ == "__main__":
    main()
