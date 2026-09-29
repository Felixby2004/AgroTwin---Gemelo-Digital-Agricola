from collections import defaultdict

from twin.evidence import (
    MachineEvidence,
)

from twin.evidence_policy import (
    EvidenceUsePolicy,
)

from twin.state_confidence import (
    StateConfidence,
    UncertaintyLevel,
)

from engines.evidence_policy_engine import (
    EvidencePolicyEngine,
)


class StateConfidenceEngine:

    def __init__(
        self,
        policy_engine: EvidencePolicyEngine | None = None,
    ):

        self.policy_engine = (
            policy_engine
            if policy_engine is not None
            else EvidencePolicyEngine()
        )


    def calculate_for_variable(
        self,
        variable: str,
        evidence_items: list[
            MachineEvidence
        ],
    ) -> StateConfidence:

        relevant = [
            item
            for item in evidence_items
            if item.variable == variable
        ]

        if not relevant:

            return StateConfidence(
                variable=variable,

                confidence_score=None,

                uncertainty_level=(
                    UncertaintyLevel.UNKNOWN
                ),

                supporting_evidence_count=0,

                current_state_evidence_count=0,

                degraded_evidence_count=0,

                excluded_evidence_count=0,

                requires_update=True,

                rationale=[
                    "No evidence available "
                    "for this variable."
                ],
            )


        decisions = [
            self.policy_engine.evaluate(
                item
            )
            for item in relevant
        ]


        supporting = []

        current_state_count = 0
        degraded_count = 0
        excluded_count = 0
        requires_update = False

        rationale = []


        for evidence, decision in zip(
            relevant,
            decisions,
        ):

            if decision.usable_for_reasoning:

                supporting.append(
                    decision.confidence_weight
                )

            if decision.usable_as_current_state:

                current_state_count += 1

            if (
                decision.policy
                in {
                    EvidenceUsePolicy
                    .USE_WITH_CAUTION,

                    EvidenceUsePolicy
                    .REQUEST_UPDATE,
                }
            ):

                degraded_count += 1

            if (
                decision.policy
                == EvidenceUsePolicy.EXCLUDE
            ):

                excluded_count += 1

            if decision.requires_update:

                requires_update = True

            rationale.append(
                (
                    f"{evidence.evidence_id}: "
                    f"{decision.policy.value}, "
                    f"weight="
                    f"{decision.confidence_weight:.2f}"
                )
            )


        if supporting:

            confidence_score = (
                sum(supporting)
                / len(supporting)
            )

        else:

            confidence_score = None


        uncertainty_level = (
            self._to_uncertainty_level(
                confidence_score=(
                    confidence_score
                ),

                current_state_count=(
                    current_state_count
                ),
            )
        )


        return StateConfidence(
            variable=variable,

            confidence_score=(
                confidence_score
            ),

            uncertainty_level=(
                uncertainty_level
            ),

            supporting_evidence_count=(
                len(supporting)
            ),

            current_state_evidence_count=(
                current_state_count
            ),

            degraded_evidence_count=(
                degraded_count
            ),

            excluded_evidence_count=(
                excluded_count
            ),

            requires_update=(
                requires_update
            ),

            rationale=rationale,
        )


    def calculate_all(
        self,
        evidence_items: list[
            MachineEvidence
        ],
    ) -> list[
        StateConfidence
    ]:

        variables = sorted(
            {
                item.variable
                for item in evidence_items
            }
        )

        return [
            self.calculate_for_variable(
                variable=variable,
                evidence_items=evidence_items,
            )
            for variable in variables
        ]


    def _to_uncertainty_level(
        self,
        confidence_score: float | None,
        current_state_count: int,
    ) -> UncertaintyLevel:

        if confidence_score is None:

            return (
                UncertaintyLevel.UNKNOWN
            )

        if current_state_count == 0:

            return (
                UncertaintyLevel.HIGH
            )

        if confidence_score >= 0.80:

            return (
                UncertaintyLevel.LOW
            )

        if confidence_score >= 0.50:

            return (
                UncertaintyLevel.MEDIUM
            )

        return (
            UncertaintyLevel.HIGH
        )