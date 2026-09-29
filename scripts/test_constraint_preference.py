import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent

if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from twin.biophysical import (
    BiophysicalScenarioResult,
)

from twin.farmer_knowledge import (
    FarmerKnowledgeItem,
    FarmerKnowledgeType,
    KnowledgeValidationStatus,
    ConstraintType,
)

from engines.constraint_engine import (
    ConstraintEngine,
)

from engines.preference_ranker import (
    PreferenceRanker,
)

from datetime import datetime


now = datetime.now()


scenarios = [
    BiophysicalScenarioResult(
        irrigation_mm=0.0,
        dry_yield_t_ha=12.1561769478,
        yield_potential_t_ha=14.7520783323,
        yield_ratio=0.8240314804,
        marginal_gain_kg_ha_mm=None,
    ),

    BiophysicalScenarioResult(
        irrigation_mm=20.0,
        dry_yield_t_ha=13.5498404859,
        yield_potential_t_ha=14.8639053170,
        yield_ratio=0.9115935682,
        marginal_gain_kg_ha_mm=69.6831769061,
    ),

    BiophysicalScenarioResult(
        irrigation_mm=40.0,
        dry_yield_t_ha=14.2478513387,
        yield_potential_t_ha=14.8724661707,
        yield_ratio=0.9580019329,
        marginal_gain_kg_ha_mm=34.9005426371,
    ),

    BiophysicalScenarioResult(
        irrigation_mm=60.0,
        dry_yield_t_ha=14.4807267528,
        yield_potential_t_ha=14.8750987956,
        yield_ratio=0.9734877698,
        marginal_gain_kg_ha_mm=11.6437707071,
    ),
]


constraint = FarmerKnowledgeItem(
    knowledge_id="FK-CON-001",
    knowledge_type=FarmerKnowledgeType.CONSTRAINT,

    source_id="farmer-001",
    source_role="FARMER",

    payload={
        "variable": "irrigation_mm",
        "operator": "<=",
        "value": 20.0,
        "unit": "mm",
    },

    created_at=now,

    validation_status=(
        KnowledgeValidationStatus.CONFIRMED
    ),

    constraint_type=ConstraintType.HARD,
)


preference = FarmerKnowledgeItem(
    knowledge_id="FK-PREF-001",
    knowledge_type=FarmerKnowledgeType.PREFERENCE,

    source_id="farmer-001",
    source_role="FARMER",

    payload={
        "objective": "WATER_SAVING",
        "weight": 0.8,
    },

    created_at=now,

    validation_status=(
        KnowledgeValidationStatus.CONFIRMED
    ),
)


constraint_engine = ConstraintEngine()

filtered = constraint_engine.apply(
    scenarios=scenarios,
    constraints=[constraint],
)


print()
print("FACTIBLES")
print("=" * 80)

for scenario in filtered.feasible_scenarios:
    print(
        scenario.irrigation_mm,
        "mm"
    )


print()
print("RECHAZADOS")
print("=" * 80)

for scenario in filtered.rejected_scenarios:
    print(
        scenario.irrigation_mm,
        "mm"
    )


ranker = PreferenceRanker()

ranking_result = ranker.rank(
    scenarios=filtered.feasible_scenarios,
    preferences=[preference],
)

ranking = (
    ranking_result.ranked_scenarios
)


print()
print("RANKING")
print("=" * 80)

for item in ranking:

    print(
        f"{item.scenario.irrigation_mm} mm"
        f" | score={item.score:.3f}"
        f" | {item.reasons}"
    )


print()
print("TRANSFORMACIONES")
print("=" * 100)

for transformation in (
    filtered.transformations
    +
    ranking_result.transformations
):

    print(
        transformation.transformation_type.value,
        "|",
        transformation.affected_scenario,
        "|",
        transformation.source_knowledge_id,
        "|",
        transformation.reason,
    )