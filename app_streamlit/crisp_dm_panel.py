from __future__ import annotations

from pathlib import Path

import pandas as pd
import streamlit as st


from ml.datasets import (
    build_eda_package,
    load_training_dataset,
)

from ml.features import (
    cv_fold_summary,
    feature_inventory,
    leakage_audit,
    preparation_interpretation,
    predictor_missingness,
    temporal_split_summary,
)

from ml.reporting import (
    HTML_REPORT_PATH,
    PDF_REPORT_PATH,
    build_reporting_package,
    generate_html_report,
    generate_pdf_report,
)


# =========================================================
# PATHS
# =========================================================

PROJECT_ROOT = (
    Path(__file__)
    .resolve()
    .parent
    .parent
)


# =========================================================
# CACHE
# =========================================================

@st.cache_data(
    show_spinner=False,
)
def get_dataset() -> pd.DataFrame:

    return (
        load_training_dataset()
    )


@st.cache_data(
    show_spinner=False,
)
def get_eda_package() -> dict:

    dataframe = (
        load_training_dataset()
    )

    return (
        build_eda_package(
            dataframe
        )
    )


@st.cache_resource(
    show_spinner=False,
)
def get_reporting_package() -> dict:
    """
    This package includes the CRISP-DM artifacts,
    Permutation Importance and SHAP calculations.

    cache_resource prevents recomputation on every
    Streamlit interaction.
    """

    return (
        build_reporting_package()
    )


# =========================================================
# UI HELPERS
# =========================================================

def interpretation_box(
    interpretation: str,
    explainability: str,
) -> None:

    st.markdown(
        "##### Interpretación"
    )

    st.info(
        interpretation
    )


    st.markdown(
        "##### Explicabilidad"
    )

    st.success(
        explainability
    )


def render_report_item(
    item,
) -> None:

    st.markdown(
        f"### {item.title}"
    )


    if (
        item.kind
        ==
        "table"
        and
        item.dataframe
        is not None
    ):

        st.dataframe(
            item.dataframe,
            use_container_width=True,
            hide_index=True,
        )


    elif (
        item.kind
        ==
        "figure"
        and
        item.figure
        is not None
    ):

        st.pyplot(
            item.figure,
            use_container_width=True,
            clear_figure=False,
        )


    interpretation_box(
        interpretation=
            item.interpretation,

        explainability=
            item.explainability,
    )


    st.divider()


def find_item(
    items: list,
    key: str,
):

    for item in items:

        if (
            item.key
            ==
            key
        ):

            return item


    return None


def render_item_if_exists(
    items: list,
    key: str,
) -> None:

    item = (
        find_item(
            items,
            key,
        )
    )


    if item is not None:

        render_report_item(
            item
        )


def metric_value(
    dataframe: pd.DataFrame,
    model_name: str,
    column: str,
) -> float | None:

    row = dataframe[
        dataframe[
            "model_name"
        ]
        ==
        model_name
    ]


    if row.empty:

        return None


    value = row.iloc[0][
        column
    ]


    if pd.isna(
        value
    ):

        return None


    return float(
        value
    )


# =========================================================
# CRISP-DM STATUS
# =========================================================

