from __future__ import annotations

import base64
import io
import json
from dataclasses import dataclass
from html import escape
from pathlib import Path
from typing import Any

import joblib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import shap

from sklearn.inspection import permutation_importance

from ml.datasets import (
    DELTA_TARGET,
    FUTURE_SOIL_MOISTURE,
    RAW_VARIABLES,
    TIMESTAMP_COLUMN,
    build_eda_package,
    load_training_dataset,
)

from ml.features import (
    FEATURES,
    final_holdout_dataset,
)


# =========================================================
# OPTIONAL PDF SUPPORT
# =========================================================

try:
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import (
        ParagraphStyle,
        getSampleStyleSheet,
    )
    from reportlab.lib.units import cm
    from reportlab.platypus import (
        Image,
        PageBreak,
        Paragraph,
        SimpleDocTemplate,
        Spacer,
        Table,
        TableStyle,
    )

    REPORTLAB_AVAILABLE = True

except ImportError:
    REPORTLAB_AVAILABLE = False


# =========================================================
# PATHS
# =========================================================

PROJECT_ROOT = (
    Path(__file__)
    .resolve()
    .parent
    .parent
)


EXPERIMENT_DIR = (
    PROJECT_ROOT
    / "artifacts"
    / "ml"
    / "crisp_dm"
)


REPORT_DIR = (
    EXPERIMENT_DIR
    / "reports"
)


ASSET_DIR = (
    REPORT_DIR
    / "assets"
)


MODEL_SELECTION_RESULTS_PATH = (
    EXPERIMENT_DIR
    / "model_selection_results.csv"
)


MODEL_SELECTION_METADATA_PATH = (
    EXPERIMENT_DIR
    / "model_selection_metadata.json"
)


CV_METRICS_PATH = (
    EXPERIMENT_DIR
    / "cv_fold_metrics.csv"
)


PAIRWISE_TESTS_PATH = (
    EXPERIMENT_DIR
    / "pairwise_statistical_tests.csv"
)


FINAL_TEST_METRICS_PATH = (
    EXPERIMENT_DIR
    / "final_test_metrics.csv"
)


FINAL_TEST_PREDICTIONS_PATH = (
    EXPERIMENT_DIR
    / "final_test_predictions.csv"
)


FRIEDMAN_PATH = (
    EXPERIMENT_DIR
    / "friedman_test.json"
)


BOOTSTRAP_PATH = (
    EXPERIMENT_DIR
    / "bootstrap_confidence_intervals.json"
)


RESIDUAL_DIAGNOSTICS_PATH = (
    EXPERIMENT_DIR
    / "residual_diagnostics.json"
)


EVALUATION_SUMMARY_PATH = (
    EXPERIMENT_DIR
    / "evaluation_summary.json"
)


FINAL_SELECTED_MODEL_PATH = (
    EXPERIMENT_DIR
    / "final_selected_model.joblib"
)


HTML_REPORT_PATH = (
    REPORT_DIR
    / "AgroTwin_CRISP_DM_Report.html"
)


PDF_REPORT_PATH = (
    REPORT_DIR
    / "AgroTwin_CRISP_DM_Report.pdf"
)


# =========================================================
# CONFIGURATION
# =========================================================

RANDOM_STATE = 42

MAX_SHAP_SAMPLES = 500

MAX_PERMUTATION_SAMPLES = 3000

TOP_FEATURES = 15


# =========================================================
# REPORT ITEM
# =========================================================

@dataclass
class ReportItem:
    key: str
    title: str
    kind: str

    interpretation: str
    explainability: str

    dataframe: pd.DataFrame | None = None
    figure: Any | None = None


# =========================================================
# LOAD HELPERS
# =========================================================

def read_json(
    path: Path,
) -> dict:

    if not path.exists():
        raise FileNotFoundError(
            f"Required artifact not found: {path}"
        )

    return json.loads(
        path.read_text(
            encoding="utf-8",
        )
    )


def read_csv(
    path: Path,
) -> pd.DataFrame:

    if not path.exists():
        raise FileNotFoundError(
            f"Required artifact not found: {path}"
        )

    return pd.read_csv(
        path
    )


# =========================================================
# LOAD CRISP-DM RESULTS
# =========================================================

def load_crisp_dm_artifacts() -> dict:

    required = [
        MODEL_SELECTION_RESULTS_PATH,
        CV_METRICS_PATH,
        PAIRWISE_TESTS_PATH,
        FINAL_TEST_METRICS_PATH,
        FINAL_TEST_PREDICTIONS_PATH,
        FRIEDMAN_PATH,
        BOOTSTRAP_PATH,
        RESIDUAL_DIAGNOSTICS_PATH,
        EVALUATION_SUMMARY_PATH,
        FINAL_SELECTED_MODEL_PATH,
    ]


    missing = [
        path
        for path in required
        if not path.exists()
    ]


    if missing:
        raise FileNotFoundError(
            "CRISP-DM artifacts are missing. "
            "Run `python -m ml.train` and "
            "`python -m ml.evaluate` first.\n"
            +
            "\n".join(
                str(path)
                for path in missing
            )
        )


    return {
        "model_selection":
            read_csv(
                MODEL_SELECTION_RESULTS_PATH
            ),

        "selection_metadata":
            read_json(
                MODEL_SELECTION_METADATA_PATH
            ),

        "cv_metrics":
            read_csv(
                CV_METRICS_PATH
            ),

        "pairwise_tests":
            read_csv(
                PAIRWISE_TESTS_PATH
            ),

        "final_metrics":
            read_csv(
                FINAL_TEST_METRICS_PATH
            ),

        "final_predictions":
            read_csv(
                FINAL_TEST_PREDICTIONS_PATH
            ),

        "friedman":
            read_json(
                FRIEDMAN_PATH
            ),

        "bootstrap":
            read_json(
                BOOTSTRAP_PATH
            ),

        "residuals":
            read_json(
                RESIDUAL_DIAGNOSTICS_PATH
            ),

        "evaluation":
            read_json(
                EVALUATION_SUMMARY_PATH
            ),

        "model_bundle":
            joblib.load(
                FINAL_SELECTED_MODEL_PATH
            ),
    }


# =========================================================
# FIGURE TO BASE64
# =========================================================

def figure_to_png_bytes(
    figure,
) -> bytes:

    buffer = io.BytesIO()

    figure.savefig(
        buffer,
        format="png",
        dpi=160,
        bbox_inches="tight",
    )

    buffer.seek(0)

    return buffer.read()


