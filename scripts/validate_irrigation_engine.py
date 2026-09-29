import sys
from pathlib import Path
from datetime import date, datetime, timedelta

ROOT_DIR = Path(__file__).resolve().parent.parent

if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from twin import Crop, Parcel, Soil, TwinState, WeatherState
from engines.scenario import ScenarioEngine
from engines.recommendation import RecommendationEngine


def build_weather_series(start_date, days, temperature_c, humidity_pct, rainfall_mm, et0_mm_day):
    return [
        WeatherState(
            timestamp=datetime.combine(start_date + timedelta(days=i), datetime.min.time()),
            temperature_c=temperature_c,
            relative_humidity_pct=humidity_pct,
            rainfall_mm=rainfall_mm,
            et0_mm_day=et0_mm_day,
        )
        for i in range(days)
    ]


def build_state(soil_moisture_pct):
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
        parcel_id="TEST-P001",
        name="Parcela prueba",
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
        temperature_c=30.0,
        relative_humidity_pct=60.0,
        rainfall_mm=0.0,
        et0_mm_day=5.5,
    )

    return TwinState(
        timestamp=datetime.now(),
        parcel=parcel,
        soil=soil,
        crop=crop,
        weather=weather,
        soil_moisture=soil_moisture_pct / 100.0,
    )


def run_case(name, soil_moisture_pct):
    print("\n" + "=" * 78)
    print(f"{name} | Humedad inicial: {soil_moisture_pct:.1f}%")
    print("=" * 78)

    start_date = date.today()

    weather_series = build_weather_series(
        start_date=start_date,
        days=5,
        temperature_c=30.0,
        humidity_pct=60.0,
        rainfall_mm=0.0,
        et0_mm_day=5.5,
    )

    irrigation_options = list(range(0, 81, 10))

    state = build_state(soil_moisture_pct)

    comparison = ScenarioEngine().compare_irrigation_scenarios(
        initial_state=state,
        weather_series=weather_series,
        irrigation_options_mm=irrigation_options,
        irrigation_day=start_date,
    )

    recommendation = RecommendationEngine(
        acceptable_stress_threshold=0.30,
        max_deep_percolation_mm=1.0,
    ).recommend(comparison)

    rows = comparison.to_dicts()

    print(f"{'Riego':>7} | {'Hum.Final':>10} | {'Estrés':>8} | {'Drenaje':>8} | {'Estado':>18}")
    print("-" * 78)

    for row in rows:
        print(
            f"{float(row.get('irrigation_mm', 0)):7.1f} | "
            f"{float(row.get('final_soil_moisture_pct', 0)):10.2f} | "
            f"{float(row.get('water_stress_index', 0)):8.3f} | "
            f"{float(row.get('deep_percolation_mm', 0)):8.3f} | "
            f"{str(row.get('technical_status', '')):>18}"
        )

    print("\nRECOMENDACIÓN")
    print("Riego recomendado:", recommendation.recommended_irrigation_mm, "mm")
    print("Humedad final:", recommendation.final_soil_moisture_pct, "%")
    print("Estrés final:", recommendation.final_water_stress_index)
    print("Drenaje:", recommendation.deep_percolation_mm, "mm")
    print("Tipo de decisión:", recommendation.decision_type)
    print("Razones:", recommendation.reason_codes)

    return {
        "name": name,
        "recommended_irrigation": recommendation.recommended_irrigation_mm,
        "stress": recommendation.final_water_stress_index,
        "deep_percolation": recommendation.deep_percolation_mm,
    }


def main():
    print("VALIDACIÓN CONTROLADA DEL MOTOR DE RIEGO")
    print("ET0 = 5.5 mm/d | Kc = 1.15 | ETc = 6.325 mm/d")
    print("Horizonte = 5 días | Lluvia = 0 mm")
    print("Escenarios = 0..80 mm cada 10 mm")
    print("Umbral estrés = 0.30 | Máx. drenaje = 1.0 mm")

    results = [
        run_case("CASO A - SECO", 13.0),
        run_case("CASO B - INTERMEDIO", 22.0),
        run_case("CASO C - CERCA DE CAPACIDAD DE CAMPO", 29.0),
    ]

    print("\n" + "=" * 78)
    print("RESUMEN COMPARATIVO")
    print("=" * 78)

    for result in results:
        print(
            f"{result['name']}: "
            f"{result['recommended_irrigation']} mm | "
            f"estrés={result['stress']:.3f} | "
            f"drenaje={result['deep_percolation']:.3f}"
        )

    print("\nCRITERIOS DE COHERENCIA ESPERADOS")
    print("1. El caso seco debería requerir igual o más riego que el caso intermedio.")
    print("2. El caso cercano a capacidad de campo debería requerir igual o menos riego que el caso intermedio.")
    print("3. Al aumentar el riego, el estrés no debería crecer sin una causa física clara.")
    print("4. Con riegos altos, el drenaje debería aparecer o aumentar.")
    print("5. La recomendación debe respetar estrés <= 0.30 y drenaje <= 1.0 mm cuando exista un escenario factible.")


if __name__ == "__main__":
    main()
