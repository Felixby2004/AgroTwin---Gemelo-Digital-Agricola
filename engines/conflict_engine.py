from datetime import datetime
from uuid import uuid4

from twin.conflicts import (
    ConflictRecord,
    ConflictType,
    ConflictStatus,
    ConflictAction,
)

from twin.evidence import (
    MachineEvidence,
)

from twin.farmer_knowledge import (
    FarmerKnowledgeItem,
    FarmerKnowledgeType,
    KnowledgeValidationStatus,
)


class ConflictEngine:

    def detect_human_machine_conflict(
        self,
        evidence: MachineEvidence,
        knowledge: FarmerKnowledgeItem,
    ) -> ConflictRecord | None:

        if not knowledge.affects:
            return None

        if evidence.variable not in knowledge.affects:
            return None

        temporal_overlap = True

        if (
            evidence.observed_at is not None
            and knowledge.valid_from is not None
            and knowledge.valid_until is not None
        ):
            temporal_overlap = (
                knowledge.valid_from
                <= evidence.observed_at
                <= knowledge.valid_until
            )

        spatial_overlap = (
            evidence.provenance.spatial_scope
            is not None
            and knowledge.spatial_scope
            is not None
            and (
                evidence.provenance.spatial_scope
                == knowledge.spatial_scope
                or knowledge.spatial_scope.startswith(
                    evidence.provenance.spatial_scope
                )
                or evidence.provenance.spatial_scope.startswith(
                    knowledge.spatial_scope
                )
            )
        )

        if not temporal_overlap:
            return None

        if not spatial_overlap:
            return None

        actions = [
            ConflictAction.PRESERVE_BOTH,
        ]

        if (
            knowledge.validation_status
            == KnowledgeValidationStatus.UNVERIFIED
        ):
            actions.append(
                ConflictAction.REQUEST_VALIDATION
            )

        if (
            knowledge.knowledge_type
            == FarmerKnowledgeType.EVENT
        ):
            actions.append(
                ConflictAction.RECOMPUTE_STATE
            )

        if (
            knowledge.knowledge_type
            in {
                FarmerKnowledgeType.OBSERVATION,
                FarmerKnowledgeType.LOCAL_KNOWLEDGE,
            }
        ):
            actions.append(
                ConflictAction.BRANCH_SCENARIOS
            )

        return ConflictRecord(
            conflict_id=(
                f"CF-{uuid4().hex[:10].upper()}"
            ),

            conflict_type=(
                ConflictType.HUMAN_VS_MACHINE
            ),

            status=(
                ConflictStatus.VALIDATION_REQUIRED
                if (
                    knowledge.validation_status
                    == KnowledgeValidationStatus.UNVERIFIED
                )
                else ConflictStatus.OPEN
            ),

            left_item_id=evidence.evidence_id,
            right_item_id=knowledge.knowledge_id,

            variable=evidence.variable,

            spatial_overlap=True,
            temporal_overlap=True,

            description=(
                "Existe evidencia de máquina y "
                "conocimiento humano con alcance "
                "coincidente que deben preservarse "
                "y razonarse por separado."
            ),

            recommended_actions=actions,

            detected_at=datetime.now(),

            metadata={
                "machine_source_type":
                    evidence.provenance.source_type.value,

                "machine_source":
                    evidence.provenance.source_name,

                "farmer_knowledge_type":
                    knowledge.knowledge_type.value,

                "farmer_validation_status":
                    knowledge.validation_status.value,
            },
        )