def figure_to_base64(
    figure,
) -> str:

    encoded = base64.b64encode(
        figure_to_png_bytes(
            figure
        )
    ).decode(
        "ascii"
    )

    return encoded


# =========================================================
# SAVE FIGURE
# =========================================================

def save_figure(
    figure,
    filename: str,
) -> Path:

    ASSET_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )


    path = (
        ASSET_DIR
        / filename
    )


    figure.savefig(
        path,
        dpi=160,
        bbox_inches="tight",
    )


    return path


# =========================================================
# EDA · TEMPORAL COVERAGE
# =========================================================

def figure_temporal_coverage(
    dataframe: pd.DataFrame,
) -> ReportItem:

    package = (
        build_eda_package(
            dataframe
        )
    )


    coverage = (
        package[
            "temporal_coverage"
        ]
    )


    figure, axis = plt.subplots(
        figsize=(8, 4.5)
    )


    axis.bar(
        coverage[
            "year"
        ].astype(str),
        coverage[
            "coverage_percent"
        ],
    )


    axis.set_title(
        "Cobertura temporal del dataset NOAA USCRN"
    )

    axis.set_xlabel(
        "Año"
    )

    axis.set_ylabel(
        "Cobertura (%)"
    )

    axis.set_ylim(
        98,
        100.1,
    )


    axis.grid(
        axis="y",
        alpha=0.25,
    )


    return ReportItem(
        key="temporal_coverage",

        title=(
            "Figura · Cobertura temporal "
            "del dataset"
        ),

        kind="figure",

        figure=figure,

        interpretation=(
            "La cobertura anual supera el 99 % en los "
            "cuatro años analizados. Esto indica que la "
            "serie es prácticamente continua y adecuada "
            "para una evaluación temporal. Las pequeñas "
            "interrupciones existentes deben conservarse "
            "como parte de la realidad del dataset y no "
            "rellenarse de forma arbitraria."
        ),

        explainability=(
            "La figura se obtiene contando timestamps "
            "horarios únicos por año y comparándolos con "
            "el número teórico de horas del año. No es "
            "una salida del modelo; explica la integridad "
            "temporal de los datos que posteriormente "
            "alimentan el entrenamiento."
        ),
    )


# =========================================================
# EDA · TARGET DISTRIBUTION
# =========================================================

def figure_target_distribution(
    dataframe: pd.DataFrame,
) -> ReportItem:

    target = (
        dataframe[
            DELTA_TARGET
        ]
        .dropna()
        .astype(float)
    )


    figure, axis = plt.subplots(
        figsize=(8, 4.5)
    )


    axis.hist(
        target,
        bins=80,
    )


    axis.axvline(
        0,
        linestyle="--",
        linewidth=1.2,
    )


    axis.set_title(
        "Distribución del cambio de humedad a +24 h"
    )

    axis.set_xlabel(
        "Δ humedad del suelo a 24 h"
    )

    axis.set_ylabel(
        "Frecuencia"
    )


    axis.grid(
        axis="y",
        alpha=0.2,
    )


    return ReportItem(
        key="target_distribution",

        title=(
            "Figura · Distribución de la "
            "variable objetivo"
        ),

        kind="figure",

        figure=figure,

        interpretation=(
            "La variable objetivo se concentra alrededor "
            "de cero, con episodios menos frecuentes de "
            "cambios positivos o negativos de mayor "
            "magnitud. Esto explica por qué un benchmark "
            "de persistencia puede resultar competitivo: "
            "durante muchas horas la humedad cambia poco."
        ),

        explainability=(
            "El objetivo corresponde a "
            "soil_moisture(t+24 h) - soil_moisture(t). "
            "Los modelos aprenden este cambio y después "
            "la humedad absoluta futura se reconstruye "
            "sumándolo a la humedad actual."
        ),
    )


# =========================================================
# EDA · CORRELATIONS
# =========================================================

def figure_target_correlations(
    dataframe: pd.DataFrame,
) -> ReportItem:

    package = (
        build_eda_package(
            dataframe
        )
    )


    correlations = (
        package[
            "target_correlations"
        ]
        .head(
            TOP_FEATURES
        )
        .sort_values(
            "absolute_correlation"
        )
    )


    figure, axis = plt.subplots(
        figsize=(8, 6)
    )


    axis.barh(
        correlations[
            "feature"
        ],
        correlations[
            "correlation"
        ],
    )


    axis.axvline(
        0,
        linewidth=1,
    )


    axis.set_title(
        "Correlación lineal con el objetivo +24 h"
    )

    axis.set_xlabel(
        "Correlación de Pearson"
    )


    return ReportItem(
        key="target_correlations",

        title=(
            "Figura · Correlaciones con "
            "la variable objetivo"
        ),

        kind="figure",

        figure=figure,

        interpretation=(
            "Las correlaciones lineales individuales son "
            "moderadas o bajas. Esto sugiere que la "
            "predicción no depende de una única variable "
            "linealmente dominante y justifica evaluar "
            "modelos capaces de capturar relaciones "
            "multivariadas y no lineales."
        ),

        explainability=(
            "La correlación describe asociación lineal "
            "entre cada predictor y el cambio de humedad. "
            "No representa importancia causal ni sustituye "
            "la explicabilidad del modelo. Más adelante "
            "Permutation Importance y SHAP analizan la "
            "contribución predictiva real."
        ),
    )


# =========================================================
# MODEL SELECTION TABLE
# =========================================================

def table_model_selection(
    artifacts: dict,
) -> ReportItem:

    results = (
        artifacts[
            "model_selection"
        ]
        .copy()
    )


    columns = [
        "model_name",
        "mae",
        "rmse",
        "r2",
        "bias",
        "mae_improvement_vs_persistence_percent",
        "rmse_improvement_vs_persistence_percent",
    ]


    results = results[
        columns
    ]


    selected_model = (
        artifacts[
            "selection_metadata"
        ][
            "selected_model"
        ]
    )


    return ReportItem(
        key="model_selection_table",

        title=(
            "Tabla · Comparación de modelos "
            "en validación 2024"
        ),

        kind="table",

        dataframe=results,

        interpretation=(
            f"{selected_model} fue seleccionado entre los "
            "modelos ML utilizando MAE como criterio "
            "principal y RMSE como criterio secundario. "
            "La selección se realizó exclusivamente con "
            "la validación temporal de 2024; el año 2025 "
            "permaneció aislado."
        ),

        explainability=(
            "MAE mide el error absoluto promedio; RMSE "
            "penaliza más los errores grandes; R² cuantifica "
            "la proporción de variabilidad explicada. "
            "La tabla debe interpretarse conjuntamente y "
            "no usando una única métrica de forma aislada."
        ),
    )