def render_status_header(
    artifacts: dict,
) -> None:

    selection_metadata = (
        artifacts[
            "selection_metadata"
        ]
    )


    selected_model = str(
        selection_metadata[
            "selected_model"
        ]
    )


    final_metrics = (
        artifacts[
            "final_metrics"
        ]
    )


    selected_mae = (
        metric_value(
            final_metrics,
            selected_model,
            "mae",
        )
    )


    selected_rmse = (
        metric_value(
            final_metrics,
            selected_model,
            "rmse",
        )
    )


    selected_r2 = (
        metric_value(
            final_metrics,
            selected_model,
            "r2",
        )
    )


    persistence_mae = (
        metric_value(
            final_metrics,
            "Persistence",
            "mae",
        )
    )


    c1, c2, c3, c4 = st.columns(
        4
    )


    c1.metric(
        "Modelo ML seleccionado",
        selected_model,
    )


    c2.metric(
        "MAE final 2025",
        (
            f"{selected_mae:.6f}"
            if selected_mae
            is not None
            else "N/D"
        ),
    )


    c3.metric(
        "RMSE final 2025",
        (
            f"{selected_rmse:.6f}"
            if selected_rmse
            is not None
            else "N/D"
        ),
    )


    c4.metric(
        "R² final 2025",
        (
            f"{selected_r2:.4f}"
            if selected_r2
            is not None
            else "N/D"
        ),
    )


    if (
        selected_mae
        is not None
        and
        persistence_mae
        is not None
        and
        persistence_mae
        >
        0
    ):

        improvement = (
            (
                persistence_mae
                -
                selected_mae
            )
            /
            persistence_mae
            *
            100
        )


        st.caption(
            "Mejora numérica de MAE frente a "
            f"persistencia en 2025: "
            f"{improvement:.2f} %. "
            "Este porcentaje es descriptivo; "
            "la significancia estadística se evalúa "
            "por separado."
        )


# =========================================================
# STAGE 0 · CONTEXT
# =========================================================

def render_crisp_dm_context() -> None:

    st.markdown(
        """
        <div style="
            padding: 1rem 1.1rem;
            border: 1px solid rgba(120,120,120,.25);
            border-radius: 12px;
            margin-bottom: 1rem;
        ">
            <strong>Alcance del laboratorio CRISP-DM</strong><br><br>

            Este módulo estudia el componente predictivo
            complementario de humedad del suelo a +24 h.

            <br><br>

            <strong>No sustituye el motor de inferencia y decisión
            de AgroTwin.</strong> El modelo ML no modifica
            TrustedState, no selecciona directamente el riego
            y no modifica las recomendaciones generadas por
            el motor de decisión.
        </div>
        """,
        unsafe_allow_html=True,
    )


    st.code(
        """
NOAA USCRN · Datos reales
        ↓
EDA y calidad
        ↓
Preparación temporal
        ↓
Entrenamiento de candidatos
        ↓
Selección con validación 2024
        ↓
Validación cruzada temporal
        ↓
Pruebas estadísticas
        ↓
Holdout final 2025
        ↓
Interpretabilidad / XAI
        ↓
Reporte reproducible
        """.strip(),
        language="text",
    )


# =========================================================
# STAGE 1 · DATA UNDERSTANDING / EDA
# =========================================================

