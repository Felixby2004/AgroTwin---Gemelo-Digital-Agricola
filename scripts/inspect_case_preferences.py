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

from twin.experiment import (
    ExperimentCondition,
)

from twin.farmer_knowledge import (
    FarmerKnowledgeType,
)


factory = ExperimentalCaseFactory()


conditions = [
    ExperimentCondition.COMPLETE,
    ExperimentCondition.MISSING_STALE,
    ExperimentCondition.CONFLICT,
]


print()
print("CASE PREFERENCES")
print("=" * 120)


for condition in conditions:

    case = factory.build(
        condition
    )

    print()
    print(
        "CONDITION:",
        condition.value,
    )

    for item in case.farmer_knowledge:

        if (
            item.knowledge_type
            == FarmerKnowledgeType.PREFERENCE
        ):

            print(
                "knowledge_id=",
                item.knowledge_id,
            )

            print(
                "type=",
                item.knowledge_type,
            )

            print(
                "validation_status=",
                item.validation_status,
            )

            print(
                "payload=",
                item.payload,
            )

            print(
                "confidence=",
                item.reported_confidence,
            )

            print("-" * 120)


print()
print("END")