# =========================================================
# MODEL SELECTION FIGURE
# =========================================================

def figure_model_selection(
    artifacts: dict,
) -> ReportItem:

    results = (
        artifacts[
            "model_selection"
        ]
        .copy()
    )


    figure, axis = plt.subplots(
        figsize=(9, 5)
    )


    positions = np.arange(
        len(
            results
        )
    )


    width = 0.36


    axis.bar(
        positions - width / 2,
        results[
            "mae"
        ],
        width=width,
        label="MAE",
    )


    axis.bar(
        positions + width / 2,
        results[
            "rmse"
        ],
        width=width,
        label="RMSE",
    )


    axis.set_xticks(
        positions
    )


    axis.set_xticklabels(
        results[
            "model_name"
        ],
        rotation=20,
        ha="right",
    )


    axis.set_ylabel(
        "Error"
    )


    axis.set_title(
        "Comparación de modelos · Validación 2024"
    )


    axis.legend()


    axis.grid(
        axis="y",
        alpha=0.2,
    )


    return ReportItem(
        key="model_selection_figure",

        title=(
            "Figura · MAE y RMSE de modelos "
            "candidatos"
        ),

        kind="figure",

        figure=figure,

        interpretation=(
            "La comparación visual confirma que los "
            "modelos candidatos presentan comportamientos "
            "distintos según MAE y RMSE. La selección no "
            "debe reducirse únicamente a la apariencia del "
            "gráfico, sino que debe complementarse con "
            "validación cruzada y pruebas estadísticas."
        ),

        explainability=(
            "Todos los modelos utilizan las mismas 25 "
            "variables de entrada, el mismo target de "
            "cambio a +24 h y la misma partición temporal. "
            "Por ello, las diferencias observadas se "
            "atribuyen al comportamiento del algoritmo "
            "bajo una comparación controlada."
        ),
    )


# =========================================================
# CROSS VALIDATION TABLE
# =========================================================

def build_cv_summary(
    artifacts: dict,
) -> pd.DataFrame:

    metrics = (
        artifacts[
            "cv_metrics"
        ]
    )


    summary = (
        metrics
        .groupby(
            "model_name",
            as_index=False,
        )
        .agg(
            mae_mean=(
                "mae",
                "mean",
            ),
            mae_std=(
                "mae",
                "std",
            ),
            rmse_mean=(
                "rmse",
                "mean",
            ),
            rmse_std=(
                "rmse",
                "std",
            ),
            r2_mean=(
                "r2",
                "mean",
            ),
            r2_std=(
                "r2",
                "std",
            ),
        )
    )


    return (
        summary
        .sort_values(
            "mae_mean"
        )
        .reset_index(
            drop=True
        )
    )


def table_cross_validation(
    artifacts: dict,
) -> ReportItem:

    summary = (
        build_cv_summary(
            artifacts
        )
    )


    return ReportItem(
        key="cv_table",

        title=(
            "Tabla · Validación cruzada temporal"
        ),

        kind="table",

        dataframe=summary,

        interpretation=(
            "La validación cruzada temporal muestra la "
            "estabilidad de los modelos a través de varios "
            "segmentos cronológicos. Persistencia presenta "
            "un MAE medio ligeramente menor que Extra Trees, "
            "mientras que Extra Trees presenta un RMSE medio "
            "ligeramente inferior."
        ),

        explainability=(
            "Los folds utilizan ventanas temporales "
            "expansivas y un gap de 24 filas entre "
            "entrenamiento y validación. Esto reduce el "
            "riesgo de contaminación asociado con el "
            "horizonte predictivo de +24 h."
        ),
    )


# =========================================================
# CV FIGURE
# =========================================================

def figure_cross_validation(
    artifacts: dict,
) -> ReportItem:

    metrics = (
        artifacts[
            "cv_metrics"
        ]
        .copy()
    )


    figure, axis = plt.subplots(
        figsize=(9, 5)
    )


    for model_name, group in (
        metrics.groupby(
            "model_name"
        )
    ):

        group = group.sort_values(
            "fold"
        )


        axis.plot(
            group[
                "fold"
            ],
            group[
                "mae"
            ],
            marker="o",
            label=model_name,
        )


    axis.set_title(
        "MAE por fold temporal"
    )


    axis.set_xlabel(
        "Fold"
    )


    axis.set_ylabel(
        "MAE"
    )


    axis.legend(
        fontsize=8
    )


    axis.grid(
        alpha=0.25,
    )


    return ReportItem(
        key="cv_figure",

        title=(
            "Figura · Error por fold temporal"
        ),

        kind="figure",

        figure=figure,

        interpretation=(
            "El rendimiento cambia entre períodos, lo que "
            "confirma que la dificultad del pronóstico de "
            "humedad no es constante en el tiempo. Por "
            "ello es más apropiado evaluar múltiples "
            "ventanas temporales que depender de una "
            "división aleatoria convencional."
        ),

        explainability=(
            "Cada punto representa el MAE obtenido después "
            "de entrenar únicamente con observaciones "
            "anteriores al bloque evaluado. Ningún fold "
            "utiliza información futura para entrenar."
        ),
    )


# =========================================================
# STATISTICAL TESTS
# =========================================================

def table_statistical_tests(
    artifacts: dict,
) -> ReportItem:

    pairwise = (
        artifacts[
            "pairwise_tests"
        ]
        .copy()
    )


    columns = [
        "selected_model",
        "comparator",
        "selected_daily_mae",
        "comparator_daily_mae",
        "selected_daily_win_rate_percent",
        "wilcoxon_p_holm",
        "dm_p_holm",
        "wilcoxon_significant_005",
        "dm_significant_005",
    ]


    pairwise = pairwise[
        columns
    ]


    friedman = (
        artifacts[
            "friedman"
        ]
    )


    return ReportItem(
        key="statistical_tests",

        title=(
            "Tabla · Pruebas estadísticas rigurosas"
        ),

        kind="table",

        dataframe=pairwise,

        interpretation=(
            "El test de Friedman detectó diferencias "
            "globales entre los métodos "
            f"(p={friedman['p_value']:.3e}). "
            "Sin embargo, las comparaciones pareadas "
            "muestran que la evidencia de superioridad "
            "depende del comparador y del test utilizado."
        ),

        explainability=(
            "Wilcoxon utiliza errores medios diarios para "
            "reducir la falsa independencia entre horas. "
            "La corrección Holm controla el error por "
            "comparaciones múltiples. Diebold-Mariano "
            "contrasta diferencias de pérdida predictiva "
            "con corrección HAC/Newey-West para dependencia "
            "serial."
        ),
    )


