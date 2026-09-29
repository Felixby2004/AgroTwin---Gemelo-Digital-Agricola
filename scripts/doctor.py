import sys
from pathlib import Path


# =========================================================
# PROJECT ROOT
# =========================================================

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


# =========================================================
# STANDARD IMPORTS
# =========================================================

from sqlalchemy import (
    inspect,
    text,
)


# =========================================================
# DATABASE
# =========================================================

from database.session import (
    SessionLocal,
)


# =========================================================
# DOMAIN / ENGINE
# =========================================================

from experiments.case_factory import (
    ExperimentalCaseFactory,
)

from engines.reasoning_orchestrator import (
    ReasoningOrchestrator,
)

from engines.decision_trace_engine import (
    DecisionTraceEngine,
)

from engines.farmer_response_engine import (
    FarmerResponseEngine,
)


from twin.experiment import (
    ExperimentCondition,
)

from twin.decision_trace import (
    DecisionResponseType,
)


# =========================================================
# ADAPTERS
# =========================================================

from database.adapters import (
    EvidenceAdapter,
    FarmerKnowledgeAdapter,
    DecisionTraceAdapter,
)


# =========================================================
# API
# =========================================================

from api.main import (
    app,
)


# =========================================================
# CONFIG
# =========================================================

REQUIRED_TABLES = {
    "parcels",
    "machine_evidence",
    "farmer_knowledge",
    "decision_traces",
    "alembic_version",
}


REQUIRED_ROUTES = {
    "/",
    "/health",
    "/parcels",
    "/evidence",
    "/farmer-knowledge",
    "/reasoning/run",
    "/parcels/{parcel_id}/reasoning",
    "/decision-traces/{trace_id}",
    "/decision-traces/parcel/{parcel_id}",
    "/decision-traces/{trace_id}/response",
    "/parcels/{parcel_id}/state",
}


# =========================================================
# REPORT
# =========================================================

RESULTS = []


def check(
    name: str,
    fn,
):
    try:

        result = fn()

        RESULTS.append(
            (
                True,
                name,
                result,
            )
        )

        print(
            f"[PASS] {name}"
        )

        if result not in (
            None,
            True,
        ):
            print(
                f"       {result}"
            )

        return result

    except Exception as exc:

        RESULTS.append(
            (
                False,
                name,
                str(exc),
            )
        )

        print(
            f"[FAIL] {name}"
        )

        print(
            f"       {type(exc).__name__}: "
            f"{exc}"
        )

        return None


# =========================================================
# 1. DATABASE CONNECTION
# =========================================================

def check_database_connection():

    with SessionLocal() as session:

        version = session.execute(
            text(
                "SELECT version();"
            )
        ).scalar_one()

    if not version:
        raise RuntimeError(
            "PostgreSQL did not return a version."
        )

    return (
        version.split(",")[0]
    )


# =========================================================
# 2. POSTGIS
# =========================================================

def check_postgis():

    with SessionLocal() as session:

        version = session.execute(
            text(
                "SELECT PostGIS_Version();"
            )
        ).scalar_one()

    if not version:
        raise RuntimeError(
            "PostGIS is not available."
        )

    return (
        f"PostGIS {version}"
    )


# =========================================================
# 3. REQUIRED TABLES
# =========================================================

def check_database_tables():

    with SessionLocal() as session:

        bind = session.get_bind()

        inspector = inspect(
            bind
        )

        tables = set(
            inspector.get_table_names()
        )

    missing = (
        REQUIRED_TABLES
        - tables
    )

    if missing:
        raise RuntimeError(
            "Missing tables: "
            + ", ".join(
                sorted(
                    missing
                )
            )
        )

    return (
        f"{len(REQUIRED_TABLES)} "
        f"required tables found"
    )


# =========================================================
# 4. ALEMBIC VERSION
# =========================================================

def check_alembic_version():

    with SessionLocal() as session:

        version = session.execute(
            text(
                "SELECT version_num "
                "FROM alembic_version;"
            )
        ).scalar_one_or_none()

    if not version:
        raise RuntimeError(
            "No Alembic revision registered."
        )

    return version


# =========================================================
# 5. DOMAIN FACTORY
# =========================================================

factory = (
    ExperimentalCaseFactory()
)

orchestrator = (
    ReasoningOrchestrator()
)

trace_engine = (
    DecisionTraceEngine()
)

response_engine = (
    FarmerResponseEngine()
)


def build_case(
    condition,
):

    return factory.build(
        condition
    )


# =========================================================
# 6. COMPLETE CASE
# =========================================================

