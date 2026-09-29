import sys
from pathlib import Path

import pandas as pd


# =========================================================
# 1. AGREGAR RAÍZ DEL PROYECTO
# =========================================================

ROOT_DIR = (
    Path(__file__)
    .resolve()
    .parent
    .parent
)

if str(ROOT_DIR) not in sys.path:
    sys.path.insert(
        0,
        str(ROOT_DIR),
    )


# =========================================================
# 2. IMPORTS DEL PROYECTO
# =========================================================

from experiments.case_factory import (
    ExperimentalCaseFactory,
)

from engines.experimental_runner import (
    ExperimentalRunner,
)

from engines.experimental_metrics_engine import (
    ExperimentalMetricsEngine,
)

from engines.recommendation_sensitivity import (
    RecommendationSensitivityEngine,
)

from twin.experiment import (
    ExperimentMode,
    ExperimentCondition,
)


# =========================================================
# 3. COMPONENTES
# =========================================================

factory = ExperimentalCaseFactory()

runner = ExperimentalRunner()

metrics_engine = ExperimentalMetricsEngine()

sensitivity_engine = (
    RecommendationSensitivityEngine()
)


# =========================================================
# 4. MODOS EXPERIMENTALES
# =========================================================

modes = [
    ExperimentMode.B0_MACHINE_ONLY,
    ExperimentMode.B1_UNTYPED_HUMAN,
    ExperimentMode.P_PROVENANCE_AWARE,
]


# =========================================================
# 5. CONDICIONES EXPERIMENTALES
# =========================================================

conditions = [
    ExperimentCondition.COMPLETE,
    ExperimentCondition.MISSING_STALE,
    ExperimentCondition.CONFLICT,
]


# =========================================================
# 6. EJECUTAR LAS 9 CORRIDAS
# =========================================================

metrics_objects = []


for condition in conditions:

    case = factory.build(
        condition
    )

    for mode in modes:

        result = runner.run(
            mode=mode,

            condition=condition,

            scenarios=case.scenarios,

            evidence=case.evidence,

            farmer_knowledge=(
                case.farmer_knowledge
            ),
        )

        metrics = (
            metrics_engine.calculate(
                result=result,

                farmer_knowledge=(
                    case.farmer_knowledge
                ),
            )
        )

        metrics_objects.append(
            metrics
        )


# =========================================================
# 7. CALCULAR SENSIBILIDAD DE RECOMENDACIÓN
# =========================================================

sensitivity_engine.apply(
    metrics_objects
)


# =========================================================
# 8. CONSTRUIR FILAS PARA DATAFRAME
# =========================================================

metric_rows = []


for metrics in metrics_objects:

    metric_rows.append(
        {
            "mode":
                metrics.mode,

            "condition":
                metrics.condition,

            # ---------------------------------------------
            # Provenance / trazabilidad
            # ---------------------------------------------

            "provenance":
                metrics
                .provenance_completeness,

            "trace":
                metrics
                .trace_completeness,

            "knowledge_traceability":
                metrics
                .applied_knowledge_traceability_rate,

            # ---------------------------------------------
            # Uso del conocimiento humano
            # ---------------------------------------------

            "processing_rate":
                metrics
                .knowledge_processing_rate,

            "application_rate":
                metrics
                .knowledge_application_rate,

            "ignore_rate":
                metrics
                .knowledge_ignore_rate,

            # ---------------------------------------------
            # Separación epistemológica
            # ---------------------------------------------

            "epistemic_separation":
                metrics
                .epistemic_separation_score,

            "state_contamination":
                metrics
                .state_contamination_rate,

            # ---------------------------------------------
            # Restricciones
            # ---------------------------------------------

            "feasible_constraint_violation":
                metrics
                .feasible_constraint_violation_rate,

            "recommendation_constraint_violation":
                metrics
                .recommendation_constraint_violation,

            # ---------------------------------------------
            # Conflictos
            # ---------------------------------------------

            "conflict_recall":
                metrics
                .conflict_recall,

            "conflict_correct":
                metrics
                .conflict_detection_correctness,

            # ---------------------------------------------
            # Recomendación
            # ---------------------------------------------

            "recommendation_mm":
                metrics
                .recommendation_irrigation_mm,

            "sensitivity_mm":
                metrics
                .recommendation_sensitivity_mm,

            "changed_from_b0":
                metrics
                .recommendation_changed_from_b0,

            # ---------------------------------------------
            # Transformaciones
            # ---------------------------------------------

            "transformations":
                metrics
                .transformation_count,


            "degraded_detected":
                metrics.degraded_evidence_detected,

            "degraded_count":
                metrics.degraded_evidence_count,

            "robustness_degraded":
                metrics.robustness_under_degraded_evidence,

            # ---------------------------------------------
            # Tipado Correcto
            # ---------------------------------------------
            "typing_correctness":
                metrics.typing_correctness,
        }
    )


# =========================================================
# 9. DATAFRAME
# =========================================================

df = pd.DataFrame(
    metric_rows
)


# =========================================================
# 10. MOSTRAR RESULTADOS
# =========================================================

print()
print("EXPERIMENTAL METRICS")
print("=" * 220)

print(
    df.to_string(
        index=False
    )
)

print("=" * 220)

print(
    "TOTAL METRIC RUNS:",
    len(df),
)