# =========================================================
# FINAL HOLDOUT TABLE
# =========================================================

def table_final_holdout(
    artifacts: dict,
) -> ReportItem:

    metrics = (
        artifacts[
            "final_metrics"
        ]
        .copy()
    )


    selected_name = (
        metrics.iloc[0][
            "model_name"
        ]
    )


    return ReportItem(
        key="final_holdout_table",

        title=(
            "Tabla · Prueba final no observada 2025"
        ),

        kind="table",

        dataframe=metrics,

        interpretation=(
            f"En el holdout 2025, {selected_name} obtiene "
            "menor MAE y RMSE y mayor R² que persistencia. "
            "Este resultado es especialmente relevante "
            "porque 2025 no participó en el entrenamiento, "
            "ajuste ni selección del candidato."
        ),

        explainability=(
            "La prueba final mide generalización temporal "
            "en observaciones completamente posteriores "
            "al proceso de selección. Las métricas no "
            "modifican el motor de decisión de AgroTwin; "
            "evalúan únicamente el predictor complementario."
        ),
    )


# =========================================================
# OBSERVED VS PREDICTED
# =========================================================

def figure_final_timeseries(
    artifacts: dict,
) -> ReportItem:

    predictions = (
        artifacts[
            "final_predictions"
        ]
        .copy()
    )


    predictions[
        "timestamp"
    ] = pd.to_datetime(
        predictions[
            "timestamp"
        ],
        utc=True,
    )


    daily = (
        predictions
        .set_index(
            "timestamp"
        )[
            [
                "observed",
                "selected_prediction",
                "persistence_prediction",
            ]
        ]
        .resample(
            "D"
        )
        .mean()
    )


    figure, axis = plt.subplots(
        figsize=(11, 5)
    )


    axis.plot(
        daily.index,
        daily[
            "observed"
        ],
        label="Observado",
        linewidth=1.4,
    )


    axis.plot(
        daily.index,
        daily[
            "selected_prediction"
        ],
        label="Modelo seleccionado",
        linewidth=1.1,
    )


    axis.plot(
        daily.index,
        daily[
            "persistence_prediction"
        ],
        label="Persistencia",
        linewidth=1,
        alpha=0.8,
    )


    axis.set_title(
        "Humedad observada y predicha · 2025"
    )


    axis.set_ylabel(
        "Humedad del suelo"
    )


    axis.legend()


    axis.grid(
        alpha=0.2,
    )


    return ReportItem(
        key="final_timeseries",

        title=(
            "Figura · Observado vs predicho "
            "en el holdout 2025"
        ),

        kind="figure",

        figure=figure,

        interpretation=(
            "La serie agregada diariamente permite observar "
            "si el modelo reproduce la dinámica general de "
            "humedad durante 2025. El modelo seleccionado "
            "sigue gran parte de la trayectoria observada, "
            "aunque existen episodios donde la magnitud del "
            "error aumenta."
        ),

        explainability=(
            "Para mejorar la legibilidad se representa el "
            "promedio diario, pero las métricas finales se "
            "calculan sobre las observaciones horarias. "
            "El modelo predice Δ humedad a 24 horas y luego "
            "reconstruye la humedad absoluta futura."
        ),
    )


# =========================================================
# RESIDUAL FIGURE
# =========================================================

def figure_residuals(
    artifacts: dict,
) -> ReportItem:

    predictions = (
        artifacts[
            "final_predictions"
        ]
    )


    residuals = (
        predictions[
            "selected_residual"
        ]
        .dropna()
    )


    diagnostics = (
        artifacts[
            "residuals"
        ]
    )


    figure, axis = plt.subplots(
        figsize=(8, 4.5)
    )


    axis.hist(
        residuals,
        bins=80,
    )


    axis.axvline(
        0,
        linestyle="--",
        linewidth=1.2,
    )


    axis.set_title(
        "Distribución de residuos · Holdout 2025"
    )


    axis.set_xlabel(
        "Predicción - Observación"
    )


    axis.set_ylabel(
        "Frecuencia"
    )


    return ReportItem(
        key="residuals",

        title=(
            "Figura · Distribución de residuos"
        ),

        kind="figure",

        figure=figure,

        interpretation=(
            "Los residuos presentan fuerte asimetría y "
            "colas pesadas. La prueba de normalidad rechaza "
            "normalidad y la autocorrelación de primer orden "
            f"es {diagnostics['lag1_autocorrelation']:.3f}. "
            "Por tanto, no es apropiado asumir errores "
            "independientes y gaussianos."
        ),

        explainability=(
            "El residuo se calcula como predicción menos "
            "observación. La fuerte autocorrelación temporal "
            "es la razón por la que la evaluación utiliza "
            "bloques diarios, bootstrap por bloques y "
            "Diebold-Mariano con varianza HAC."
        ),
    )


# =========================================================
# BOOTSTRAP FIGURE
# =========================================================

def figure_bootstrap(
    artifacts: dict,
) -> ReportItem:

    bootstrap = (
        artifacts[
            "bootstrap"
        ]
    )


    mae = (
        bootstrap[
            "mae_difference_selected_minus_persistence"
        ]
    )


    rmse = (
        bootstrap[
            "rmse_difference_selected_minus_persistence"
        ]
    )


    means = [
        mae[
            "mean"
        ],
        rmse[
            "mean"
        ],
    ]


    lowers = [
        mae[
            "mean"
        ]
        -
        mae[
            "lower"
        ],

        rmse[
            "mean"
        ]
        -
        rmse[
            "lower"
        ],
    ]


    uppers = [
        mae[
            "upper"
        ]
        -
        mae[
            "mean"
        ],

        rmse[
            "upper"
        ]
        -
        rmse[
            "mean"
        ],
    ]


    figure, axis = plt.subplots(
        figsize=(7, 4.5)
    )


    axis.errorbar(
        [
            "MAE",
            "RMSE",
        ],
        means,
        yerr=[
            lowers,
            uppers,
        ],
        fmt="o",
        capsize=5,
    )


    axis.axhline(
        0,
        linestyle="--",
        linewidth=1,
    )


    axis.set_title(
        "IC 95 % · Modelo seleccionado - Persistencia"
    )


    axis.set_ylabel(
        "Diferencia de error"
    )


    return ReportItem(
        key="bootstrap",

        title=(
            "Figura · Intervalos bootstrap del "
            "beneficio predictivo"
        ),

        kind="figure",

        figure=figure,

        interpretation=(
            "El intervalo bootstrap del MAE cruza cero, "
            "por lo que la mejora media absoluta no es "
            "concluyente. El intervalo del RMSE permanece "
            "completamente por debajo de cero, lo que "
            "indica una reducción consistente de errores "
            "de mayor magnitud en el holdout 2025."
        ),

        explainability=(
            "Los intervalos se obtienen mediante 2000 "
            "remuestreos por bloques diarios. Valores "
            "negativos significan menor error del modelo "
            "seleccionado frente a persistencia."
        ),
    )