def render_eda(
    dataframe: pd.DataFrame,
    eda: dict,
    items: list,
) -> None:

    st.header(
        "1 · EDA y comprensión de los datos"
    )


    overview = (
        eda[
            "overview"
        ]
    )


    c1, c2, c3, c4 = st.columns(
        4
    )


    c1.metric(
        "Observaciones",
        f"{overview['rows']:,}",
    )


    c2.metric(
        "Variables",
        overview[
            "columns"
        ],
    )


    c3.metric(
        "Estación",
        (
            ", ".join(
                overview[
                    "stations"
                ]
            )
        ),
    )


    c4.metric(
        "Horizonte",
        (
            f"{overview['prediction_horizon_hours']} h"
        ),
    )


    st.markdown(
        "#### Resumen del dataset"
    )


    overview_table = pd.DataFrame(
        [
            {
                "Aspecto":
                    "Fuente",

                "Valor":
                    "NOAA USCRN",
            },
            {
                "Aspecto":
                    "Estación",

                "Valor":
                    ", ".join(
                        overview[
                            "stations"
                        ]
                    ),
            },
            {
                "Aspecto":
                    "Inicio",

                "Valor":
                    overview[
                        "start"
                    ],
            },
            {
                "Aspecto":
                    "Fin",

                "Valor":
                    overview[
                        "end"
                    ],
            },
            {
                "Aspecto":
                    "Años",

                "Valor":
                    ", ".join(
                        str(
                            year
                        )
                        for year
                        in overview[
                            "years"
                        ]
                    ),
            },
            {
                "Aspecto":
                    "Target",

                "Valor":
                    overview[
                        "delta_target"
                    ],
            },
            {
                "Aspecto":
                    "Humedad futura",

                "Valor":
                    overview[
                        "future_target"
                    ],
            },
        ]
    )


    st.dataframe(
        overview_table,
        use_container_width=True,
        hide_index=True,
    )


    interpretation_box(
        interpretation=(
            eda[
                "interpretations"
            ][
                "dataset"
            ]
        ),

        explainability=(
            "El dataset fue construido a partir de "
            "observaciones horarias NOAA USCRN. "
            "Las variables derivadas conservan la "
            "secuencia temporal y el target representa "
            "el cambio real observado a +24 horas."
        ),
    )


    st.divider()


    render_item_if_exists(
        items,
        "data_quality",
    )


    render_item_if_exists(
        items,
        "temporal_coverage",
    )


    st.markdown(
        "### Tabla · Valores faltantes"
    )


    st.dataframe(
        eda[
            "missing"
        ].head(
            20
        ),
        use_container_width=True,
        hide_index=True,
    )


    interpretation_box(
        interpretation=(
            eda[
                "interpretations"
            ][
                "missingness"
            ]
        ),

        explainability=(
            "Los faltantes de los lags iniciales son "
            "consecuencia natural de construir variables "
            "históricas. La imputación no se realiza "
            "globalmente: cada pipeline la aprende usando "
            "solamente sus datos de entrenamiento."
        ),
    )


    st.divider()


    render_item_if_exists(
        items,
        "target_distribution",
    )


    render_item_if_exists(
        items,
        "target_correlations",
    )


    with st.expander(
        "Ver estadísticos descriptivos completos"
    ):

        st.dataframe(
            eda[
                "numeric_summary"
            ],
            use_container_width=True,
            hide_index=True,
        )


        interpretation_box(
            interpretation=(
                "Los estadísticos descriptivos permiten "
                "examinar tendencia central, dispersión "
                "y valores extremos antes de entrenar."
            ),

            explainability=(
                "Esta tabla describe los datos de entrada "
                "y el target; no representa todavía "
                "rendimiento de ningún modelo."
            ),
        )


# =========================================================
# STAGE 2 · DATA PREPARATION
# =========================================================

def render_preparation(
    dataframe: pd.DataFrame,
) -> None:

    st.header(
        "2 · Preparación de datos"
    )


    inventory = (
        feature_inventory()
    )


    st.markdown(
        "### Inventario de variables predictoras"
    )


    st.dataframe(
        inventory,
        use_container_width=True,
        hide_index=True,
    )


    interpretation_box(
        interpretation=(
            "El modelo utiliza humedad actual e histórica, "
            "meteorología actual, acumulados y medias "
            "móviles, además de codificaciones cíclicas "
            "del tiempo."
        ),

        explainability=(
            "Las variables históricas representan solamente "
            "información disponible en el instante de "
            "predicción. El target y la humedad futura "
            "se excluyen de FEATURES."
        ),
    )


    st.divider()


    st.markdown(
        "### Auditoría de data leakage"
    )


    leakage = (
        leakage_audit(
            dataframe
        )
    )


    st.dataframe(
        leakage,
        use_container_width=True,
        hide_index=True,
    )


    interpretation_box(
        interpretation=(
            "Todas las verificaciones estructurales deben "
            "permanecer en PASS. Esto confirma que la "
            "partición respeta el orden temporal y que "
            "ninguna variable futura se entrega como "
            "entrada al modelo."
        ),

        explainability=(
            "Evitar data leakage es indispensable porque "
            "un modelo puede mostrar métricas artificialmente "
            "altas si durante entrenamiento accede directa "
            "o indirectamente a información futura."
        ),
    )


    st.divider()


    st.markdown(
        "### Partición temporal"
    )


    split_table = (
        temporal_split_summary(
            dataframe
        )
    )


    st.dataframe(
        split_table,
        use_container_width=True,
        hide_index=True,
    )


    interpretation_box(
        interpretation=(
            preparation_interpretation(
                dataframe
            )
        ),

        explainability=(
            "2022–2023 se utiliza para entrenamiento, "
            "2024 para selección y 2025 permanece aislado "
            "hasta la evaluación final. No se realiza "
            "una división aleatoria de observaciones."
        ),
    )


    st.divider()


    st.markdown(
        "### Folds de validación temporal"
    )


    folds = (
        cv_fold_summary(
            dataframe
        )
    )


    st.dataframe(
        folds,
        use_container_width=True,
        hide_index=True,
    )


    interpretation_box(
        interpretation=(
            "Los folds aplican una ventana expansiva: "
            "cada entrenamiento usa únicamente datos "
            "anteriores al período evaluado."
        ),

        explainability=(
            "Se deja además un gap de 24 observaciones "
            "entre entrenamiento y validación para reducir "
            "solapamiento alrededor del horizonte +24 h."
        ),
    )


    with st.expander(
        "Ver faltantes por predictor"
    ):

        missing = (
            predictor_missingness(
                dataframe
            )
        )


        st.dataframe(
            missing,
            use_container_width=True,
            hide_index=True,
        )


