from twin.quality_gate import (
    TwinQualityGateResult,
)

from twin.decision_risk import (
    DecisionRiskLevel,
    DecisionRiskResult,
)


class DecisionRiskEngine:

    def evaluate(
        self,
        quality_gate: TwinQualityGateResult,
        twin_confidence: float | None,
        conflict_count: int,
    ) -> DecisionRiskResult:

        reasons = []

        if not quality_gate.recommendation_allowed:

            return DecisionRiskResult(
                risk_level=DecisionRiskLevel.BLOCKED,
                decision_confidence=0.0,
                requires_human_confirmation=True,
                reasons=[
                    "Recommendation blocked by Twin Quality Gate."
                ],
            )

        confidence = (
            0.5
            if twin_confidence is None
            else max(
                0.0,
                min(
                    twin_confidence,
                    1.0,
                ),
            )
        )

        # -----------------------------------------
        # Confianza base
        # -----------------------------------------

        if confidence >= 0.80:
            risk = DecisionRiskLevel.LOW

        elif confidence >= 0.50:
            risk = DecisionRiskLevel.MODERATE

        else:
            risk = DecisionRiskLevel.HIGH

        # -----------------------------------------
        # Conflictos humano-máquina
        # -----------------------------------------

        requires_confirmation = False

        if conflict_count > 0:

            reasons.append(
                f"{conflict_count} unresolved conflict(s) detected."
            )

            requires_confirmation = True

            if risk == DecisionRiskLevel.LOW:
                risk = DecisionRiskLevel.MODERATE

        # -----------------------------------------
        # Estado degradado
        # -----------------------------------------

        if quality_gate.degraded_variables:

            reasons.append(
                "One or more critical Twin variables are degraded."
            )

            requires_confirmation = True

            if risk == DecisionRiskLevel.LOW:
                risk = DecisionRiskLevel.MODERATE

        if not reasons:
            reasons.append(
                "Twin state is sufficiently reliable for autonomous recommendation."
            )

        return DecisionRiskResult(
            risk_level=risk,
            decision_confidence=confidence,
            requires_human_confirmation=(
                requires_confirmation
            ),
            reasons=reasons,
        )