# =========================================================
# XAI · LOAD MODEL
# =========================================================

def get_final_model_components(
    artifacts: dict,
):

    bundle = (
        artifacts[
            "model_bundle"
        ]
    )


    pipeline = (
        bundle[
            "pipeline"
        ]
    )


    model = (
        pipeline.named_steps[
            "model"
        ]
    )


    return (
        bundle,
        pipeline,
        model,
    )


# =========================================================
# XAI · PERMUTATION IMPORTANCE
# =========================================================

def calculate_permutation_importance(
    dataframe: pd.DataFrame,
    artifacts: dict,
) -> pd.DataFrame:

    final_test = (
        final_holdout_dataset(
            dataframe
        )
    )


    if (
        len(
            final_test
        )
        >
        MAX_PERMUTATION_SAMPLES
    ):

        sample = (
            final_test
            .sample(
                n=
                    MAX_PERMUTATION_SAMPLES,

                random_state=
                    RANDOM_STATE,
            )
            .sort_values(
                TIMESTAMP_COLUMN
            )
        )

    else:

        sample = (
            final_test
        )


    (
        _,
        pipeline,
        _,
    ) = get_final_model_components(
        artifacts
    )


    X = (
        sample[
            FEATURES
        ]
    )


    y = (
        sample[
            DELTA_TARGET
        ]
    )


    result = (
        permutation_importance(
            pipeline,
            X,
            y,
            scoring=
                "neg_mean_absolute_error",
            n_repeats=
                10,
            random_state=
                RANDOM_STATE,
            n_jobs=
                -1,
        )
    )


    table = pd.DataFrame(
        {
            "feature":
                FEATURES,

            "importance_mean":
                result.importances_mean,

            "importance_std":
                result.importances_std,
        }
    )


    return (
        table
        .sort_values(
            "importance_mean",
            ascending=False,
        )
        .reset_index(
            drop=True
        )
    )


def figure_permutation_importance(
    permutation_table: pd.DataFrame,
) -> ReportItem:

    top = (
        permutation_table
        .head(
            TOP_FEATURES
        )
        .sort_values(
            "importance_mean"
        )
    )


    figure, axis = plt.subplots(
        figsize=(8, 6)
    )


    axis.barh(
        top[
            "feature"
        ],
        top[
            "importance_mean"
        ],
        xerr=
            top[
                "importance_std"
            ],
    )


    axis.set_title(
        "Permutation Importance · Holdout 2025"
    )


    axis.set_xlabel(
        "Incremento de error al permutar la variable"
    )


    return ReportItem(
        key="permutation_importance",

        title=(
            "Figura · Importancia por permutación"
        ),

        kind="figure",

        figure=figure,

        interpretation=(
            "Las variables situadas en la parte superior "
            "son aquellas cuya alteración deteriora más el "
            "desempeño predictivo del modelo. Esto permite "
            "identificar qué información histórica o "
            "meteorológica resulta más relevante para la "
            "predicción a +24 horas."
        ),

        explainability=(
            "Permutation Importance mide la caída de "
            "rendimiento cuando una variable se desordena "
            "mientras las demás permanecen intactas. "
            "A diferencia de la importancia interna de "
            "árboles, es una medida independiente de la "
            "forma en que el algoritmo construye sus nodos."
        ),
    )


# =========================================================
# XAI · SHAP
# =========================================================

def calculate_shap_explanations(
    dataframe: pd.DataFrame,
    artifacts: dict,
) -> dict:

    final_test = (
        final_holdout_dataset(
            dataframe
        )
    )


    if (
        len(
            final_test
        )
        >
        MAX_SHAP_SAMPLES
    ):

        sample = (
            final_test
            .sample(
                n=
                    MAX_SHAP_SAMPLES,

                random_state=
                    RANDOM_STATE,
            )
            .sort_values(
                TIMESTAMP_COLUMN
            )
        )

    else:

        sample = (
            final_test
        )


    (
        bundle,
        pipeline,
        model,
    ) = get_final_model_components(
        artifacts
    )


    X_original = (
        sample[
            FEATURES
        ]
        .copy()
    )


    if (
        "imputer"
        in pipeline.named_steps
    ):

        transformed = (
            pipeline.named_steps[
                "imputer"
            ]
            .transform(
                X_original
            )
        )

    else:

        transformed = (
            X_original
            .to_numpy(
                dtype=float
            )
        )


    explainer = (
        shap.TreeExplainer(
            model
        )
    )


    shap_values = (
        explainer.shap_values(
            transformed
        )
    )


    values = np.asarray(
        shap_values
    )


    if (
        values.ndim
        !=
        2
    ):

        values = (
            values.reshape(
                len(
                    X_original
                ),
                -1,
            )
        )


    global_importance = pd.DataFrame(
        {
            "feature":
                FEATURES,

            "mean_abs_shap":
                np.mean(
                    np.abs(
                        values
                    ),
                    axis=0,
                ),
        }
    )


    global_importance = (
        global_importance
        .sort_values(
            "mean_abs_shap",
            ascending=False,
        )
        .reset_index(
            drop=True
        )
    )


    # -----------------------------------------------------
    # LOCAL EXPLANATION
    #
    # Use the most recent sampled observation.
    # -----------------------------------------------------

    local_position = (
        len(
            X_original
        )
        -
        1
    )


    local_shap = (
        values[
            local_position
        ]
    )


    local_input = (
        transformed[
            local_position
        ]
    )


    local_table = pd.DataFrame(
        {
            "feature":
                FEATURES,

            "input_value":
                local_input,

            "shap_value":
                local_shap,

            "absolute_shap":
                np.abs(
                    local_shap
                ),

            "direction":
                np.where(
                    local_shap
                    >
                    0,
                    "INCREASE_DELTA",

                    np.where(
                        local_shap
                        <
                        0,
                        "DECREASE_DELTA",
                        "NEUTRAL",
                    ),
                ),
        }
    )


    local_table = (
        local_table
        .sort_values(
            "absolute_shap",
            ascending=False,
        )
        .reset_index(
            drop=True
        )
    )


    local_timestamp = (
        X_original
        .index[
            local_position
        ]
    )


    selected_row = (
        sample.iloc[
            local_position
        ]
    )


    return {
        "global":
            global_importance,

        "local":
            local_table,

        "local_timestamp":
            str(
                selected_row[
                    TIMESTAMP_COLUMN
                ]
            ),

        "explained_output":
            (
                "soil_moisture_change_24h"
            ),

        "model_name":
            bundle[
                "model_name"
            ],
    }


