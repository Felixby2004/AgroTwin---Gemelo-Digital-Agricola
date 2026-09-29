from dataclasses import dataclass
from datetime import datetime

from twin.evidence import (
    MachineEvidence,
    EvidenceStatus,
)


@dataclass
class EvidenceQualityAssessment:
    evidence_id: str

    usable: bool
    degraded: bool

    age_hours: float | None

    status: EvidenceStatus

    reason: str


class EvidenceQualityEngine:

    def assess(
        self,
        evidence: MachineEvidence,
        reference_time: datetime,
        stale_after_hours: float = 24.0,
    ) -> EvidenceQualityAssessment:

        age_hours = None

        if evidence.observed_at is not None:

            delta = (
                reference_time
                - evidence.observed_at
            )

            age_hours = (
                delta.total_seconds()
                / 3600.0
            )

        # -------------------------------------------------
        # Evidencia explícitamente inválida
        # -------------------------------------------------

        if (
            evidence.status
            == EvidenceStatus.INVALID
        ):

            return EvidenceQualityAssessment(
                evidence_id=evidence.evidence_id,

                usable=False,
                degraded=True,

                age_hours=age_hours,

                status=evidence.status,

                reason="Evidence marked INVALID.",
            )

        # -------------------------------------------------
        # Evidencia STALE
        # -------------------------------------------------

        if (
            evidence.status
            == EvidenceStatus.STALE
        ):

            return EvidenceQualityAssessment(
                evidence_id=evidence.evidence_id,

                usable=True,
                degraded=True,

                age_hours=age_hours,

                status=evidence.status,

                reason=(
                    "Evidence is STALE and should not "
                    "be treated as current measurement."
                ),
            )

        # -------------------------------------------------
        # Detección temporal adicional
        # -------------------------------------------------

        if (
            age_hours is not None
            and age_hours > stale_after_hours
        ):

            return EvidenceQualityAssessment(
                evidence_id=evidence.evidence_id,

                usable=True,
                degraded=True,

                age_hours=age_hours,

                status=EvidenceStatus.STALE,

                reason=(
                    f"Evidence age "
                    f"{age_hours:.2f} h exceeds "
                    f"{stale_after_hours:.2f} h."
                ),
            )

        # -------------------------------------------------
        # Evidencia vigente
        # -------------------------------------------------

        return EvidenceQualityAssessment(
            evidence_id=evidence.evidence_id,

            usable=True,
            degraded=False,

            age_hours=age_hours,

            status=evidence.status,

            reason="Evidence considered current.",
        )