def check_complete_reasoning():

    case = build_case(
        ExperimentCondition.COMPLETE
    )

    reasoning = orchestrator.run(
        scenarios=case.scenarios,

        evidence=case.evidence,

        farmer_knowledge=(
            case.farmer_knowledge
        ),
    )

    if (
        reasoning
        .quality_gate
        .status
        .value
        != "READY"
    ):
        raise AssertionError(
            "COMPLETE must be READY."
        )

    if (
        reasoning
        .recommendation_allowed
        is not True
    ):
        raise AssertionError(
            "COMPLETE must allow "
            "recommendation."
        )

    recommendation = (
        reasoning
        .recommendation_result
    )

    if (
        recommendation
        .recommended_scenario
        is None
    ):
        raise AssertionError(
            "COMPLETE has no "
            "recommended scenario."
        )

    irrigation = (
        recommendation
        .recommended_scenario
        .irrigation_mm
    )

    if abs(
        irrigation - 20.0
    ) > 1e-9:
        raise AssertionError(
            f"Expected 20 mm, "
            f"received {irrigation}."
        )

    if (
        reasoning
        .decision_risk
        .risk_level
        .value
        != "LOW"
    ):
        raise AssertionError(
            "COMPLETE risk must be LOW."
        )

    return (
        "READY | "
        "recommendation=20 mm | "
        "risk=LOW"
    )


# =========================================================
# 7. MISSING / STALE CASE
# =========================================================

def check_missing_stale_reasoning():

    case = build_case(
        ExperimentCondition.MISSING_STALE
    )

    reasoning = orchestrator.run(
        scenarios=case.scenarios,

        evidence=case.evidence,

        farmer_knowledge=(
            case.farmer_knowledge
        ),
    )

    status = (
        reasoning
        .quality_gate
        .status
        .value
    )

    if status != "INSUFFICIENT_DATA":
        raise AssertionError(
            "MISSING_STALE must be "
            "INSUFFICIENT_DATA."
        )

    if (
        reasoning
        .recommendation_allowed
        is not False
    ):
        raise AssertionError(
            "MISSING_STALE must block "
            "recommendation."
        )

    if (
        reasoning
        .decision_risk
        .risk_level
        .value
        != "BLOCKED"
    ):
        raise AssertionError(
            "MISSING_STALE risk must "
            "be BLOCKED."
        )

    if (
        "soil_water_state"
        not in
        reasoning
        .update_required_variables
    ):
        raise AssertionError(
            "soil_water_state should "
            "require update."
        )

    return (
        "INSUFFICIENT_DATA | "
        "recommendation blocked"
    )


# =========================================================
# 8. CONFLICT CASE
# =========================================================

def check_conflict_reasoning():

    case = build_case(
        ExperimentCondition.CONFLICT
    )

    reasoning = orchestrator.run(
        scenarios=case.scenarios,

        evidence=case.evidence,

        farmer_knowledge=(
            case.farmer_knowledge
        ),
    )

    if len(
        reasoning.conflicts
    ) < 1:
        raise AssertionError(
            "CONFLICT case must produce "
            "at least one conflict."
        )

    if (
        reasoning
        .decision_risk
        .risk_level
        .value
        != "MODERATE"
    ):
        raise AssertionError(
            "CONFLICT risk must "
            "be MODERATE."
        )

    if (
        reasoning
        .decision_risk
        .requires_human_confirmation
        is not True
    ):
        raise AssertionError(
            "CONFLICT must require "
            "human confirmation."
        )

    return (
        f"conflicts="
        f"{len(reasoning.conflicts)} | "
        f"risk=MODERATE"
    )


# =========================================================
# 9. HARD CONSTRAINT
# =========================================================

def check_hard_constraint():

    case = build_case(
        ExperimentCondition.COMPLETE
    )

    reasoning = orchestrator.run(
        scenarios=case.scenarios,

        evidence=case.evidence,

        farmer_knowledge=(
            case.farmer_knowledge
        ),
    )

    trace = trace_engine.build_trace(
        reasoning_result=reasoning,

        evidence=case.evidence,

        farmer_knowledge=(
            case.farmer_knowledge
        ),

        parcel_id=(
            "DOCTOR-PARCEL"
        ),
    )


    # -----------------------------------------------------
    # VALID MODIFY = 10 mm
    # -----------------------------------------------------

    valid_trace = (
        response_engine
        .register_response(
            trace=trace,

            response_type=(
                DecisionResponseType.MODIFY
            ),

            modified_action={
                "irrigation_mm": 10.0
            },

            rationale=(
                "Doctor valid test."
            ),

            farmer_knowledge=(
                case.farmer_knowledge
            ),
        )
    )

    if (
        valid_trace
        .farmer_response
        .modified_action
        .get(
            "irrigation_mm"
        )
        != 10.0
    ):
        raise AssertionError(
            "10 mm MODIFY was not accepted."
        )


    # -----------------------------------------------------
    # INVALID MODIFY = 50 mm
    # -----------------------------------------------------

    case_2 = build_case(
        ExperimentCondition.COMPLETE
    )

    reasoning_2 = (
        orchestrator.run(
            scenarios=case_2.scenarios,

            evidence=case_2.evidence,

            farmer_knowledge=(
                case_2.farmer_knowledge
            ),
        )
    )

    trace_2 = (
        trace_engine.build_trace(
            reasoning_result=(
                reasoning_2
            ),

            evidence=case_2.evidence,

            farmer_knowledge=(
                case_2.farmer_knowledge
            ),

            parcel_id=(
                "DOCTOR-PARCEL"
            ),
        )
    )

    blocked = False

    try:

        response_engine.register_response(
            trace=trace_2,

            response_type=(
                DecisionResponseType.MODIFY
            ),

            modified_action={
                "irrigation_mm": 50.0
            },

            rationale=(
                "Doctor invalid test."
            ),

            farmer_knowledge=(
                case_2.farmer_knowledge
            ),
        )

    except ValueError as exc:

        blocked = True

        message = str(
            exc
        )

        if (
            "HARD"
            not in message
            and
            "FK-CON-001"
            not in message
        ):
            raise AssertionError(
                "50 mm was blocked, "
                "but not clearly by "
                "the HARD constraint."
            )


    if not blocked:

        raise AssertionError(
            "50 mm MODIFY should have "
            "been blocked."
        )

    return (
        "10 mm accepted | "
        "50 mm blocked by HARD constraint"
    )