def figure_shap_global(
    shap_result: dict,
) -> ReportItem:

    top = (
        shap_result[
            "global"
        ]
        .head(
            TOP_FEATURES
        )
        .sort_values(
            "mean_abs_shap"
        )
    )


    figure, axis = plt.subplots(
        figsize=(8, 6)
    )


    axis.barh(
        top[
            "feature"
        ],
        top[
            "mean_abs_shap"
        ],
    )


    axis.set_title(
        "SHAP global · Importancia media absoluta"
    )


    axis.set_xlabel(
        "|SHAP| medio"
    )


    return ReportItem(
        key="shap_global",

        title=(
            "Figura · Explicabilidad global SHAP"
        ),

        kind="figure",

        figure=figure,

        interpretation=(
            "El gráfico muestra qué variables tienen mayor "
            "contribución promedio a las predicciones del "
            "modelo seleccionado. Una mayor magnitud SHAP "
            "indica mayor influencia sobre el cambio de "
            "humedad predicho."
        ),

        explainability=(
            "Los valores SHAP descomponen la predicción "
            "del cambio de humedad a +24 horas en "
            "contribuciones atribuibles a cada variable. "
            "El gráfico utiliza el valor absoluto medio, "
            "por lo que mide magnitud de influencia y no "
            "dirección causal."
        ),
    )


def table_shap_local(
    shap_result: dict,
) -> ReportItem:

    local = (
        shap_result[
            "local"
        ]
        .head(
            12
        )
        .copy()
    )


    return ReportItem(
        key="shap_local",

        title=(
            "Tabla · Explicación SHAP de "
            "una predicción individual"
        ),

        kind="table",

        dataframe=local,

        interpretation=(
            "La tabla identifica las variables que más "
            "influyeron en una predicción individual del "
            "holdout. Valores SHAP positivos desplazan el "
            "cambio de humedad hacia valores mayores; "
            "valores negativos lo desplazan hacia valores "
            "menores."
        ),

        explainability=(
            "Esta es una explicación local: describe una "
            "predicción concreta y no debe generalizarse "
            "automáticamente a todas las observaciones. "
            f"La salida explicada es "
            f"{shap_result['explained_output']}."
        ),
    )


# =========================================================
# DATA QUALITY TABLE
# =========================================================

def table_data_quality(
    dataframe: pd.DataFrame,
) -> ReportItem:

    package = (
        build_eda_package(
            dataframe
        )
    )


    quality = (
        package[
            "physical_checks"
        ]
    )


    return ReportItem(
        key="data_quality",

        title=(
            "Tabla · Control de calidad físico "
            "del dataset"
        ),

        kind="table",

        dataframe=quality,

        interpretation=(
            "Las comprobaciones físicas principales del "
            "dataset procesado no detectan humedad del "
            "suelo fuera del rango definido, humedad "
            "relativa fuera de 0–100 %, lluvia negativa "
            "ni radiación solar negativa."
        ),

        explainability=(
            "Estos controles no validan el modelo; validan "
            "la plausibilidad de las variables de entrada. "
            "Su objetivo es impedir que valores físicamente "
            "imposibles sean interpretados como patrones "
            "predictivos válidos."
        ),
    )


# =========================================================
# BUILD ALL REPORT ITEMS
# =========================================================

def build_report_items(
    dataframe: pd.DataFrame,
    artifacts: dict,
) -> list[ReportItem]:

    print(
        "[REPORT] Calculando Permutation Importance..."
    )


    permutation_table = (
        calculate_permutation_importance(
            dataframe,
            artifacts,
        )
    )


    print(
        "[REPORT] Calculando SHAP..."
    )


    shap_result = (
        calculate_shap_explanations(
            dataframe,
            artifacts,
        )
    )


    items = [
        table_data_quality(
            dataframe
        ),

        figure_temporal_coverage(
            dataframe
        ),

        figure_target_distribution(
            dataframe
        ),

        figure_target_correlations(
            dataframe
        ),

        table_model_selection(
            artifacts
        ),

        figure_model_selection(
            artifacts
        ),

        table_cross_validation(
            artifacts
        ),

        figure_cross_validation(
            artifacts
        ),

        table_statistical_tests(
            artifacts
        ),

        table_final_holdout(
            artifacts
        ),

        figure_final_timeseries(
            artifacts
        ),

        figure_residuals(
            artifacts
        ),

        figure_bootstrap(
            artifacts
        ),

        ReportItem(
            key="permutation_table",

            title=(
                "Tabla · Importancia por "
                "permutación"
            ),

            kind="table",

            dataframe=
                permutation_table.head(
                    TOP_FEATURES
                ),

            interpretation=(
                "La tabla cuantifica cuánto empeora el "
                "modelo al perturbar cada predictor. "
                "Las variables con mayor importancia "
                "positiva contienen mayor información "
                "predictiva para el target."
            ),

            explainability=(
                "La importancia se calcula en datos del "
                "holdout y utiliza pérdida MAE sobre el "
                "cambio de humedad. No representa una "
                "relación causal."
            ),
        ),

        figure_permutation_importance(
            permutation_table
        ),

        figure_shap_global(
            shap_result
        ),

        table_shap_local(
            shap_result
        ),
    ]


    return items


# =========================================================
# DATAFRAME TO HTML
# =========================================================

