from dataclasses import dataclass


@dataclass
class ExperimentalMetrics:
    mode: str
    condition: str

    # Conocimiento humano
    knowledge_processing_rate: float
    knowledge_application_rate: float
    knowledge_ignore_rate: float

    # Separación epistemológica
    epistemic_separation_score: float
    state_contamination_rate: float

    # Restricciones
    feasible_constraint_violation_rate: float
    recommendation_constraint_violation: float

    # Conflictos
    expected_conflicts: int
    detected_conflicts: int
    conflict_recall: float | None
    conflict_false_positives: int
    conflict_detection_correctness: float

    # Trazabilidad
    applied_knowledge_traceability_rate: float | None

    # Resultado decisional
    recommendation_irrigation_mm: float | None

    # Información auxiliar
    processed_knowledge_count: int
    applied_knowledge_count: int
    ignored_knowledge_count: int
    transformation_count: int

    provenance_completeness: float | None
    trace_completeness: float | None

    recommendation_sensitivity_mm: float | None

    recommendation_changed_from_b0: float | None

    degraded_evidence_detected: float | None

    degraded_evidence_count: int

    robustness_under_degraded_evidence: float | None

    typing_correctness: float | None