# =========================================================
# STAGE 3 · TRAINING / MODEL SELECTION
# =========================================================

def render_training(
    artifacts: dict,
    items: list,
) -> None:

    st.header(
        "3 · Entrenamientos y selección del modelo"
    )


    st.markdown(
        """
        Los candidatos entrenados bajo las mismas
        condiciones fueron:

        - Ridge
        - Random Forest
        - Extra Trees
        - Hist Gradient Boosting

        Se utiliza además **Persistence** como benchmark
        no entrenado.
        """
    )


    render_item_if_exists(
        items,
        "model_selection_table",
    )


    render_item_if_exists(
        items,
        "model_selection_figure",
    )


    selected_model = (
        artifacts[
            "selection_metadata"
        ][
            "selected_model"
        ]
    )


    st.success(
        "Candidato ML seleccionado durante la etapa "
        f"de modelado: **{selected_model}**."
    )


    st.warning(
        "Seleccionado no significa automáticamente "
        "«superior estadísticamente a todos». "
        "La conclusión depende de la validación cruzada "
        "y de las pruebas estadísticas posteriores."
    )


# =========================================================
# STAGE 4 · CV
# =========================================================

def render_validation(
    artifacts: dict,
    items: list,
) -> None:

    st.header(
        "4 · Validación cruzada temporal"
    )


    render_item_if_exists(
        items,
        "cv_table",
    )


    render_item_if_exists(
        items,
        "cv_figure",
    )


    evaluation = (
        artifacts[
            "evaluation"
        ]
    )


    interpretation = (
        evaluation.get(
            "interpretation",
            {}
        )
    )


    if (
        "cross_validation"
        in interpretation
    ):

        st.markdown(
            "### Interpretación global"
        )

        st.info(
            interpretation[
                "cross_validation"
            ]
        )


        st.success(
            "La validación temporal evalúa capacidad "
            "de generalización cronológica. A diferencia "
            "de una división aleatoria, reproduce mejor "
            "el escenario real en el que el modelo debe "
            "pronosticar observaciones futuras."
        )


# =========================================================
# STAGE 5 · STATISTICS
# =========================================================

def render_statistics(
    artifacts: dict,
    items: list,
) -> None:

    st.header(
        "5 · Pruebas estadísticas rigurosas"
    )


    friedman = (
        artifacts[
            "friedman"
        ]
    )


    f1, f2, f3 = st.columns(
        3
    )


    f1.metric(
        "Friedman χ²",
        f"{friedman['statistic']:.4f}",
    )


    f2.metric(
        "p-value Friedman",
        f"{friedman['p_value']:.3e}",
    )


    f3.metric(
        "Bloques diarios",
        friedman[
            "blocks"
        ],
    )


    st.info(
        "Friedman permite determinar si existen "
        "diferencias globales entre los métodos. "
        "Un resultado significativo no identifica "
        "por sí solo cuál método es superior."
    )


    render_item_if_exists(
        items,
        "statistical_tests",
    )


    st.markdown(
        "### Holdout final 2025"
    )


    render_item_if_exists(
        items,
        "final_holdout_table",
    )


    render_item_if_exists(
        items,
        "final_timeseries",
    )


    render_item_if_exists(
        items,
        "bootstrap",
    )


    render_item_if_exists(
        items,
        "residuals",
    )


    evaluation = (
        artifacts[
            "evaluation"
        ]
    )


    interpretation = (
        evaluation.get(
            "interpretation",
            {}
        )
    )


    st.markdown(
        "### Síntesis estadística"
    )


    for key in [
        "final_holdout",
        "diebold_mariano",
        "wilcoxon",
        "bootstrap",
    ]:

        if (
            key
            in interpretation
        ):

            st.write(
                "•",
                interpretation[
                    key
                ],
            )


