from datetime import datetime
from uuid import uuid4

from twin.decision_trace import (
    HumanTwinDecisionTrace,
)

from twin.outcome import (
    DecisionOutcome,
    OutcomeStatus,
)


class OutcomeEngine:

    def register_outcome(
        self,
        trace: HumanTwinDecisionTrace,
        executed_action: dict | None,
        observations: dict | None = None,
        resulting_evidence_ids: list[str] | None = None,
        rationale: str | None = None,
        status: OutcomeStatus = OutcomeStatus.OBSERVED,
    ) -> HumanTwinDecisionTrace:

        # -------------------------------------------------
        # 1. Debe existir respuesta del agricultor
        # -------------------------------------------------

        if trace.farmer_response is None:
            raise ValueError(
                "No se puede registrar outcome "
                "sin respuesta del agricultor."
            )

        # -------------------------------------------------
        # 2. Obtener acción final esperada
        # -------------------------------------------------

        final_action = (
            trace.get_final_action()
        )

        # -------------------------------------------------
        # 3. Detectar desviación entre acción final
        #    y acción realmente ejecutada
        # -------------------------------------------------

        deviation = self._calculate_deviation(
            final_action=final_action,
            executed_action=executed_action,
        )

        # -------------------------------------------------
        # 4. Crear outcome
        # -------------------------------------------------

        outcome = DecisionOutcome(
            outcome_id=(
                f"OUT-"
                f"{uuid4().hex[:12].upper()}"
            ),

            trace_id=trace.trace_id,

            status=status,

            recorded_at=datetime.now(),

            executed_action=executed_action,

            observations=(
                observations or {}
            ),

            resulting_evidence_ids=(
                resulting_evidence_ids or []
            ),

            deviation_from_final_action=(
                deviation
            ),

            rationale=rationale,

            metadata={
                "expected_final_action":
                    final_action,
            },
        )

        # -------------------------------------------------
        # 5. Asociarlo al DecisionTrace
        # -------------------------------------------------

        trace.outcome = outcome

        return trace


    def _calculate_deviation(
        self,
        final_action: dict | None,
        executed_action: dict | None,
    ) -> dict | None:

        # -------------------------------------------------
        # REJECT:
        # acción final = None
        # -------------------------------------------------

        if (
            final_action is None
            and executed_action is None
        ):
            return None

        if (
            final_action is None
            and executed_action is not None
        ):
            return {
                "expected": None,
                "executed": executed_action,
                "deviation_detected": True,
                "reason": (
                    "Se ejecutó una acción aunque "
                    "la decisión final era no ejecutar."
                ),
            }

        if (
            final_action is not None
            and executed_action is None
        ):
            return {
                "expected": final_action,
                "executed": None,
                "deviation_detected": True,
                "reason": (
                    "La acción final aprobada "
                    "no fue ejecutada."
                ),
            }

        # -------------------------------------------------
        # Comparar irrigation_mm
        # -------------------------------------------------

        expected_mm = final_action.get(
            "irrigation_mm"
        )

        executed_mm = executed_action.get(
            "irrigation_mm"
        )

        if (
            expected_mm is not None
            and executed_mm is not None
        ):

            difference_mm = round(
                float(executed_mm)
                - float(expected_mm),
                6,
            )

            return {
                "expected_irrigation_mm":
                    float(expected_mm),

                "executed_irrigation_mm":
                    float(executed_mm),

                "difference_mm":
                    difference_mm,

                "absolute_difference_mm": round(
                    abs(difference_mm),
                    6,
                ),

                "deviation_detected":
                    abs(difference_mm) > 1e-9,
            }

        # -------------------------------------------------
        # Comparación genérica
        # -------------------------------------------------

        if final_action != executed_action:

            return {
                "expected": final_action,
                "executed": executed_action,
                "deviation_detected": True,
            }

        return None