from collections import defaultdict

from twin.evidence import (
    MachineEvidence,
)

from twin.evidence_policy import (
    EvidenceUsePolicy,
)

from twin.trusted_state import (
    TrustedStateVariable,
    TrustedTwinState,
)

from engines.evidence_policy_engine import (
    EvidencePolicyEngine,
)

from engines.state_confidence_engine import (
    StateConfidenceEngine,
)


class TrustedStateEngine:

    def __init__(
        self,
        policy_engine: EvidencePolicyEngine | None = None,
        confidence_engine: StateConfidenceEngine | None = None,
    ):

        self.policy_engine = (
            policy_engine
            if policy_engine is not None
            else EvidencePolicyEngine()
        )

        self.confidence_engine = (
            confidence_engine
            if confidence_engine is not None
            else StateConfidenceEngine(
                policy_engine=self.policy_engine
            )
        )


    # =====================================================
    # BUILD TRUSTED STATE
    # =====================================================

    def build(
        self,
        evidence_items: list[
            MachineEvidence
        ],
    ) -> TrustedTwinState:

        grouped = defaultdict(
            list
        )

        excluded_evidence_ids = []


        # =================================================
        # 1. EVIDENCE POLICY
        # =================================================

        for item in evidence_items:

            decision = (
                self.policy_engine.evaluate(
                    item
                )
            )

            if (
                decision.policy
                == EvidenceUsePolicy.EXCLUDE
            ):

                excluded_evidence_ids.append(
                    item.evidence_id
                )

                continue


            grouped[
                item.variable
            ].append(
                item
            )


        variables = {}

        update_required_variables = []


        # =================================================
        # 2. BUILD EACH TRUSTED VARIABLE
        # =================================================

        for variable, items in grouped.items():

            # ---------------------------------------------
            # Aggregate state confidence
            # ---------------------------------------------

            confidence = (
                self.confidence_engine
                .calculate_for_variable(
                    variable=variable,
                    evidence_items=items,
                )
            )


            # ---------------------------------------------
            # Current-state candidates only
            # ---------------------------------------------

            current_candidates = []

            for item in items:

                decision = (
                    self.policy_engine.evaluate(
                        item
                    )
                )

                if (
                    decision.usable_as_current_state
                ):

                    current_candidates.append(
                        (
                            item,
                            decision,
                        )
                    )


            selected_item = None


            # =================================================
            # 3. SELECT CURRENT EVIDENCE
            #
            # Priority:
            #
            # 1. Real operational evidence
            # 2. Generic evidence
            # 3. Manual/test evidence
            #
            # Then:
            # - quality score
            # - most recent observation
            #
            # STALE evidence never enters this candidate list.
            # =================================================

            if current_candidates:

                current_candidates.sort(
                    key=lambda candidate: (
                        self._origin_priority(
                            candidate[0]
                        ),

                        (
                            candidate[0]
                            .quality_score
                            or 0.0
                        ),

                        candidate[0]
                        .observed_at,
                    ),
                    reverse=True,
                )


                selected_item = (
                    current_candidates[
                        0
                    ][
                        0
                    ]
                )


            # =================================================
            # 4. CURRENT VALUE
            #
            # If there is no usable current evidence,
            # STALE evidence is NOT promoted.
            # =================================================

            if selected_item is not None:

                value = (
                    selected_item.value
                )

                unit = (
                    selected_item.unit
                )

            else:

                value = None

                unit = None


            # =================================================
            # 5. PROVENANCE LINKS
            # =================================================

            source_evidence_ids = [
                item.evidence_id
                for item in items
            ]


            # =================================================
            # 6. TRUSTED VARIABLE
            # =================================================

            variables[
                variable
            ] = TrustedStateVariable(
                variable=variable,

                value=value,

                unit=unit,

                source_evidence_ids=(
                    source_evidence_ids
                ),

                confidence=confidence,

                metadata={
                    "selected_evidence_id":
                        (
                            selected_item
                            .evidence_id

                            if selected_item
                            is not None

                            else None
                        ),

                    "selected_origin":
                        (
                            self
                            ._get_origin(
                                selected_item
                            )

                            if selected_item
                            is not None

                            else None
                        ),
                },
            )


            # =================================================
            # 7. UPDATE REQUIREMENT
            # =================================================

            if confidence.requires_update:

                update_required_variables.append(
                    variable
                )


        # =====================================================
        # 8. TRUSTED TWIN STATE
        # =====================================================

        return TrustedTwinState(
            variables=variables,

            excluded_evidence_ids=(
                excluded_evidence_ids
            ),

            update_required_variables=(
                update_required_variables
            ),

            metadata={
                "variable_count":
                    len(
                        variables
                    ),

                "excluded_evidence_count":
                    len(
                        excluded_evidence_ids
                    ),
            },
        )


    # =====================================================
    # ORIGIN
    # =====================================================

    @staticmethod
    def _get_origin(
        evidence: MachineEvidence,
    ) -> str | None:

        metadata = (
            evidence.metadata
            or {}
        )


        # Explicit satellite/manual origin.
        origin = metadata.get(
            "data_origin"
        )

        if origin:
            return origin


        # IoT readings created in
        # SensorIngestionService currently use:
        #
        # ingestion_type = "IOT"
        #
        ingestion_type = metadata.get(
            "ingestion_type"
        )

        if ingestion_type:
            return ingestion_type


        return None


    # =====================================================
    # ORIGIN PRIORITY
    # =====================================================

    @classmethod
    def _origin_priority(
        cls,
        evidence: MachineEvidence,
    ) -> int:

        origin = (
            cls._get_origin(
                evidence
            )
        )


        # ---------------------------------------------
        # Real data
        # ---------------------------------------------

        if origin == "CDSE_REAL":
            return 3

        if origin == "IOT":
            return 3


        # ---------------------------------------------
        # Explicit manual/test observations
        # ---------------------------------------------

        if origin == "MANUAL_TEST":
            return 1


        # ---------------------------------------------
        # Existing/legacy evidence
        # ---------------------------------------------

        return 2