# =========================================================
# STAGE 6 · XAI
# =========================================================

def render_xai(
    items: list,
) -> None:

    st.header(
        "6 · Interpretabilidad y explicabilidad"
    )


    st.markdown(
        """
        La explicabilidad corresponde al **modelo
        predictivo complementario de humedad del suelo**.

        No explica la decisión de riego del motor de
        inferencia. Esa decisión mantiene su propia
        trazabilidad mediante escenarios, restricciones,
        criterios técnicos y reason codes.
        """
    )


    render_item_if_exists(
        items,
        "permutation_table",
    )


    render_item_if_exists(
        items,
        "permutation_importance",
    )


    render_item_if_exists(
        items,
        "shap_global",
    )


    render_item_if_exists(
        items,
        "shap_local",
    )


# =========================================================
# STAGE 7 · REPORTS
# =========================================================

def render_reports(
    package: dict,
) -> None:

    st.header(
        "7 · Reportes"
    )


    artifacts = (
        package[
            "artifacts"
        ]
    )


    items = (
        package[
            "items"
        ]
    )


    st.markdown(
        """
        Los reportes reproducen las mismas tablas,
        figuras, interpretaciones y explicaciones que se
        muestran en este laboratorio.
        """
    )


    c1, c2 = st.columns(
        2
    )


    with c1:

        if st.button(
            "🔄 Regenerar reporte HTML",
            use_container_width=True,
        ):

            with st.spinner(
                "Generando HTML..."
            ):

                generate_html_report(
                    items=
                        items,

                    artifacts=
                        artifacts,
                )


            st.success(
                "Reporte HTML actualizado."
            )


    with c2:

        if st.button(
            "🔄 Regenerar reporte PDF",
            use_container_width=True,
        ):

            with st.spinner(
                "Generando PDF..."
            ):

                generate_pdf_report(
                    items=
                        items,

                    artifacts=
                        artifacts,
                )


            st.success(
                "Reporte PDF actualizado."
            )


    st.divider()


    d1, d2 = st.columns(
        2
    )


    with d1:

        if HTML_REPORT_PATH.exists():

            html_bytes = (
                HTML_REPORT_PATH
                .read_bytes()
            )


            st.download_button(
                label=
                    "⬇️ Descargar reporte HTML",

                data=
                    html_bytes,

                file_name=
                    "AgroTwin_CRISP_DM_Report.html",

                mime=
                    "text/html",

                use_container_width=True,
            )


        else:

            st.warning(
                "El reporte HTML todavía no existe."
            )


    with d2:

        if PDF_REPORT_PATH.exists():

            pdf_bytes = (
                PDF_REPORT_PATH
                .read_bytes()
            )


            st.download_button(
                label=
                    "⬇️ Descargar reporte PDF",

                data=
                    pdf_bytes,

                file_name=
                    "AgroTwin_CRISP_DM_Report.pdf",

                mime=
                    "application/pdf",

                use_container_width=True,
            )


        else:

            st.warning(
                "El reporte PDF todavía no existe."
            )


    st.markdown(
        "### Cobertura del reporte"
    )


    report_contents = pd.DataFrame(
        [
            {
                "Requisito":
                    "EDA",

                "Pantalla":
                    "Sí",

                "Reporte":
                    "Sí",
            },
            {
                "Requisito":
                    "Entrenamientos",

                "Pantalla":
                    "Sí",

                "Reporte":
                    "Sí",
            },
            {
                "Requisito":
                    "Selección del modelo",

                "Pantalla":
                    "Sí",

                "Reporte":
                    "Sí",
            },
            {
                "Requisito":
                    "Validación cruzada",

                "Pantalla":
                    "Sí",

                "Reporte":
                    "Sí",
            },
            {
                "Requisito":
                    "Pruebas estadísticas",

                "Pantalla":
                    "Sí",

                "Reporte":
                    "Sí",
            },
            {
                "Requisito":
                    "Interpretabilidad",

                "Pantalla":
                    "Sí",

                "Reporte":
                    "Sí",
            },
            {
                "Requisito":
                    "Explicabilidad",

                "Pantalla":
                    "Sí",

                "Reporte":
                    "Sí",
            },
        ]
    )


    st.dataframe(
        report_contents,
        use_container_width=True,
        hide_index=True,
    )


    interpretation_box(
        interpretation=(
            "El mismo conjunto de resultados alimenta "
            "la visualización Streamlit y los reportes "
            "HTML/PDF, reduciendo inconsistencias entre "
            "lo mostrado y lo documentado."
        ),

        explainability=(
            "Los reportes se generan directamente desde "
            "los artefactos reproducibles de entrenamiento "
            "y evaluación almacenados en "
            "artifacts/ml/crisp_dm."
        ),
    )