def dataframe_to_html(
    dataframe: pd.DataFrame,
) -> str:

    display = (
        dataframe.copy()
    )


    for column in display.columns:

        if pd.api.types.is_float_dtype(
            display[
                column
            ]
        ):

            display[
                column
            ] = (
                display[
                    column
                ]
                .map(
                    lambda value:
                        (
                            f"{value:.6f}"
                            if pd.notna(
                                value
                            )
                            else ""
                        )
                )
            )


    return display.to_html(
        index=False,
        border=0,
        classes="report-table",
    )


# =========================================================
# HTML REPORT
# =========================================================

def generate_html_report(
    items: list[ReportItem],
    artifacts: dict,
    output_path: Path = HTML_REPORT_PATH,
) -> Path:

    REPORT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )


    selected_model = (
        artifacts[
            "selection_metadata"
        ][
            "selected_model"
        ]
    )


    parts = []


    parts.append(
        """
<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="utf-8">
<title>AgroTwin · Reporte CRISP-DM</title>

<style>

body {
    font-family: Arial, Helvetica, sans-serif;
    max-width: 1200px;
    margin: 0 auto;
    padding: 36px;
    line-height: 1.5;
    color: #222;
}

h1, h2, h3 {
    margin-top: 1.4em;
}

.hero {
    padding: 24px;
    border: 1px solid #ccc;
    border-radius: 14px;
    margin-bottom: 30px;
}

.scope {
    padding: 14px;
    border-left: 5px solid #555;
    background: #f6f6f6;
    margin: 18px 0;
}

.item {
    margin-bottom: 40px;
    page-break-inside: avoid;
}

.figure {
    max-width: 100%;
    margin: 16px auto;
    display: block;
}

.report-table {
    border-collapse: collapse;
    width: 100%;
    font-size: 0.88rem;
    margin: 16px 0;
}

.report-table th,
.report-table td {
    border: 1px solid #ddd;
    padding: 7px;
    text-align: left;
}

.report-table th {
    background: #f2f2f2;
}

.interpretation,
.explainability {
    padding: 12px 14px;
    margin-top: 10px;
    border-radius: 6px;
}

.interpretation {
    background: #f2f7f2;
}

.explainability {
    background: #f3f5f8;
}

small {
    color: #666;
}

</style>
</head>

<body>
"""
    )


    parts.append(
        f"""
<div class="hero">

<h1>
AgroTwin · Reporte CRISP-DM
</h1>

<p>
Evaluación reproducible del módulo predictivo
complementario de humedad del suelo a +24 horas.
</p>

<p>
<strong>Modelo seleccionado:</strong>
{escape(str(selected_model))}
</p>

<p>
<strong>Dataset:</strong>
NOAA USCRN · AZ_Yuma_27_ENE · 2022–2025
</p>

</div>

<div class="scope">

<strong>Alcance arquitectónico.</strong>

Este reporte evalúa exclusivamente el módulo predictivo
complementario de humedad del suelo. El modelo no posee
autoridad decisional, no modifica TrustedState y no
modifica las recomendaciones generadas por el motor de
inferencia y decisión de AgroTwin.

</div>
"""
    )


    section_map = {
        "data_quality":
            "2. Comprensión de los datos",

        "model_selection_table":
            "4. Modelado y selección",

        "cv_table":
            "5. Validación cruzada",

        "statistical_tests":
            "6. Pruebas estadísticas",

        "final_holdout_table":
            "7. Prueba final 2025",

        "permutation_table":
            "8. Interpretabilidad y explicabilidad",
    }


    for item in items:

        if (
            item.key
            in section_map
        ):

            parts.append(
                f"<h2>{section_map[item.key]}</h2>"
            )


        parts.append(
            '<div class="item">'
        )


        parts.append(
            f"<h3>{escape(item.title)}</h3>"
        )


        if (
            item.kind
            ==
            "table"
            and
            item.dataframe
            is not None
        ):

            parts.append(
                dataframe_to_html(
                    item.dataframe
                )
            )


        elif (
            item.kind
            ==
            "figure"
            and
            item.figure
            is not None
        ):

            encoded = (
                figure_to_base64(
                    item.figure
                )
            )


            parts.append(
                (
                    '<img class="figure" '
                    f'src="data:image/png;base64,{encoded}">'
                )
            )


        parts.append(
            (
                '<div class="interpretation">'
                '<strong>Interpretación.</strong><br>'
                f'{escape(item.interpretation)}'
                '</div>'
            )
        )


        parts.append(
            (
                '<div class="explainability">'
                '<strong>Explicabilidad.</strong><br>'
                f'{escape(item.explainability)}'
                '</div>'
            )
        )


        parts.append(
            "</div>"
        )


    parts.append(
        """
<h2>9. Conclusión metodológica</h2>

<p>
El flujo implementado sigue CRISP-DM: comprensión del
problema, comprensión de los datos, preparación,
modelado, evaluación y generación de resultados
reproducibles. El conjunto 2025 permaneció fuera del
proceso de selección y fue utilizado únicamente como
holdout final.
</p>

<p>
La comparación estadística debe interpretarse con
prudencia debido a la dependencia temporal observada en
los residuos. Por esta razón se complementaron las
métricas convencionales con bloques diarios, bootstrap
por bloques y pruebas de pérdida predictiva con
corrección por autocorrelación.
</p>

</body>
</html>
"""
    )


    output_path.write_text(
        "\n".join(
            parts
        ),
        encoding="utf-8",
    )


    return output_path


# =========================================================
# PDF HELPERS
# =========================================================

def pdf_dataframe(
    dataframe: pd.DataFrame,
    styles,
) -> Table:

    display = (
        dataframe.copy()
    )


    if len(
        display.columns
    ) > 8:

        display = display.iloc[
            :,
            :8
        ]


    if len(
        display
    ) > 30:

        display = display.head(
            30
        )


    rows = [
        [
            Paragraph(
                f"<b>{escape(str(column))}</b>",
                styles[
                    "BodyText"
                ],
            )

            for column
            in display.columns
        ]
    ]


    for _, row in (
        display.iterrows()
    ):

        values = []


        for value in row:

            if isinstance(
                value,
                float,
            ):

                text = (
                    f"{value:.6f}"
                )

            else:

                text = (
                    str(
                        value
                    )
                )


            values.append(
                Paragraph(
                    escape(
                        text
                    ),
                    styles[
                        "BodyText"
                    ],
                )
            )


        rows.append(
            values
        )


    table = Table(
        rows,
        repeatRows=1,
    )


    table.setStyle(
        TableStyle(
            [
                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.4,
                    colors.grey,
                ),
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    colors.lightgrey,
                ),
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "TOP",
                ),
                (
                    "FONTSIZE",
                    (0, 0),
                    (-1, -1),
                    6.5,
                ),
            ]
        )
    )


    return table


