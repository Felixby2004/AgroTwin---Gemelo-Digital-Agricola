from datetime import datetime
from uuid import uuid4

from twin.evidence import (
    MachineEvidence,
    EvidenceStatus,
)

from twin.provenance import (
    ProvenanceRecord,
    EvidenceSourceType,
)

from twin.decision_trace import (
    HumanTwinDecisionTrace,
)


class FeedbackEngine:

    def create_observation_evidence(
        self,
        trace: HumanTwinDecisionTrace,
        variable: str,
        value,
        unit: str | None,
        source_name: str,
        observed_at: datetime,
        spatial_scope: str | None = None,
        quality_score: float | None = None,
    ) -> MachineEvidence:

        if trace.outcome is None:
            raise ValueError(
                "El trace debe tener un outcome "
                "antes de crear evidencia de feedback."
            )

        evidence_id = (
            f"EV-FB-"
            f"{uuid4().hex[:10].upper()}"
        )

        provenance = ProvenanceRecord(
            source_type=(
                EvidenceSourceType.MEASURED
            ),

            source_name=source_name,

            generated_at=datetime.now(),

            valid_at=observed_at,

            spatial_scope=spatial_scope,

            transformation=(
                "Post-decision outcome observation"
            ),

            parent_ids=[
                trace.trace_id,
                trace.outcome.outcome_id,
            ],

            metadata={
                "feedback_from_trace":
                    trace.trace_id,

                "outcome_id":
                    trace.outcome.outcome_id,
            },
        )

        evidence = MachineEvidence(
            evidence_id=evidence_id,

            variable=variable,

            value=value,

            unit=unit,

            observed_at=observed_at,

            provenance=provenance,

            status=EvidenceStatus.ACTIVE,

            quality_score=quality_score,

            metadata={
                "feedback_cycle": True,
            },
        )

        return evidence