# =========================================================
# COMPLETE PANEL
# =========================================================

def render_crisp_dm_panel() -> None:

    st.subheader(
        "CRISP-DM · Motor predictivo complementario"
    )


    render_crisp_dm_context()


    refresh_col, status_col = st.columns(
        [
            1,
            3,
        ]
    )


    with refresh_col:

        if st.button(
            "↻ Recargar CRISP-DM",
            use_container_width=True,
        ):

            get_dataset.clear()

            get_eda_package.clear()

            get_reporting_package.clear()

            st.rerun()


    with status_col:

        st.caption(
            "Fuente: NOAA USCRN · AZ_Yuma_27_ENE · "
            "2022–2025 · horizonte predictivo +24 h."
        )


    try:

        dataframe = (
            get_dataset()
        )


        eda = (
            get_eda_package()
        )


        with st.spinner(
            "Cargando resultados, "
            "Permutation Importance y SHAP..."
        ):

            package = (
                get_reporting_package()
            )


    except Exception as exc:

        st.error(
            "No fue posible cargar el laboratorio "
            "CRISP-DM."
        )


        st.exception(
            exc
        )


        st.info(
            "Verifica que hayas ejecutado:\n\n"
            "`python -m ml.datasets`\n\n"
            "`python -m ml.features`\n\n"
            "`python -m ml.train`\n\n"
            "`python -m ml.evaluate`\n\n"
            "`python -m ml.reporting`"
        )


        return


    artifacts = (
        package[
            "artifacts"
        ]
    )


    items = (
        package[
            "items"
        ]
    )


    render_status_header(
        artifacts
    )


    st.divider()


    (
        tab_eda,
        tab_preparation,
        tab_training,
        tab_validation,
        tab_statistics,
        tab_xai,
        tab_reports,
    ) = st.tabs(
        [
            "1️⃣ EDA",
            "2️⃣ Preparación",
            "3️⃣ Entrenamientos",
            "4️⃣ Validación cruzada",
            "5️⃣ Pruebas estadísticas",
            "6️⃣ XAI",
            "7️⃣ Reportes",
        ]
    )


    with tab_eda:

        render_eda(
            dataframe=
                dataframe,

            eda=
                eda,

            items=
                items,
        )


    with tab_preparation:

        render_preparation(
            dataframe=
                dataframe,
        )


    with tab_training:

        render_training(
            artifacts=
                artifacts,

            items=
                items,
        )


    with tab_validation:

        render_validation(
            artifacts=
                artifacts,

            items=
                items,
        )


    with tab_statistics:

        render_statistics(
            artifacts=
                artifacts,

            items=
                items,
        )


    with tab_xai:

        render_xai(
            items=
                items,
        )


    with tab_reports:

        render_reports(
            package=
                package,
        )