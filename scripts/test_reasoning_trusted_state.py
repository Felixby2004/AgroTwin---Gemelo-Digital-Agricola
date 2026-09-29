import sys
from pathlib import Path
from datetime import datetime, timedelta


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

from twin.experiment import (
    ExperimentCondition,
)


factory = ExperimentalCaseFactory()

orchestrator = (
    ReasoningOrchestrator()
)


# =====================================================
# UTILIDAD DE IMPRESIÓN
# =====================================================

def print_case(
    condition,
):

    case = factory.build(
        condition
    )

    result = orchestrator.run(
        scenarios=case.scenarios,
        evidence=case.evidence,
        farmer_knowledge=(
            case.farmer_knowledge
        ),
    )

    print()
    print(
        "=" * 150
    )

    print(
        "CONDITION:",
        condition.value,
    )

    print(
        "OPERATIONAL EVIDENCE:",
        result.operational_evidence_ids,
    )

    print(
        "EXCLUDED EVIDENCE:",
        result.excluded_evidence_ids,
    )

    print(
        "UPDATE REQUIRED:",
        result.update_required_variables,
    )

    print(
        "CONFLICTS:",
        len(
            result.conflicts
        ),
    )

    print(
        "TRUSTED STATE:"
    )

    for variable, state_variable in (
        result.trusted_state
        .variables
        .items()
    ):

        print(
            " ",
            variable,
            "| value=",
            state_variable.value,
            "| selected=",
            state_variable.metadata.get(
                "selected_evidence_id"
            ),
            "| confidence=",
            state_variable
            .confidence
            .confidence_score,
            "| uncertainty=",
            state_variable
            .confidence
            .uncertainty_level
            .value,
            "| update=",
            state_variable
            .confidence
            .requires_update,
        )


# =====================================================
# EJECUTAR CASOS
# =====================================================

print()
print(
    "REASONING + TRUSTED STATE TEST"
)


print_case(
    ExperimentCondition.COMPLETE
)

print_case(
    ExperimentCondition.MISSING_STALE
)

print_case(
    ExperimentCondition.CONFLICT
)


print()
print(
    "=" * 150
)

print(
    "TOTAL CONDITIONS: 3"
)