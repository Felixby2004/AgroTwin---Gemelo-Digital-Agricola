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

from engines.multicriteria_recommendation_engine import (
    MultiCriteriaRecommendationEngine,
)

from twin.experiment import (
    ExperimentCondition,
)


factory = ExperimentalCaseFactory()

orchestrator = (
    ReasoningOrchestrator()
)

recommendation_engine = (
    MultiCriteriaRecommendationEngine()
)


conditions = [
    ExperimentCondition.COMPLETE,
    ExperimentCondition.MISSING_STALE,
    ExperimentCondition.CONFLICT,
]


print()
print(
    "MULTICRITERIA RECOMMENDATION TEST"
)

print("=" * 170)


for condition in conditions:

    case = factory.build(
        condition
    )


    reasoning = orchestrator.run(
        scenarios=case.scenarios,

        evidence=case.evidence,

        farmer_knowledge=(
            case.farmer_knowledge
        ),
    )


    soil_water = (
        reasoning
        .trusted_state
        .get(
            "soil_water_state"
        )
    )


    twin_confidence = (
        soil_water
        .confidence
        .confidence_score

        if soil_water is not None
        else None
    )


    recommendation = (
        recommendation_engine
        .recommend(
            scenarios=(
                reasoning
                .feasible_scenarios
            ),

            farmer_knowledge=(
                case.farmer_knowledge
            ),

            quality_gate=(
                reasoning
                .quality_gate
            ),

            twin_confidence=(
                twin_confidence
            ),
        )
    )


    print()
    print(
        "CONDITION:",
        condition.value
    )

    print(
        "STATUS:",
        recommendation.status.value
    )

    print(
        "ALLOWED:",
        recommendation
        .recommendation_allowed
    )


    if (
        recommendation
        .recommended_scenario
        is not None
    ):

        print(
            "RECOMMENDED IRRIGATION:",
            recommendation
            .recommended_scenario
            .irrigation_mm,
            "mm",
        )

    else:

        print(
            "RECOMMENDED IRRIGATION:",
            None,
        )


    print(
        "RANKING:"
    )


    for rank, item in enumerate(
        recommendation
        .ranked_scenarios,
        start=1,
    ):

        print(
            " ",
            rank,
            "| irrigation=",
            item.scenario
            .irrigation_mm,

            "| final=",
            round(
                item.final_score,
                4,
            ),

            "| agronomic=",
            round(
                item
                .agronomic_component,
                4,
            ),

            "| marginal=",
            round(
                item
                .marginal_component,
                4,
            ),

            "| preference=",
            round(
                item
                .preference_component,
                4,
            ),

            "| confidence=",
            round(
                item
                .confidence_factor,
                4,
            ),
        )


    print(
        "REASON:",
        recommendation.reason
    )

    print(
        "-" * 170
    )


print(
    "TOTAL CONDITIONS:",
    len(conditions),
)