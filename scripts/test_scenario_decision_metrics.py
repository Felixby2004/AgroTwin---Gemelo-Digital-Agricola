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

from engines.scenario_decision_metrics_engine import (
    ScenarioDecisionMetricsEngine,
)

from twin.experiment import (
    ExperimentCondition,
)


factory = ExperimentalCaseFactory()

engine = (
    ScenarioDecisionMetricsEngine()
)


case = factory.build(
    ExperimentCondition.COMPLETE
)


results = engine.calculate(
    case.scenarios
)


print()
print(
    "SCENARIO DECISION METRICS"
)

print("=" * 170)


for item in results:

    print(
        "irrigation=",
        item.irrigation_mm,

        "| yield_ratio=",
        round(
            item.yield_ratio,
            4,
        ),

        "| yield=",
        round(
            item.dry_yield_t_ha,
            4,
        ),

        "| yield_preservation=",
        round(
            item.yield_preservation_score,
            4,
        ),

        "| water_saving=",
        round(
            item.water_saving_score,
            4,
        ),

        "| irrigation_eff=",
        round(
            item.irrigation_efficiency_score,
            4,
        ),

        "| marginal_kg_ha_mm=",
        (
            round(
                item.marginal_gain_kg_ha_mm,
                3,
            )
            if item.marginal_gain_kg_ha_mm
            is not None
            else None
        ),

        "| agronomic_score=",
        round(
            item.agronomic_score,
            4,
        ),
    )


print("=" * 170)

print(
    "TOTAL SCENARIOS:",
    len(results),
)