# =========================================================
# PDF REPORT
# =========================================================

def generate_pdf_report(
    items: list[ReportItem],
    artifacts: dict,
    output_path: Path = PDF_REPORT_PATH,
) -> Path:

    if not REPORTLAB_AVAILABLE:

        raise RuntimeError(
            "reportlab is not installed. "
            "Install it with: pip install reportlab"
        )


    REPORT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )


    ASSET_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )


    document = SimpleDocTemplate(
        str(
            output_path
        ),
        pagesize=A4,
        rightMargin=1.5 * cm,
        leftMargin=1.5 * cm,
        topMargin=1.4 * cm,
        bottomMargin=1.4 * cm,
    )


    styles = (
        getSampleStyleSheet()
    )


    styles.add(
        ParagraphStyle(
            name="ReportTitle",
            parent=styles[
                "Title"
            ],
            alignment=TA_CENTER,
            fontSize=19,
            leading=23,
            spaceAfter=14,
        )
    )


    styles.add(
        ParagraphStyle(
            name="Interpretation",
            parent=styles[
                "BodyText"
            ],
            leading=12,
            spaceBefore=7,
            spaceAfter=5,
        )
    )


    selected_model = (
        artifacts[
            "selection_metadata"
        ][
            "selected_model"
        ]
    )


    story = [
        Paragraph(
            (
                "AgroTwin · Reporte CRISP-DM"
            ),
            styles[
                "ReportTitle"
            ],
        ),

        Paragraph(
            (
                "Módulo predictivo complementario "
                "de humedad del suelo a +24 horas"
            ),
            styles[
                "Heading2"
            ],
        ),

        Spacer(
            1,
            8,
        ),

        Paragraph(
            (
                "<b>Dataset:</b> "
                "NOAA USCRN · AZ_Yuma_27_ENE · "
                "2022–2025"
            ),
            styles[
                "BodyText"
            ],
        ),

        Paragraph(
            (
                "<b>Modelo seleccionado:</b> "
                f"{escape(str(selected_model))}"
            ),
            styles[
                "BodyText"
            ],
        ),

        Spacer(
            1,
            10,
        ),

        Paragraph(
            (
                "<b>Alcance:</b> este reporte evalúa "
                "exclusivamente el módulo predictivo "
                "complementario. El modelo no posee "
                "autoridad decisional, no modifica "
                "TrustedState y no modifica las "
                "recomendaciones del motor de AgroTwin."
            ),
            styles[
                "BodyText"
            ],
        ),

        PageBreak(),
    ]


    for item in items:

        story.append(
            Paragraph(
                escape(
                    item.title
                ),
                styles[
                    "Heading2"
                ],
            )
        )


        if (
            item.kind
            ==
            "table"
            and
            item.dataframe
            is not None
        ):

            story.append(
                pdf_dataframe(
                    item.dataframe,
                    styles,
                )
            )


        elif (
            item.kind
            ==
            "figure"
            and
            item.figure
            is not None
        ):

            image_path = (
                save_figure(
                    item.figure,
                    f"{item.key}.png",
                )
            )


            story.append(
                Image(
                    str(
                        image_path
                    ),
                    width=17 * cm,
                    height=9.5 * cm,
                    kind="proportional",
                )
            )


        story.append(
            Paragraph(
                (
                    "<b>Interpretación.</b> "
                    +
                    escape(
                        item.interpretation
                    )
                ),
                styles[
                    "Interpretation"
                ],
            )
        )


        story.append(
            Paragraph(
                (
                    "<b>Explicabilidad.</b> "
                    +
                    escape(
                        item.explainability
                    )
                ),
                styles[
                    "Interpretation"
                ],
            )
        )


        story.append(
            Spacer(
                1,
                15,
            )
        )


    document.build(
        story
    )


    return output_path


# =========================================================
# BUILD COMPLETE REPORTING PACKAGE
# =========================================================

def build_reporting_package() -> dict:

    dataframe = (
        load_training_dataset()
    )


    artifacts = (
        load_crisp_dm_artifacts()
    )


    items = (
        build_report_items(
            dataframe=
                dataframe,

            artifacts=
                artifacts,
        )
    )


    return {
        "dataframe":
            dataframe,

        "artifacts":
            artifacts,

        "items":
            items,
    }


# =========================================================
# CLOSE FIGURES
# =========================================================

def close_report_figures(
    items: list[ReportItem],
) -> None:

    for item in items:

        if (
            item.figure
            is not None
        ):

            plt.close(
                item.figure
            )


# =========================================================
# MAIN
# =========================================================

def main() -> None:

    print()
    print(
        "=" * 96
    )

    print(
        "AGROTWIN · CRISP-DM REPORTING"
    )

    print(
        "=" * 96
    )


    package = (
        build_reporting_package()
    )


    items = (
        package[
            "items"
        ]
    )


    artifacts = (
        package[
            "artifacts"
        ]
    )


    print()
    print(
        f"Report items generated: "
        f"{len(items)}"
    )


    print()
    print(
        "GENERATING HTML REPORT"
    )

    print(
        "-" * 96
    )


    html_path = (
        generate_html_report(
            items=
                items,

            artifacts=
                artifacts,
        )
    )


    print(
        html_path
    )


    print()
    print(
        "GENERATING PDF REPORT"
    )

    print(
        "-" * 96
    )


    if REPORTLAB_AVAILABLE:

        pdf_path = (
            generate_pdf_report(
                items=
                    items,

                artifacts=
                    artifacts,
            )
        )


        print(
            pdf_path
        )

    else:

        print(
            "PDF skipped: reportlab is not installed."
        )


    print()
    print(
        "REPORT CONTENT"
    )

    print(
        "-" * 96
    )


    for item in items:

        print(
            f"[{item.kind.upper()}] "
            f"{item.title}"
        )


    print()
    print(
        "ARCHITECTURE NOTE"
    )

    print(
        "-" * 96
    )


    print(
        "The CRISP-DM reports concern only the "
        "complementary soil-moisture prediction module."
    )


    print(
        "They do not replace or evaluate AgroTwin's "
        "inference and decision engine."
    )


    close_report_figures(
        items
    )


    print()
    print(
        "=" * 96
    )

    print(
        "CRISP-DM REPORTING COMPLETE"
    )

    print(
        "=" * 96
    )


if __name__ == "__main__":
    main()