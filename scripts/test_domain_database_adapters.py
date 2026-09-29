import sys
from pathlib import Path


ROOT_DIR = (
    Path(__file__)
    .resolve()
    .parent
    .parent
)

if str(ROOT_DIR) not in sys.path:
    sys.path.insert(
        0,
        str(ROOT_DIR),
    )


from experiments.case_factory import (
    ExperimentalCaseFactory,
)

from engines.reasoning_orchestrator import (
    ReasoningOrchestrator,
)

from engines.decision_trace_engine import (
    DecisionTraceEngine,
)

from database.session import (
    SessionLocal,
)

from database.repositories import (
    ParcelRepository,
    EvidenceRepository,
    FarmerKnowledgeRepository,
    DecisionTraceRepository,
)

from database.adapters import (
    EvidenceAdapter,
    FarmerKnowledgeAdapter,
    DecisionTraceAdapter,
)

from twin.experiment import (
    ExperimentCondition,
)


factory = ExperimentalCaseFactory()

orchestrator = ReasoningOrchestrator()

trace_engine = DecisionTraceEngine()


case = factory.build(
    ExperimentCondition.COMPLETE
)


reasoning = orchestrator.run(
    scenarios=case.scenarios,
    evidence=case.evidence,
    farmer_knowledge=(
        case.farmer_knowledge
    ),
)


with SessionLocal() as session:

    parcel_repo = ParcelRepository(
        session
    )

    evidence_repo = EvidenceRepository(
        session
    )

    knowledge_repo = (
        FarmerKnowledgeRepository(
            session
        )
    )

    trace_repo = (
        DecisionTraceRepository(
            session
        )
    )


    parcel = parcel_repo.create(
        name="Adapter Test Parcel",
        crop_type="Maize",
        area_ha=2.0,
    )


    # =====================================================
    # EVIDENCE DOMAIN → DB
    # =====================================================

    evidence = case.evidence[0]

    evidence_data = (
        EvidenceAdapter
        .to_model_dict(
            evidence,
            parcel_id=parcel.id,
        )
    )

    evidence_model = (
        evidence_repo.create(
            **evidence_data
        )
    )


    # =====================================================
    # FARMER KNOWLEDGE DOMAIN → DB
    # =====================================================

    knowledge_models = []

    for item in (
        case.farmer_knowledge
    ):

        data = (
            FarmerKnowledgeAdapter
            .to_model_dict(
                item,
                parcel_id=parcel.id,
            )
        )

        model = (
            knowledge_repo.create(
                **data
            )
        )

        knowledge_models.append(
            model
        )


    # =====================================================
    # DECISION TRACE DOMAIN → DB
    # =====================================================

    trace = trace_engine.build_trace(
        reasoning_result=reasoning,
        evidence=case.evidence,
        farmer_knowledge=(
            case.farmer_knowledge
        ),
        parcel_id=parcel.id,
    )


    trace_data = (
        DecisionTraceAdapter
        .to_model_dict(
            trace
        )
    )


    trace_model = (
        trace_repo.create(
            **trace_data
        )
    )


    session.commit()


    # =====================================================
    # DB → DOMAIN
    # =====================================================

    restored_evidence = (
        EvidenceAdapter.from_model(
            evidence_model
        )
    )


    restored_knowledge = (
        FarmerKnowledgeAdapter
        .from_model(
            knowledge_models[0]
        )
    )


    restored_trace = (
        DecisionTraceAdapter
        .from_model(
            trace_model
        )
    )


    print()
    print(
        "DOMAIN <-> DATABASE ADAPTER TEST"
    )

    print("=" * 120)

    print(
        "EVIDENCE:",
        restored_evidence
        .evidence_id,
        restored_evidence
        .variable,
    )

    print(
        "KNOWLEDGE:",
        restored_knowledge
        .knowledge_id,
        restored_knowledge
        .knowledge_type
        .value,
    )

    print(
        "TRACE:",
        restored_trace[
            "trace_id"
        ],
    )

    print(
        "TRACE RECOMMENDATION:",
        restored_trace[
            "provisional_recommendation"
        ],
    )

    print("=" * 120)

    print(
        "DOMAIN <-> DATABASE ADAPTER TEST: OK"
    )