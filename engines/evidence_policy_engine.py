from twin.evidence import (
    MachineEvidence,
    EvidenceStatus,
)

from twin.evidence_policy import (
    EvidencePolicyDecision,
    EvidenceUsePolicy,
)


class EvidencePolicyEngine:

    def __init__(
        self,
        minimum_quality: float = 0.60,
    ):

        self.minimum_quality = (
            minimum_quality
        )


    def evaluate(
        self,
        evidence: MachineEvidence,
    ) -> EvidencePolicyDecision:

        # =================================================
        # 1. INVALID
        # =================================================

        if (
            evidence.status
            == EvidenceStatus.INVALID
        ):

            return EvidencePolicyDecision(
                evidence_id=(
                    evidence.evidence_id
                ),

                policy=(
                    EvidenceUsePolicy.EXCLUDE
                ),

                usable_for_reasoning=False,

                usable_as_current_state=False,

                requires_update=True,

                confidence_weight=0.0,

                reason=(
                    "Evidence is INVALID and "
                    "must be excluded from "
                    "operational reasoning."
                ),
            )


        # =================================================
        # 2. SUPERSEDED
        # =================================================

        if (
            evidence.status
            == EvidenceStatus.SUPERSEDED
        ):

            return EvidencePolicyDecision(
                evidence_id=(
                    evidence.evidence_id
                ),

                policy=(
                    EvidenceUsePolicy.EXCLUDE
                ),

                usable_for_reasoning=False,

                usable_as_current_state=False,

                requires_update=False,

                confidence_weight=0.0,

                reason=(
                    "Evidence was superseded by "
                    "a newer record."
                ),
            )


        # =================================================
        # 3. STALE
        # =================================================

        if (
            evidence.status
            == EvidenceStatus.STALE
        ):

            quality = (
                evidence.quality_score
                if evidence.quality_score
                is not None
                else 0.5
            )

            confidence_weight = (
                max(
                    0.0,
                    min(
                        quality * 0.5,
                        1.0,
                    ),
                )
            )

            return EvidencePolicyDecision(
                evidence_id=(
                    evidence.evidence_id
                ),

                policy=(
                    EvidenceUsePolicy.REQUEST_UPDATE
                ),

                usable_for_reasoning=True,

                # Importante:
                # puede servir como contexto,
                # pero NO como estado actual.
                usable_as_current_state=False,

                requires_update=True,

                confidence_weight=(
                    confidence_weight
                ),

                reason=(
                    "Evidence is STALE. It may "
                    "be preserved as historical "
                    "or contextual evidence but "
                    "must not be treated as a "
                    "current measurement."
                ),
            )


        # =================================================
        # 4. ACTIVE + calidad desconocida
        # =================================================

        if (
            evidence.quality_score
            is None
        ):

            return EvidencePolicyDecision(
                evidence_id=(
                    evidence.evidence_id
                ),

                policy=(
                    EvidenceUsePolicy
                    .USE_WITH_CAUTION
                ),

                usable_for_reasoning=True,

                usable_as_current_state=True,

                requires_update=False,

                confidence_weight=0.5,

                reason=(
                    "Evidence is ACTIVE but has "
                    "no explicit quality score."
                ),
            )


        # =================================================
        # 5. ACTIVE + baja calidad
        # =================================================

        if (
            evidence.quality_score
            < self.minimum_quality
        ):

            return EvidencePolicyDecision(
                evidence_id=(
                    evidence.evidence_id
                ),

                policy=(
                    EvidenceUsePolicy
                    .USE_WITH_CAUTION
                ),

                usable_for_reasoning=True,

                usable_as_current_state=True,

                requires_update=False,

                confidence_weight=(
                    max(
                        0.0,
                        min(
                            evidence.quality_score,
                            1.0,
                        ),
                    )
                ),

                reason=(
                    "Evidence is ACTIVE but its "
                    "quality score is below the "
                    "preferred threshold."
                ),
            )


        # =================================================
        # 6. ACTIVE + calidad suficiente
        # =================================================

        return EvidencePolicyDecision(
            evidence_id=(
                evidence.evidence_id
            ),

            policy=(
                EvidenceUsePolicy.USE_NORMALLY
            ),

            usable_for_reasoning=True,

            usable_as_current_state=True,

            requires_update=False,

            confidence_weight=(
                max(
                    0.0,
                    min(
                        evidence.quality_score,
                        1.0,
                    ),
                )
            ),

            reason=(
                "Evidence is active and its "
                "quality is sufficient for "
                "normal operational use."
            ),
        )


    def evaluate_all(
        self,
        evidence_items: list[
            MachineEvidence
        ],
    ) -> list[
        EvidencePolicyDecision
    ]:

        return [
            self.evaluate(
                evidence=item
            )
            for item in evidence_items
        ]