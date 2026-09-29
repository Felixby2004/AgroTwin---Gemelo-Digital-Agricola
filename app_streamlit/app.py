import sys
from pathlib import Path
from datetime import date, datetime, timedelta

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# ---------------------------------------------------------
# Proyecto
# ---------------------------------------------------------

ROOT_DIR = Path(__file__).resolve().parent.parent

if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from config.settings import settings
from twin import Crop, Parcel, Soil, TwinState, WeatherState
from integrations.nasa_power import (
    NASAPowerClient,
    NASAPowerError,
)
from integrations.soilgrids_wcs import (
    SoilGridsWCSClient,
    SoilGridsWCSError,
)
from engines.soil_hydraulics import (
    SoilHydraulicEstimator,
    SoilHydraulicError,
)
from engines.recommendation import RecommendationEngine
from engines.scenario import ScenarioEngine


# ---------------------------------------------------------
# Configuración Streamlit
# ---------------------------------------------------------

st.set_page_config(
    page_title="AgroTwin · Laboratorio del Motor IA",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ---------------------------------------------------------
# Estilos
# ---------------------------------------------------------

st.markdown(
    """
    <style>
    .block-container {
        max-width: 1500px;
        padding-top: 1.2rem;
        padding-bottom: 2rem;
    }

    .agro-hero {
        padding: 1.15rem 1.25rem;
        border: 1px solid rgba(120, 120, 120, 0.20);
        border-radius: 16px;
        margin-bottom: 1rem;
    }

    .agro-hero h1 {
        margin: 0 0 .35rem 0;
        font-size: 2rem;
    }

    .agro-hero p {
        margin: 0;
        opacity: .78;
    }

    .status-grid {
        display: grid;
        grid-template-columns: repeat(4, minmax(0, 1fr));
        gap: .7rem;
        margin: .6rem 0 1rem 0;
    }

    .status-card {
        padding: .9rem;
        border: 1px solid rgba(120, 120, 120, 0.20);
        border-radius: 12px;
    }

    .status-card strong {
        display: block;
        margin-bottom: .2rem;
    }

    .status-card span {
        font-size: .85rem;
        opacity: .72;
    }

    .pipeline {
        display: flex;
        flex-wrap: wrap;
        gap: .45rem;
        align-items: center;
        margin: .4rem 0 1rem 0;
    }

    .pipeline-step {
        padding: .5rem .75rem;
        border-radius: 999px;
        border: 1px solid rgba(120, 120, 120, 0.24);
        font-size: .85rem;
    }

    .pipeline-arrow {
        opacity: .55;
    }

    .mini-note {
        padding: .75rem .9rem;
        border-left: 4px solid #2f855a;
        background: rgba(47, 133, 90, 0.08);
        border-radius: 8px;
        margin: .5rem 0 .9rem 0;
    }

    .warning-note {
        padding: .75rem .9rem;
        border-left: 4px solid #d97706;
        background: rgba(217, 119, 6, 0.08);
        border-radius: 8px;
        margin: .5rem 0 .9rem 0;
    }

    @media (max-width: 900px) {
        .status-grid {
            grid-template-columns: 1fr 1fr;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ---------------------------------------------------------
# Funciones auxiliares
# ---------------------------------------------------------

def build_weather_series(
    start_date: date,
    days: int,
    temperature_c: float,
    humidity_pct: float,
    rainfall_mm: float,
    et0_mm_day: float,
) -> list[WeatherState]:

    weather_series = []

    for i in range(days):
        current_date = start_date + timedelta(days=i)

        weather_series.append(
            WeatherState(
                timestamp=datetime.combine(
                    current_date,
                    datetime.min.time(),
                ),
                temperature_c=temperature_c,
                relative_humidity_pct=humidity_pct,
                rainfall_mm=rainfall_mm,
                et0_mm_day=et0_mm_day,
            )
        )

    return weather_series


def build_twin_state(
    soil: Soil,
    soil_moisture_pct: float,
    crop_name: str,
    kc: float,
    root_depth_m: float,
    depletion_fraction_p: float,
    temperature_c: float,
    humidity_pct: float,
    rainfall_mm: float,
    et0_mm_day: float,
) -> TwinState:

    parcel = Parcel(
        parcel_id="P001",
        name="Parcela Piloto",
        latitude=-6.77,
        longitude=-79.84,
        area_ha=2.5,
    )

    crop = Crop(
        crop_name=crop_name,
        planting_date=date(2026, 7, 1),
        growth_stage="mid-season",
        kc=kc,
        root_depth_m=root_depth_m,
        depletion_fraction_p=depletion_fraction_p,
    )

    weather = WeatherState(
        timestamp=datetime.now(),
        temperature_c=temperature_c,
        relative_humidity_pct=humidity_pct,
        rainfall_mm=rainfall_mm,
        et0_mm_day=et0_mm_day,
    )

    return TwinState(
        timestamp=datetime.now(),
        parcel=parcel,
        soil=soil,
        crop=crop,
        weather=weather,
        soil_moisture=(
            soil_moisture_pct / 100.0
        ),
    )


def translate_reason_code(code: str) -> str:
    translations = {
        "CURRENT_STATE_ACCEPTABLE":
            "El estado hídrico se mantiene dentro del rango aceptable.",
        "IRRIGATION_NOT_REQUIRED":
            "No se requiere riego bajo las condiciones simuladas.",
        "WATER_SAVING":
            "Se prioriza evitar una aplicación innecesaria de agua.",
        "WATER_STRESS_CONTROLLED":
            "El escenario mantiene el estrés hídrico dentro del límite aceptable.",
        "DEEP_PERCOLATION_ACCEPTABLE":
            "La pérdida estimada por drenaje profundo es aceptable.",
        "MINIMUM_ACCEPTABLE_IRRIGATION":
            "Es la menor cantidad de riego que satisface los criterios técnicos.",
        "NO_FULLY_ACCEPTABLE_SCENARIO":
            "Ningún escenario evaluado cumple completamente todos los criterios.",
        "BEST_AVAILABLE_SCENARIO":
            "Se seleccionó la mejor alternativa entre los escenarios disponibles.",
        "RESIDUAL_WATER_STRESS":
            "Persistirá cierto nivel de estrés hídrico después del riego.",
        "DEEP_PERCOLATION_RISK":
            "Existe riesgo de pérdida de agua por drenaje profundo.",
    }

    return translations.get(
        code,
        code,
    )


def stress_label(value: float) -> str:
    if value < 0.30:
        return "Bajo"

    if value < 0.70:
        return "Moderado"

    return "Alto"


def build_provenance_table(
    soil_source: str,
    weather_source: str,
) -> pd.DataFrame:

    return pd.DataFrame(
        [
            {
                "Variable / bloque": "Humedad actual",
                "Fuente": "Usuario / sensor manual",
                "Tipo de evidencia": "MEASURED / USER_INPUT",
                "Uso": "Estado inicial del TwinState",
            },
            {
                "Variable / bloque": "Textura y propiedades del suelo",
                "Fuente": (
                    "SoilGrids"
                    if soil_source == "SoilGrids"
                    else "Entrada manual"
                ),
                "Tipo de evidencia": (
                    "EXTERNAL"
                    if soil_source == "SoilGrids"
                    else "USER_INPUT"
                ),
                "Uso": "Capacidad de campo, marchitez y balance hídrico",
            },
            {
                "Variable / bloque": "Meteorología",
                "Fuente": weather_source,
                "Tipo de evidencia": (
                    "EXTERNAL"
                    if weather_source == "NASA POWER"
                    else "SYNTHETIC"
                ),
                "Uso": "ET0, lluvia, temperatura y simulación",
            },
            {
                "Variable / bloque": "Escenarios de riego",
                "Fuente": "ScenarioEngine",
                "Tipo de evidencia": "MODEL_DERIVED",
                "Uso": "Comparación de alternativas",
            },
            {
                "Variable / bloque": "Recomendación",
                "Fuente": "RecommendationEngine",
                "Tipo de evidencia": "MODEL_DERIVED",
                "Uso": "Selección y explicación de la alternativa",
            },
        ]
    )


def build_engine_inventory() -> pd.DataFrame:

    return pd.DataFrame(
        [
            {
                "Componente": "TwinState",
                "Estado": "Operativo",
                "Función": "Representa el estado hídrico actual de la parcela.",
                "Dónde se ejecuta": "Motor principal / API",
            },
            {
                "Componente": "NASA POWER + FAO-56 ET0",
                "Estado": "Operativo",
                "Función": "Meteorología externa y evapotranspiración de referencia.",
                "Dónde se ejecuta": "Integraciones científicas",
            },
            {
                "Componente": "SoilGrids + hidráulica",
                "Estado": "Operativo",
                "Función": "Perfil edáfico y parámetros hidráulicos derivados.",
                "Dónde se ejecuta": "Integraciones científicas",
            },
            {
                "Componente": "Scenario Engine",
                "Estado": "Operativo",
                "Función": "Simula alternativas de riego y su respuesta hídrica.",
                "Dónde se ejecuta": "Este laboratorio",
            },
            {
                "Componente": "Recommendation Engine",
                "Estado": "Operativo",
                "Función": "Aplica criterios deterministas y genera razones.",
                "Dónde se ejecuta": "Este laboratorio",
            },
            {
                "Componente": "AquaCrop",
                "Estado": "Operativo en el motor principal",
                "Función": "Simulación agronómica avanzada de escenarios validados.",
                "Dónde se ejecuta": "Pipeline científico principal",
            },
            {
                "Componente": "ML Random Forest",
                "Estado": "Complementario",
                "Función": "Predice humedad del suelo con incertidumbre y explicación.",
                "Dónde se ejecuta": "API / frontend principal",
            },
            {
                "Componente": "Conocimiento del agricultor",
                "Estado": "Operativo",
                "Función": "Observaciones, eventos, restricciones, preferencias y conocimiento local.",
                "Dónde se ejecuta": "Motor participativo principal",
            },
            {
                "Componente": "HITL",
                "Estado": "Operativo",
                "Función": "Aceptar, modificar o rechazar recomendaciones.",
                "Dónde se ejecuta": "API / frontend principal",
            },
            {
                "Componente": "Provenance + DecisionTrace",
                "Estado": "Operativo",
                "Función": "Trazabilidad del origen, evidencia y decisión.",
                "Dónde se ejecuta": "Motor principal",
            },
        ]
    )


def scenario_explanation(
    recommendation,
) -> list[dict]:

    return [
        {
            "Paso": "1",
            "Pregunta": "¿Qué alternativas se evaluaron?",
            "Respuesta": (
                "Se simularon múltiples cantidades de riego "
                "sobre el mismo estado inicial y clima."
            ),
        },
        {
            "Paso": "2",
            "Pregunta": "¿Qué se compara?",
            "Respuesta": (
                "Humedad final, agotamiento de la zona radicular, "
                "estrés hídrico, ETc y drenaje profundo."
            ),
        },
        {
            "Paso": "3",
            "Pregunta": "¿Cómo se filtra?",
            "Respuesta": (
                "Se aplican umbrales técnicos de estrés máximo "
                "y drenaje profundo aceptable."
            ),
        },
        {
            "Paso": "4",
            "Pregunta": "¿Qué se recomienda?",
            "Respuesta": (
                f"{recommendation.recommended_irrigation_mm:.1f} mm "
                "según los criterios configurados en este laboratorio."
            ),
        },
        {
            "Paso": "5",
            "Pregunta": "¿Por qué?",
            "Respuesta": (
                "La recomendación conserva reason_codes que se muestran "
                "como una explicación legible para el usuario."
            ),
        },
    ]


# ---------------------------------------------------------
# Encabezado
# ---------------------------------------------------------

st.markdown(
    """
    <div class="agro-hero">
        <h1>🌱 AgroTwin · Laboratorio del Motor IA</h1>
        <p>
            Entorno explicable para observar entradas, evidencias,
            simulación, comparación de escenarios y lógica de recomendación.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="status-grid">
        <div class="status-card">
            <strong>Motor científico</strong>
            <span>Balance hídrico + escenarios + reglas de decisión</span>
        </div>
        <div class="status-card">
            <strong>Participativo</strong>
            <span>Conocimiento del agricultor sin sobrescribir evidencia de máquina</span>
        </div>
        <div class="status-card">
            <strong>Explicable</strong>
            <span>Razones, procedencia y trazabilidad de decisiones</span>
        </div>
        <div class="status-card">
            <strong>ML complementario</strong>
            <span>Predice; el motor de decisión decide</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="pipeline">
        <span class="pipeline-step">Entradas</span>
        <span class="pipeline-arrow">→</span>
        <span class="pipeline-step">Evidencia</span>
        <span class="pipeline-arrow">→</span>
        <span class="pipeline-step">TwinState</span>
        <span class="pipeline-arrow">→</span>
        <span class="pipeline-step">Escenarios</span>
        <span class="pipeline-arrow">→</span>
        <span class="pipeline-step">Criterios</span>
        <span class="pipeline-arrow">→</span>
        <span class="pipeline-step">Recomendación</span>
        <span class="pipeline-arrow">→</span>
        <span class="pipeline-step">HITL / trazabilidad</span>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="mini-note">
        <strong>Regla de diseño:</strong>
        el conocimiento del agricultor se utiliza como contexto,
        restricción, preferencia, evento u observación; no reemplaza
        silenciosamente la evidencia de máquina ni el TwinState.
    </div>
    """,
    unsafe_allow_html=True,
)


# ---------------------------------------------------------
# Sidebar
# ---------------------------------------------------------

st.sidebar.title("Configuración")
st.sidebar.caption("Parámetros del laboratorio local")

st.sidebar.subheader("Cultivo")

crop_name = st.sidebar.selectbox(
    "Cultivo",
    [
        "Maíz",
        "Tomate",
        "Papa",
        "Arroz",
        "Otro",
    ],
)

kc = st.sidebar.number_input(
    "Coeficiente Kc",
    min_value=0.10,
    max_value=2.00,
    value=1.15,
    step=0.05,
)

root_depth_m = st.sidebar.number_input(
    "Profundidad radicular (m)",
    min_value=0.10,
    max_value=3.00,
    value=0.60,
    step=0.05,
)

depletion_fraction_p = st.sidebar.slider(
    "Fracción de agotamiento tolerable (p)",
    min_value=0.10,
    max_value=0.90,
    value=0.50,
    step=0.05,
)

st.sidebar.divider()
st.sidebar.subheader("Suelo")

soil_source = st.sidebar.radio(
    "Fuente de datos del suelo",
    options=[
        "Manual",
        "SoilGrids",
    ],
    horizontal=True,
)

if soil_source == "Manual":

    soil_moisture_pct = st.sidebar.number_input(
        "Humedad actual del suelo (%)",
        min_value=0.0,
        max_value=100.0,
        value=22.0,
        step=1.0,
    )

    field_capacity = st.sidebar.number_input(
        "Capacidad de campo (fracción)",
        min_value=0.01,
        max_value=0.80,
        value=0.30,
        step=0.01,
    )

    wilting_point = st.sidebar.number_input(
        "Punto de marchitez (fracción)",
        min_value=0.0,
        max_value=0.70,
        value=0.12,
        step=0.01,
    )

    saturation = st.sidebar.number_input(
        "Saturación (fracción)",
        min_value=0.01,
        max_value=1.0,
        value=0.45,
        step=0.01,
    )

    sand_pct = st.sidebar.number_input(
        "Arena (%)",
        min_value=0.0,
        max_value=100.0,
        value=40.0,
        step=1.0,
    )

    silt_pct = st.sidebar.number_input(
        "Limo (%)",
        min_value=0.0,
        max_value=100.0,
        value=40.0,
        step=1.0,
    )

    clay_pct = st.sidebar.number_input(
        "Arcilla (%)",
        min_value=0.0,
        max_value=100.0,
        value=20.0,
        step=1.0,
    )

else:

    soilgrids_latitude = st.sidebar.number_input(
        "Latitud SoilGrids",
        value=-6.77,
        format="%.6f",
    )

    soilgrids_longitude = st.sidebar.number_input(
        "Longitud SoilGrids",
        value=-79.84,
        format="%.6f",
    )

    soil_moisture_pct = st.sidebar.number_input(
        "Humedad actual del suelo (%)",
        min_value=0.0,
        max_value=100.0,
        value=22.0,
        step=1.0,
    )

    if st.sidebar.button(
        "Consultar SoilGrids",
        use_container_width=True,
    ):

        try:

            client = SoilGridsWCSClient(
                timeout_seconds=90,
            )

            profile = client.get_soil_profile(
                latitude=soilgrids_latitude,
                longitude=soilgrids_longitude,
            )

            estimator = SoilHydraulicEstimator()

            soil_from_soilgrids = (
                estimator.build_soil(
                    profile=profile,
                    root_zone_depth_m=root_depth_m,
                )
            )

            st.session_state[
                "soilgrids_profile"
            ] = profile

            st.session_state[
                "soilgrids_soil"
            ] = soil_from_soilgrids

            st.sidebar.success(
                "SoilGrids cargado."
            )

        except (
            SoilGridsWCSError,
            SoilHydraulicError,
            ValueError,
        ) as exc:

            st.sidebar.error(
                f"Error SoilGrids: {exc}"
            )

st.sidebar.divider()
st.sidebar.subheader("Clima del laboratorio")

weather_mode = st.sidebar.radio(
    "Fuente climática usada en la simulación",
    [
        "Simulado",
        "NASA POWER descargado",
    ],
)

temperature_c = st.sidebar.number_input(
    "Temperatura (°C)",
    value=30.0,
    step=0.5,
)

humidity_pct = st.sidebar.slider(
    "Humedad relativa (%)",
    min_value=0.0,
    max_value=100.0,
    value=60.0,
    step=1.0,
)

rainfall_mm = st.sidebar.number_input(
    "Precipitación diaria (mm)",
    min_value=0.0,
    value=0.0,
    step=1.0,
)

et0_mm_day = st.sidebar.number_input(
    "ET0 diaria (mm/día)",
    min_value=0.0,
    value=5.5,
    step=0.1,
)

st.sidebar.divider()
st.sidebar.subheader("Simulación")

simulation_days = st.sidebar.slider(
    "Horizonte de simulación (días)",
    min_value=1,
    max_value=15,
    value=5,
)

irrigation_step = st.sidebar.selectbox(
    "Incremento de escenarios (mm)",
    [
        5,
        10,
    ],
)

max_irrigation = st.sidebar.slider(
    "Máximo riego a evaluar (mm)",
    min_value=10,
    max_value=150,
    value=80,
    step=5,
)

acceptable_stress_threshold = st.sidebar.slider(
    "Estrés máximo aceptable",
    min_value=0.0,
    max_value=1.0,
    value=0.30,
    step=0.05,
)

max_percolation_mm = st.sidebar.number_input(
    "Drenaje profundo máximo aceptable (mm)",
    min_value=0.0,
    value=1.0,
    step=0.5,
)

st.sidebar.divider()

run_simulation = st.sidebar.button(
    "💧 Ejecutar motor",
    type="primary",
    use_container_width=True,
)


# ---------------------------------------------------------
# Selección del suelo activo
# ---------------------------------------------------------

selected_soil = None

if soil_source == "Manual":

    selected_soil = Soil(
        soil_type=None,
        sand_pct=sand_pct,
        silt_pct=silt_pct,
        clay_pct=clay_pct,
        field_capacity=field_capacity,
        wilting_point=wilting_point,
        saturation=saturation,
        bulk_density_g_cm3=None,
        root_zone_depth_m=root_depth_m,
    )

elif soil_source == "SoilGrids":

    selected_soil = (
        st.session_state.get(
            "soilgrids_soil"
        )
    )


# ---------------------------------------------------------
# Validaciones
# ---------------------------------------------------------

validation_errors = []

if soil_source == "Manual":

    if wilting_point >= field_capacity:
        validation_errors.append(
            "El punto de marchitez debe ser menor que la capacidad de campo."
        )

    if field_capacity >= saturation:
        validation_errors.append(
            "La capacidad de campo debe ser menor que la saturación."
        )

    if (
        soil_moisture_pct / 100.0
        >
        saturation
    ):
        validation_errors.append(
            "La humedad actual no puede superar la saturación."
        )

    texture_sum = (
        sand_pct
        +
        silt_pct
        +
        clay_pct
    )

    if not 99 <= texture_sum <= 101:
        validation_errors.append(
            "Arena + limo + arcilla deben sumar aproximadamente 100%."
        )

elif (
    soil_source == "SoilGrids"
    and
    selected_soil is not None
):

    if (
        soil_moisture_pct / 100.0
        <
        selected_soil.wilting_point
    ):
        st.warning(
            "La humedad introducida está por debajo del punto de marchitez estimado."
        )

for error in validation_errors:
    st.error(error)

if validation_errors:
    st.stop()


# ---------------------------------------------------------
# Tabs principales
# ---------------------------------------------------------

tab_overview, tab_inputs, tab_weather, tab_engine, tab_results, tab_trace = st.tabs(
    [
        "🧭 Arquitectura",
        "📥 Entradas y evidencia",
        "🌦️ Datos externos",
        "🧠 Motor de inferencia",
        "📊 Resultados",
        "🔎 Explicabilidad y trazabilidad",
    ]
)


# ---------------------------------------------------------
# TAB 1 · Arquitectura
# ---------------------------------------------------------

with tab_overview:

    st.subheader("Arquitectura funcional del motor")

    st.markdown(
        """
        El gemelo digital no depende de un único algoritmo.
        Combina una capa científica, una capa participativa,
        una capa de decisión y una capa de trazabilidad.
        """
    )

    inventory = build_engine_inventory()

    st.dataframe(
        inventory,
        use_container_width=True,
        hide_index=True,
    )

    st.markdown("#### Separación de responsabilidades")

    c1, c2, c3 = st.columns(3)

    with c1:
        st.info(
            "**Motor científico**\n\n"
            "Representa el estado hídrico y simula escenarios."
        )

    with c2:
        st.info(
            "**ML complementario**\n\n"
            "Predice variables futuras; no sustituye la decisión científica."
        )

    with c3:
        st.info(
            "**HITL participativo**\n\n"
            "El agricultor puede aceptar, modificar o rechazar una recomendación."
        )

    st.markdown(
        """
        <div class="mini-note">
            <strong>Principio del sistema:</strong>
            ML predicts; the engine decides.
            El Random Forest es una señal complementaria,
            mientras que las restricciones, la evidencia y el motor de decisión
            gobiernan la recomendación final.
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("#### Flujo de conocimiento del agricultor")

    farmer_flow = pd.DataFrame(
        [
            {
                "Tipo": "OBSERVATION",
                "Uso": "Contexto y contraste",
                "¿Sobrescribe TwinState?": "No",
            },
            {
                "Tipo": "EVENT",
                "Uso": "Valida, registra y puede disparar recomputación",
                "¿Sobrescribe TwinState?": "No",
            },
            {
                "Tipo": "CONSTRAINT",
                "Uso": "Filtra acciones factibles",
                "¿Sobrescribe TwinState?": "No",
            },
            {
                "Tipo": "PREFERENCE",
                "Uso": "Reordena alternativas",
                "¿Sobrescribe TwinState?": "No",
            },
            {
                "Tipo": "LOCAL_KNOWLEDGE",
                "Uso": "Califica supuestos y contexto",
                "¿Sobrescribe TwinState?": "No",
            },
        ]
    )

    st.dataframe(
        farmer_flow,
        use_container_width=True,
        hide_index=True,
    )


# ---------------------------------------------------------
# TAB 2 · Entradas y evidencia
# ---------------------------------------------------------

with tab_inputs:

    st.subheader("Estado de entrada del laboratorio")

    display_fc = None
    display_wp = None

    if selected_soil is not None:

        display_fc = (
            selected_soil.field_capacity
            * 100
        )

        display_wp = (
            selected_soil.wilting_point
            * 100
        )

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "Humedad del suelo",
        f"{soil_moisture_pct:.1f} %",
    )

    c2.metric(
        "Capacidad de campo",
        (
            f"{display_fc:.1f} %"
            if display_fc is not None
            else "N/D"
        ),
    )

    c3.metric(
        "Punto de marchitez",
        (
            f"{display_wp:.1f} %"
            if display_wp is not None
            else "N/D"
        ),
    )

    c4.metric(
        "ET0",
        f"{et0_mm_day:.2f} mm/d",
    )

    c5, c6, c7, c8 = st.columns(4)

    c5.metric(
        "ETc estimada",
        f"{et0_mm_day * kc:.2f} mm/d",
    )

    c6.metric(
        "Kc",
        f"{kc:.2f}",
    )

    c7.metric(
        "Profundidad radicular",
        f"{root_depth_m:.2f} m",
    )

    c8.metric(
        "Fuente de suelo",
        soil_source,
    )

    st.markdown("#### Procedencia de las entradas")

    weather_source_label = (
        "NASA POWER"
        if weather_mode == "NASA POWER descargado"
        else "Clima simulado"
    )

    st.dataframe(
        build_provenance_table(
            soil_source=soil_source,
            weather_source=weather_source_label,
        ),
        use_container_width=True,
        hide_index=True,
    )

    if (
        soil_source == "SoilGrids"
        and
        "soilgrids_soil" in st.session_state
    ):

        soil_data = (
            st.session_state[
                "soilgrids_soil"
            ]
        )

        st.markdown("#### Propiedades derivadas de SoilGrids")

        s1, s2, s3 = st.columns(3)

        s1.metric(
            "Arena",
            f"{soil_data.sand_pct:.1f}%",
        )

        s1.metric(
            "Capacidad de campo",
            f"{soil_data.field_capacity:.3f}",
        )

        s2.metric(
            "Limo",
            f"{soil_data.silt_pct:.1f}%",
        )

        s2.metric(
            "Punto de marchitez",
            f"{soil_data.wilting_point:.3f}",
        )

        s3.metric(
            "Arcilla",
            f"{soil_data.clay_pct:.1f}%",
        )

        s3.metric(
            "Densidad aparente",
            (
                f"{soil_data.bulk_density_g_cm3:.2f} g/cm³"
                if soil_data.bulk_density_g_cm3
                is not None
                else "N/D"
            ),
        )

    if (
        soil_source == "SoilGrids"
        and
        "soilgrids_profile" in st.session_state
    ):

        profile = (
            st.session_state[
                "soilgrids_profile"
            ]
        )

        rows = []

        for layer in profile.layers:

            rows.append(
                {
                    "Profundidad":
                        f"{layer.depth_top_cm}-{layer.depth_bottom_cm} cm",
                    "Arena (%)":
                        layer.sand_pct,
                    "Limo (%)":
                        layer.silt_pct,
                    "Arcilla (%)":
                        layer.clay_pct,
                    "Densidad":
                        layer.bulk_density_g_cm3,
                    "SOC":
                        layer.organic_carbon_g_kg,
                    "pH":
                        layer.ph_h2o,
                    "WV33 (%)":
                        layer.water_content_33kpa_pct,
                    "WV1500 (%)":
                        layer.water_content_1500kpa_pct,
                }
            )

        st.dataframe(
            pd.DataFrame(rows),
            use_container_width=True,
            hide_index=True,
        )


# ---------------------------------------------------------
# TAB 3 · Datos externos
# ---------------------------------------------------------

with tab_weather:

    st.subheader("NASA POWER + ET0 FAO-56")

    st.caption(
        "Permite observar la evidencia meteorológica externa "
        "que alimenta el estado y la simulación."
    )

    nasa_col1, nasa_col2 = st.columns(2)

    with nasa_col1:

        nasa_latitude = st.number_input(
            "Latitud NASA POWER",
            value=-6.77,
            format="%.6f",
            key="nasa_latitude",
        )

    with nasa_col2:

        nasa_longitude = st.number_input(
            "Longitud NASA POWER",
            value=-79.84,
            format="%.6f",
            key="nasa_longitude",
        )

    d1, d2 = st.columns(2)

    with d1:
        nasa_start_date = st.date_input(
            "Fecha inicial",
            value=date.today() - timedelta(days=7),
            key="nasa_start_date",
        )

    with d2:
        nasa_end_date = st.date_input(
            "Fecha final",
            value=date.today() - timedelta(days=1),
            key="nasa_end_date",
        )

    if st.button(
        "🌎 Descargar clima NASA POWER",
        use_container_width=True,
    ):

        try:

            nasa_client = NASAPowerClient()

            nasa_weather = (
                nasa_client.get_daily_weather(
                    latitude=nasa_latitude,
                    longitude=nasa_longitude,
                    start_date=nasa_start_date,
                    end_date=nasa_end_date,
                )
            )

            nasa_elevation = 30.0

            nasa_weather = nasa_client.add_et0(
                weather_series=nasa_weather,
                latitude=nasa_latitude,
                elevation_m=nasa_elevation,
            )

            st.session_state[
                "nasa_weather"
            ] = nasa_weather

            st.success(
                f"{len(nasa_weather)} días obtenidos correctamente."
            )

        except (
            ValueError,
            NASAPowerError,
        ) as exc:

            st.error(
                str(exc)
            )

    if "nasa_weather" in st.session_state:

        nasa_weather = st.session_state[
            "nasa_weather"
        ]

        nasa_df = pd.DataFrame(
            [
                {
                    "Fecha": w.timestamp.date(),
                    "T media (°C)":
                        w.temperature_c,
                    "T min (°C)":
                        w.temperature_min_c,
                    "T max (°C)":
                        w.temperature_max_c,
                    "HR (%)":
                        w.relative_humidity_pct,
                    "Lluvia (mm)":
                        w.rainfall_mm,
                    "Viento (m/s)":
                        w.wind_speed_m_s,
                    "Radiación (MJ/m²/día)":
                        w.solar_radiation_mj_m2_day,
                    "ET0 FAO-56 (mm/día)":
                        w.et0_mm_day,
                }
                for w in nasa_weather
            ]
        )

        st.dataframe(
            nasa_df,
            use_container_width=True,
            hide_index=True,
        )

        if not nasa_df.empty:

            fig_weather = px.line(
                nasa_df,
                x="Fecha",
                y=[
                    "T media (°C)",
                    "ET0 FAO-56 (mm/día)",
                    "Lluvia (mm)",
                ],
                markers=True,
            )

            st.plotly_chart(
                fig_weather,
                use_container_width=True,
            )


# ---------------------------------------------------------
# Ejecución del motor
# ---------------------------------------------------------

if run_simulation:

    if selected_soil is None:

        st.error(
            "No existe un suelo válido seleccionado. "
            "Si elegiste SoilGrids, primero consulta SoilGrids."
        )

        st.stop()

    start_date = date.today()

    weather_series = build_weather_series(
        start_date=start_date,
        days=simulation_days,
        temperature_c=temperature_c,
        humidity_pct=humidity_pct,
        rainfall_mm=rainfall_mm,
        et0_mm_day=et0_mm_day,
    )

    if (
        weather_mode == "NASA POWER descargado"
        and
        "nasa_weather" in st.session_state
    ):

        source_weather = st.session_state[
            "nasa_weather"
        ]

        if len(source_weather) >= simulation_days:
            weather_series = source_weather[
                :simulation_days
            ]

        else:
            st.warning(
                "NASA POWER tiene menos días que el horizonte solicitado. "
                "Se utilizará el clima simulado para mantener el horizonte completo."
            )

    irrigation_options = list(
        range(
            0,
            max_irrigation + irrigation_step,
            irrigation_step,
        )
    )

    state = build_twin_state(
        soil=selected_soil,
        soil_moisture_pct=soil_moisture_pct,
        crop_name=crop_name,
        kc=kc,
        root_depth_m=root_depth_m,
        depletion_fraction_p=depletion_fraction_p,
        temperature_c=temperature_c,
        humidity_pct=humidity_pct,
        rainfall_mm=rainfall_mm,
        et0_mm_day=et0_mm_day,
    )

    scenario_engine = ScenarioEngine()

    comparison = (
        scenario_engine.compare_irrigation_scenarios(
            initial_state=state,
            weather_series=weather_series,
            irrigation_options_mm=irrigation_options,
            irrigation_day=start_date,
        )
    )

    recommendation_engine = RecommendationEngine(
        acceptable_stress_threshold=(
            acceptable_stress_threshold
        ),
        max_deep_percolation_mm=(
            max_percolation_mm
        ),
    )

    recommendation = (
        recommendation_engine.recommend(
            comparison
        )
    )

    st.session_state[
        "comparison"
    ] = comparison

    st.session_state[
        "recommendation"
    ] = recommendation

    st.session_state[
        "lab_twin_state"
    ] = state

    st.session_state[
        "lab_run_timestamp"
    ] = datetime.now()

    st.toast(
        "Motor ejecutado correctamente.",
        icon="✅",
    )


# ---------------------------------------------------------
# TAB 4 · Motor de inferencia
# ---------------------------------------------------------

with tab_engine:

    st.subheader("Cómo decide el motor")

    st.markdown(
        """
        En este laboratorio, el proceso es explícito:
        se construye un `TwinState`, se simulan alternativas,
        se calculan métricas técnicas y luego se aplica
        `RecommendationEngine`.
        """
    )

    st.code(
        """
TwinState
   ↓
ScenarioEngine.compare_irrigation_scenarios(...)
   ↓
Escenarios con humedad, agotamiento, estrés, ETc y drenaje
   ↓
RecommendationEngine.recommend(...)
   ↓
Alternativa seleccionada + reason_codes
        """.strip(),
        language="text",
    )

    if (
        "recommendation" in st.session_state
        and
        "comparison" in st.session_state
    ):

        recommendation = st.session_state[
            "recommendation"
        ]

        st.markdown("#### Decisión actual")

        d1, d2, d3, d4 = st.columns(4)

        d1.metric(
            "Riego recomendado",
            f"{recommendation.recommended_irrigation_mm:.1f} mm",
        )

        d2.metric(
            "Humedad final",
            f"{recommendation.final_soil_moisture_pct:.1f} %",
        )

        d3.metric(
            "Estrés",
            f"{recommendation.final_water_stress_index:.2f}",
        )

        d4.metric(
            "Drenaje",
            f"{recommendation.deep_percolation_mm:.2f} mm",
        )

        st.dataframe(
            pd.DataFrame(
                scenario_explanation(
                    recommendation
                )
            ),
            use_container_width=True,
            hide_index=True,
        )

    else:

        st.info(
            "Ejecuta el motor desde la barra lateral "
            "para observar la explicación paso a paso."
        )

    st.markdown("#### Qué no hace este script por sí solo")

    st.markdown(
        """
        - No sustituye la API principal.
        - No modifica la base de datos del sistema.
        - No crea DecisionTrace persistente.
        - No ejecuta el flujo HITL de producción.
        - No ejecuta aquí el Random Forest complementario.
        - No reemplaza el pipeline AquaCrop validado del motor principal.
        """
    )

    st.markdown(
        """
        <div class="warning-note">
            Estas capacidades existen en el proyecto principal,
            pero este archivo Streamlit funciona como laboratorio explicable
            y demostrador del razonamiento local.
        </div>
        """,
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------
# TAB 5 · Resultados
# ---------------------------------------------------------

with tab_results:

    if (
        "comparison" not in st.session_state
        or
        "recommendation" not in st.session_state
    ):

        st.info(
            "Todavía no hay resultados. "
            "Configura los parámetros y pulsa «Ejecutar motor»."
        )

    else:

        comparison = st.session_state[
            "comparison"
        ]

        recommendation = st.session_state[
            "recommendation"
        ]

        df = pd.DataFrame(
            comparison.to_dicts()
        )

        st.subheader("Recomendación técnica")

        r1, r2, r3, r4 = st.columns(4)

        r1.metric(
            "💧 Riego recomendado",
            f"{recommendation.recommended_irrigation_mm:.1f} mm",
        )

        r2.metric(
            "Humedad final estimada",
            f"{recommendation.final_soil_moisture_pct:.1f} %",
        )

        r3.metric(
            "Estrés estimado",
            f"{recommendation.final_water_stress_index:.2f}",
        )

        r4.metric(
            "Drenaje profundo",
            f"{recommendation.deep_percolation_mm:.2f} mm",
        )

        if recommendation.decision_type == "NO_IRRIGATION_REQUIRED":

            st.success(
                "No se requiere riego bajo las condiciones simuladas."
            )

        elif recommendation.decision_type == "ACCEPTABLE_MINIMUM_WATER":

            st.success(
                "Se encontró una alternativa técnicamente aceptable "
                "con la menor cantidad de agua evaluada."
            )

        else:

            st.warning(
                "Ningún escenario cumple completamente los criterios. "
                "Se muestra la mejor alternativa disponible."
            )

        st.write(
            "**Nivel de estrés previsto:**",
            stress_label(
                recommendation.final_water_stress_index
            ),
        )

        st.markdown("#### Razones de la recomendación")

        for reason_code in recommendation.reason_codes:
            st.write(
                "✓",
                translate_reason_code(
                    reason_code
                ),
            )

        st.markdown("#### Comparación de escenarios")

        display_df = df.copy()

        display_df = display_df.rename(
            columns={
                "scenario_id": "Escenario",
                "irrigation_mm": "Riego (mm)",
                "final_soil_moisture_pct": "Humedad final (%)",
                "root_zone_depletion_mm": "Déficit (mm)",
                "water_stress_index": "Estrés",
                "total_etc_mm": "ETc total (mm)",
                "total_rainfall_mm": "Lluvia total (mm)",
                "deep_percolation_mm": "Drenaje (mm)",
                "technical_status": "Estado técnico",
            }
        )

        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True,
        )

        chart1, chart2 = st.columns(2)

        with chart1:

            fig_stress = px.line(
                df,
                x="irrigation_mm",
                y="water_stress_index",
                markers=True,
                labels={
                    "irrigation_mm":
                        "Riego aplicado (mm)",
                    "water_stress_index":
                        "Índice de estrés hídrico",
                },
            )

            fig_stress.add_hline(
                y=acceptable_stress_threshold,
                line_dash="dash",
                annotation_text="Umbral aceptable",
            )

            st.plotly_chart(
                fig_stress,
                use_container_width=True,
            )

        with chart2:

            fig_percolation = px.bar(
                df,
                x="irrigation_mm",
                y="deep_percolation_mm",
                labels={
                    "irrigation_mm":
                        "Riego aplicado (mm)",
                    "deep_percolation_mm":
                        "Drenaje profundo (mm)",
                },
            )

            st.plotly_chart(
                fig_percolation,
                use_container_width=True,
            )

        simulation_soil = (
            recommendation
            .selected_scenario
            .simulation
            .initial_state
            .soil
        )

        selected_fc_pct = (
            simulation_soil.field_capacity
            * 100
        )

        selected_wp_pct = (
            simulation_soil.wilting_point
            * 100
        )

        fig_moisture = px.line(
            df,
            x="irrigation_mm",
            y="final_soil_moisture_pct",
            markers=True,
            labels={
                "irrigation_mm":
                    "Riego aplicado (mm)",
                "final_soil_moisture_pct":
                    "Humedad final (%)",
            },
        )

        fig_moisture.add_hline(
            y=selected_fc_pct,
            line_dash="dash",
            annotation_text="Capacidad de campo",
        )

        fig_moisture.add_hline(
            y=selected_wp_pct,
            line_dash="dot",
            annotation_text="Punto de marchitez",
        )

        st.plotly_chart(
            fig_moisture,
            use_container_width=True,
        )

        st.markdown("#### Evolución temporal del escenario recomendado")

        selected_simulation = (
            recommendation
            .selected_scenario
            .simulation
        )

        trajectory_df = pd.DataFrame(
            selected_simulation.to_dicts()
        )

        fig_trajectory = px.line(
            trajectory_df,
            x="date",
            y="soil_moisture_pct",
            markers=True,
            labels={
                "date":
                    "Fecha",
                "soil_moisture_pct":
                    "Humedad del suelo (%)",
            },
        )

        fig_trajectory.add_hline(
            y=selected_fc_pct,
            line_dash="dash",
            annotation_text="Capacidad de campo",
        )

        fig_trajectory.add_hline(
            y=selected_wp_pct,
            line_dash="dot",
            annotation_text="Punto de marchitez",
        )

        st.plotly_chart(
            fig_trajectory,
            use_container_width=True,
        )


# ---------------------------------------------------------
# TAB 6 · Explicabilidad y trazabilidad
# ---------------------------------------------------------

with tab_trace:

    st.subheader("Explicabilidad del laboratorio")

    if (
        "recommendation" in st.session_state
        and
        "comparison" in st.session_state
    ):

        recommendation = st.session_state[
            "recommendation"
        ]

        st.markdown("#### Reason codes")

        reason_rows = []

        for reason_code in recommendation.reason_codes:

            reason_rows.append(
                {
                    "Código": reason_code,
                    "Explicación": translate_reason_code(
                        reason_code
                    ),
                }
            )

        st.dataframe(
            pd.DataFrame(
                reason_rows
            ),
            use_container_width=True,
            hide_index=True,
        )

        st.markdown("#### Registro estructurado de la decisión")

        run_timestamp = st.session_state.get(
            "lab_run_timestamp"
        )

        trace_preview = {
            "run_timestamp": (
                run_timestamp.isoformat()
                if run_timestamp
                else None
            ),
            "decision_engine":
                "RecommendationEngine",
            "scenario_engine":
                "ScenarioEngine",
            "recommended_irrigation_mm":
                recommendation.recommended_irrigation_mm,
            "decision_type":
                recommendation.decision_type,
            "reason_codes":
                recommendation.reason_codes,
            "stress_threshold":
                acceptable_stress_threshold,
            "max_deep_percolation_mm":
                max_percolation_mm,
            "soil_source":
                soil_source,
            "weather_mode":
                weather_mode,
        }

        st.json(
            trace_preview
        )

        with st.expander(
            "Salida estructurada completa del RecommendationEngine"
        ):
            st.json(
                recommendation.to_dict()
            )

    else:

        st.info(
            "Ejecuta el motor para construir una traza explicable."
        )

    st.markdown("#### Cómo se conecta con el sistema completo")

    integration_df = pd.DataFrame(
        [
            {
                "Elemento": "DecisionTrace",
                "Laboratorio": "Vista previa local",
                "Sistema principal": "Persistente",
            },
            {
                "Elemento": "HITL",
                "Laboratorio": "Explicado",
                "Sistema principal": "ACCEPT / MODIFY / REJECT",
            },
            {
                "Elemento": "ML",
                "Laboratorio": "Arquitectura explicada",
                "Sistema principal": "Random Forest + incertidumbre + SHAP",
            },
            {
                "Elemento": "AquaCrop",
                "Laboratorio": "Arquitectura explicada",
                "Sistema principal": "Escenarios científicos validados",
            },
            {
                "Elemento": "Provenance",
                "Laboratorio": "Tabla de fuentes",
                "Sistema principal": "Persistencia y trazabilidad",
            },
        ]
    )

    st.dataframe(
        integration_df,
        use_container_width=True,
        hide_index=True,
    )

    st.markdown(
        """
        <div class="mini-note">
            Para una demostración académica, esta pantalla permite explicar
            qué entra al motor, qué deriva el modelo, qué reglas se aplican
            y por qué se obtiene una recomendación. La plataforma principal
            conserva además la gobernanza, permisos, trazabilidad persistente,
            HITL, ML y el pipeline científico AquaCrop.
        </div>
        """,
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------
# Pie
# ---------------------------------------------------------

st.divider()

st.caption(
    f"{settings.app_name} · "
    f"Entorno: {settings.app_env} · "
    "Laboratorio explicable del motor de decisión"
)