# =========================================================
# 10. ADAPTERS
# =========================================================

def check_adapters():

    case = build_case(
        ExperimentCondition.COMPLETE
    )

    evidence_data = (
        EvidenceAdapter
        .to_model_dict(
            case.evidence[0],
            parcel_id=(
                "DOCTOR-PARCEL"
            ),
        )
    )

    if (
        evidence_data.get(
            "variable"
        )
        !=
        case.evidence[0].variable
    ):
        raise AssertionError(
            "EvidenceAdapter failed."
        )


    if case.farmer_knowledge:

        knowledge_data = (
            FarmerKnowledgeAdapter
            .to_model_dict(
                case
                .farmer_knowledge[0],

                parcel_id=(
                    "DOCTOR-PARCEL"
                ),
            )
        )

        if (
            knowledge_data.get(
                "knowledge_id"
            )
            !=
            case
            .farmer_knowledge[0]
            .knowledge_id
        ):
            raise AssertionError(
                "FarmerKnowledgeAdapter "
                "failed."
            )


    reasoning = orchestrator.run(
        scenarios=case.scenarios,

        evidence=case.evidence,

        farmer_knowledge=(
            case.farmer_knowledge
        ),
    )

    trace = trace_engine.build_trace(
        reasoning_result=reasoning,

        evidence=case.evidence,

        farmer_knowledge=(
            case.farmer_knowledge
        ),

        parcel_id=(
            "DOCTOR-PARCEL"
        ),
    )

    trace_data = (
        DecisionTraceAdapter
        .to_model_dict(
            trace
        )
    )

    if (
        trace_data.get(
            "trace_id"
        )
        != trace.trace_id
    ):
        raise AssertionError(
            "DecisionTraceAdapter failed."
        )

    return (
        "Evidence + Knowledge + "
        "DecisionTrace adapters OK"
    )


# =========================================================
# 11. FASTAPI ROUTES
# =========================================================

def check_api_routes():

    openapi_schema = (
        app.openapi()
    )

    available_routes = set(
        openapi_schema
        .get(
            "paths",
            {},
        )
        .keys()
    )

    missing = (
        REQUIRED_ROUTES
        - available_routes
    )

    if missing:

        raise RuntimeError(
            "Missing API routes: "
            + ", ".join(
                sorted(
                    missing
                )
            )
        )

    return (
        f"{len(REQUIRED_ROUTES)} "
        f"required routes found"
    )

# =========================================================
# MAIN
# =========================================================

def main():

    print()
    print(
        "=" * 100
    )

    print(
        "AGRICULTURAL DIGITAL TWIN "
        "— SYSTEM DOCTOR"
    )

    print(
        "=" * 100
    )

    print()


    check(
        "PostgreSQL connection",
        check_database_connection,
    )

    check(
        "PostGIS extension",
        check_postgis,
    )

    check(
        "Database schema",
        check_database_tables,
    )

    check(
        "Alembic revision",
        check_alembic_version,
    )

    check(
        "Reasoning COMPLETE",
        check_complete_reasoning,
    )

    check(
        "Reasoning MISSING_STALE",
        check_missing_stale_reasoning,
    )

    check(
        "Reasoning CONFLICT",
        check_conflict_reasoning,
    )

    check(
        "Human-in-the-loop "
        "HARD constraint",
        check_hard_constraint,
    )

    check(
        "Domain/database adapters",
        check_adapters,
    )

    check(
        "FastAPI routes",
        check_api_routes,
    )


    # =====================================================
    # SUMMARY
    # =====================================================

    passed = sum(
        1
        for success, _, _
        in RESULTS
        if success
    )

    failed = (
        len(RESULTS)
        - passed
    )


    print()

    print(
        "-" * 100
    )

    print(
        f"PASSED: {passed}"
    )

    print(
        f"FAILED: {failed}"
    )

    print(
        "-" * 100
    )


    if failed == 0:

        print(
            "SYSTEM STATUS: HEALTHY"
        )

        print(
            "=" * 100
        )

        sys.exit(
            0
        )


    print(
        "SYSTEM STATUS: ATTENTION REQUIRED"
    )

    print()

    print(
        "FAILED CHECKS:"
    )


    for success, name, detail in RESULTS:

        if not success:

            print(
                f" - {name}: "
                f"{detail}"
            )


    print(
        "=" * 100
    )

    sys.exit(
        1
    )


if __name__ == "__main__":
    main()