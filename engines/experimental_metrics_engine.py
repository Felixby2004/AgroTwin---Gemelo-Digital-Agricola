from twin.experiment import (
    ExperimentalRunResult,
    ExperimentCondition,
)

from twin.farmer_knowledge import (
    FarmerKnowledgeItem,
    FarmerKnowledgeType,
    KnowledgeValidationStatus,
    ConstraintType,
)

from twin.experimental_metrics import (
    ExperimentalMetrics,
)

from engines.typing_metrics_engine import (
    TypingMetricsEngine,
)


class ExperimentalMetricsEngine:

    def __init__(self):

        self.typing_metrics_engine = (
            TypingMetricsEngine()
        )

    def calculate(
        self,
        result: ExperimentalRunResult,
        farmer_knowledge: list[FarmerKnowledgeItem],
    ) -> ExperimentalMetrics:

        total_knowledge = len(
            farmer_knowledge
        )

        processed_count = len(
            set(
                result.processed_knowledge_ids
            )
        )

        applied_count = len(
            set(
                result.applied_knowledge_ids
            )
        )

        ignored_count = len(
            set(
                result.ignored_knowledge_ids
            )
        )

        # =================================================
        # 1. KNOWLEDGE PROCESSING
        # =================================================

        if total_knowledge > 0:

            knowledge_processing_rate = (
                processed_count
                / total_knowledge
            )

            knowledge_application_rate = (
                applied_count
                / total_knowledge
            )

            knowledge_ignore_rate = (
                ignored_count
                / total_knowledge
            )

        else:

            knowledge_processing_rate = 1.0
            knowledge_application_rate = 0.0
            knowledge_ignore_rate = 0.0

        # =================================================
        # 2. EPISTEMIC SEPARATION
        # =================================================

        epistemic_separation_score = (
            1.0
            if result.epistemic_separation_preserved
            else 0.0
        )

        state_contamination_rate = (
            1.0
            if result.state_contamination_detected
            else 0.0
        )

        # =================================================
        # 3. HARD CONSTRAINTS
        # =================================================

        hard_constraints = [
            item
            for item in farmer_knowledge
            if (
                item.knowledge_type
                == FarmerKnowledgeType.CONSTRAINT
                and item.validation_status
                == KnowledgeValidationStatus.CONFIRMED
                and item.constraint_type
                == ConstraintType.HARD
            )
        ]

        violating_feasible = 0

        for scenario in result.feasible_scenarios:

            if self._violates_any_constraint(
                irrigation_mm=(
                    scenario.irrigation_mm
                ),
                constraints=hard_constraints,
            ):
                violating_feasible += 1

        if result.feasible_scenarios:

            feasible_constraint_violation_rate = (
                violating_feasible
                / len(
                    result.feasible_scenarios
                )
            )

        else:

            feasible_constraint_violation_rate = 0.0

        # -------------------------------------------------
        # Recomendación final vs restricciones
        # -------------------------------------------------

        recommendation_constraint_violation = 0.0

        recommendation_mm = None

        if result.recommendation is not None:

            recommendation_mm = (
                result.recommendation.get(
                    "irrigation_mm"
                )
            )

            if (
                recommendation_mm is not None
                and self._violates_any_constraint(
                    irrigation_mm=float(
                        recommendation_mm
                    ),
                    constraints=hard_constraints,
                )
            ):
                recommendation_constraint_violation = 1.0

        # =================================================
        # 4. CONFLICT DETECTION
        # =================================================

        expected_conflicts = (
            1
            if (
                result.condition
                == ExperimentCondition.CONFLICT
            )
            else 0
        )

        detected_conflicts = len(
            result.conflicts
        )

        if expected_conflicts > 0:

            conflict_recall = min(
                detected_conflicts
                / expected_conflicts,
                1.0,
            )

            conflict_false_positives = max(
                detected_conflicts
                - expected_conflicts,
                0,
            )

            conflict_detection_correctness = (
                1.0
                if (
                    detected_conflicts
                    == expected_conflicts
                )
                else 0.0
            )

        else:

            conflict_recall = None

            conflict_false_positives = (
                detected_conflicts
            )

            conflict_detection_correctness = (
                1.0
                if detected_conflicts == 0
                else 0.0
            )

        # =================================================
        # 5. KNOWLEDGE TRACEABILITY
        # =================================================

        traced_knowledge_ids = set()

        # Transformaciones
        for transformation in (
            result.transformations
        ):

            source_id = (
                transformation
                .source_knowledge_id
            )

            if source_id:
                traced_knowledge_ids.add(
                    source_id
                )

        # Conflictos
        for conflict in result.conflicts:

            if conflict.right_item_id:
                traced_knowledge_ids.add(
                    conflict.right_item_id
                )

            if conflict.left_item_id:
                traced_knowledge_ids.add(
                    conflict.left_item_id
                )

        applied_ids = set(
            result.applied_knowledge_ids
        )

        if applied_ids:

            traced_applied_ids = (
                applied_ids
                &
                traced_knowledge_ids
            )

            applied_knowledge_traceability_rate = (
                len(
                    traced_applied_ids
                )
                / len(
                    applied_ids
                )
            )

        else:

            # No hubo conocimiento aplicado.
            # No lo penalizamos.
            applied_knowledge_traceability_rate = None



        # =================================================
        # 6. PROVENANCE COMPLETENESS
        # =================================================

        provenance_completeness = (
            self._calculate_provenance_completeness(
                result=result,
                farmer_knowledge=farmer_knowledge,
            )
        )


        # =================================================
        # 7. TRACE COMPLETENESS
        # =================================================

        trace_completeness = (
            self._calculate_trace_completeness(
                result=result,
            )
        )

        # =================================================
        # DEGRADED / STALE EVIDENCE
        # =================================================

        degraded_evidence_count = int(
            result.metadata.get(
                "degraded_evidence_count",
                0,
            )
        )

        if (
            result.condition
            == ExperimentCondition.MISSING_STALE
        ):

            degraded_evidence_detected = (
                1.0
                if degraded_evidence_count > 0
                else 0.0
            )

            robustness_under_degraded_evidence = (
                1.0
                if (
                    degraded_evidence_detected == 1.0
                    and result.epistemic_separation_preserved
                    and not result.state_contamination_detected
                )
                else 0.0
            )

        else:

            degraded_evidence_detected = None
            robustness_under_degraded_evidence = None


        # =================================================
        # TYPING CORRECTNESS
        # =================================================

        if result.knowledge_effects:

            typing_metrics = (
                self.typing_metrics_engine.calculate(
                    farmer_knowledge=farmer_knowledge,
                    knowledge_effects=(
                        result.knowledge_effects
                    ),
                )
            )

            typing_correctness = (
                typing_metrics.typing_correctness
            )

        else:

            typing_correctness = None


        # =================================================
        # 8. RESULT
        # =================================================

        return ExperimentalMetrics(
            mode=result.mode.value,

            condition=result.condition.value,

            knowledge_processing_rate=(
                knowledge_processing_rate
            ),

            knowledge_application_rate=(
                knowledge_application_rate
            ),

            knowledge_ignore_rate=(
                knowledge_ignore_rate
            ),

            epistemic_separation_score=(
                epistemic_separation_score
            ),

            state_contamination_rate=(
                state_contamination_rate
            ),

            feasible_constraint_violation_rate=(
                feasible_constraint_violation_rate
            ),

            recommendation_constraint_violation=(
                recommendation_constraint_violation
            ),

            expected_conflicts=(
                expected_conflicts
            ),

            detected_conflicts=(
                detected_conflicts
            ),

            conflict_recall=(
                conflict_recall
            ),

            conflict_false_positives=(
                conflict_false_positives
            ),

            conflict_detection_correctness=(
                conflict_detection_correctness
            ),

            applied_knowledge_traceability_rate=(
                applied_knowledge_traceability_rate
            ),

            recommendation_irrigation_mm=(
                float(
                    recommendation_mm
                )
                if recommendation_mm
                is not None
                else None
            ),

            processed_knowledge_count=(
                processed_count
            ),

            applied_knowledge_count=(
                applied_count
            ),

            ignored_knowledge_count=(
                ignored_count
            ),

            transformation_count=len(
                result.transformations
            ),

            provenance_completeness=(
                provenance_completeness
            ),

            trace_completeness=(
                trace_completeness
            ),

            recommendation_sensitivity_mm=None,

            recommendation_changed_from_b0=None,

            degraded_evidence_detected=(
                degraded_evidence_detected
            ),

            degraded_evidence_count=(
                degraded_evidence_count
            ),

            robustness_under_degraded_evidence=(
                robustness_under_degraded_evidence
            ),

            typing_correctness=(
                typing_correctness
            ),
        )


    # =====================================================
    # CONSTRAINT HELPERS
    # =====================================================

    def _violates_any_constraint(
        self,
        irrigation_mm: float,
        constraints: list[
            FarmerKnowledgeItem
        ],
    ) -> bool:

        for constraint in constraints:

            payload = constraint.payload

            if not isinstance(
                payload,
                dict,
            ):
                continue

            variable = payload.get(
                "variable"
            )

            if variable != "irrigation_mm":
                continue

            operator = payload.get(
                "operator"
            )

            limit = payload.get(
                "value"
            )

            if limit is None:
                continue

            if not self._compare(
                left=float(
                    irrigation_mm
                ),
                operator=operator,
                right=float(
                    limit
                ),
            ):
                return True

        return False


    @staticmethod
    def _compare(
        left: float,
        operator: str,
        right: float,
    ) -> bool:

        if operator == "<=":
            return left <= right

        if operator == "<":
            return left < right

        if operator == ">=":
            return left >= right

        if operator == ">":
            return left > right

        if operator == "==":
            return left == right

        raise ValueError(
            f"Operador no soportado: "
            f"{operator}"
        )


    def _calculate_provenance_completeness(
        self,
        result: ExperimentalRunResult,
        farmer_knowledge: list[
            FarmerKnowledgeItem
        ],
    ) -> float | None:

        provenance_enabled = (
            result.metadata.get(
                "provenance_enabled",
                None,
            )
        )

        if provenance_enabled is False:
            return 0.0

        # -------------------------------------------------
        # B0 no utiliza conocimiento humano.
        # La métrica de provenance del conocimiento humano
        # no es aplicable.
        # -------------------------------------------------

        if not result.processed_knowledge_ids:
            return None

        processed_ids = set(
            result.processed_knowledge_ids
        )

        applied_ids = set(
            result.applied_knowledge_ids
        )

        transformation_sources = {
            transformation.source_knowledge_id
            for transformation
            in result.transformations
            if transformation.source_knowledge_id
        }

        conflict_sources = {
            conflict.right_item_id
            for conflict
            in result.conflicts
            if conflict.right_item_id
        }

        complete = 0

        total_processed = len(
            processed_ids
        )

        if total_processed == 0:
            return None

        for knowledge_id in processed_ids:

            # ---------------------------------------------
            # Si fue realmente aplicado a la decisión,
            # debe existir una referencia explícita
            # a ese conocimiento.
            # ---------------------------------------------

            if knowledge_id in applied_ids:

                traced = (
                    knowledge_id
                    in transformation_sources
                    or knowledge_id
                    in conflict_sources
                )

                if traced:
                    complete += 1

            else:

                # -----------------------------------------
                # Procesado pero no aplicado.
                #
                # P puede preservar el conocimiento como
                # contexto, hipótesis o validación pendiente.
                #
                # B1 no tiene semántica tipada explícita.
                # -----------------------------------------

                human_input_typed = (
                    result.metadata.get(
                        "human_input_typed"
                    )
                )

                if human_input_typed is True:
                    complete += 1

        return (
            complete
            / total_processed
        )


    def _calculate_trace_completeness(
        self,
        result: ExperimentalRunResult,
    ) -> float | None:

        # -------------------------------------------------
        # La métrica representa Human–Twin Decision Trace.
        #
        # Si el sistema no procesa conocimiento humano,
        # no es aplicable.
        # -------------------------------------------------

        if not result.processed_knowledge_ids:
            return None

        components = []

        # -------------------------------------------------
        # 1. Recomendación disponible
        # -------------------------------------------------

        components.append(
            1.0
            if result.recommendation
            is not None
            else 0.0
        )

        # -------------------------------------------------
        # 2. Ranking disponible
        # -------------------------------------------------

        components.append(
            1.0
            if result.ranking
            else 0.0
        )

        # -------------------------------------------------
        # 3. Espacio factible registrado
        # -------------------------------------------------

        components.append(
            1.0
            if result.feasible_scenarios
            is not None
            else 0.0
        )

        # -------------------------------------------------
        # 4. Conocimiento aplicado trazable
        # -------------------------------------------------

        applied_ids = set(
            result.applied_knowledge_ids
        )

        if applied_ids:

            traced_ids = {
                transformation.source_knowledge_id
                for transformation
                in result.transformations
                if transformation.source_knowledge_id
            }

            traced_ids.update(
                conflict.right_item_id
                for conflict
                in result.conflicts
                if conflict.right_item_id
            )

            traced_rate = (
                len(
                    applied_ids
                    & traced_ids
                )
                / len(
                    applied_ids
                )
            )

            components.append(
                traced_rate
            )

        else:

            components.append(
                1.0
            )

        # -------------------------------------------------
        # 5. Separación epistemológica
        # -------------------------------------------------

        components.append(
            1.0
            if result.epistemic_separation_preserved
            else 0.0
        )

        return (
            sum(components)
            / len(components)
        )