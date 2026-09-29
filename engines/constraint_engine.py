from dataclasses import dataclass

from twin.biophysical import (
    BiophysicalScenarioResult,
)

from twin.farmer_knowledge import (
    FarmerKnowledgeItem,
    FarmerKnowledgeType,
    KnowledgeValidationStatus,
    ConstraintType,
)

from datetime import datetime
from uuid import uuid4

from twin.scenario_transformation import (
    ScenarioTransformation,
    TransformationType,
)


@dataclass
class ConstraintEvaluation:
    knowledge_id: str
    scenario_irrigation_mm: float
    feasible: bool
    reason: str


@dataclass
class ConstraintFilterResult:
    feasible_scenarios: list[BiophysicalScenarioResult]
    rejected_scenarios: list[BiophysicalScenarioResult]
    evaluations: list[ConstraintEvaluation]

    transformations: list[ScenarioTransformation]


class ConstraintEngine:

    SUPPORTED_OPERATORS = {
        "<=",
        "<",
        ">=",
        ">",
        "==",
    }

    def apply(
        self,
        scenarios: list[BiophysicalScenarioResult],
        constraints: list[FarmerKnowledgeItem],
    ) -> ConstraintFilterResult:

        feasible = list(scenarios)
        rejected = []
        evaluations = []
        transformations = []

        active_constraints = [
            item
            for item in constraints
            if (
                item.knowledge_type
                == FarmerKnowledgeType.CONSTRAINT
                and item.validation_status
                == KnowledgeValidationStatus.CONFIRMED
            )
        ]

        for constraint in active_constraints:

            payload = constraint.payload

            variable = payload.get("variable")
            operator = payload.get("operator")
            value = float(payload.get("value"))

            if variable != "irrigation_mm":
                continue

            if operator not in self.SUPPORTED_OPERATORS:
                raise ValueError(
                    f"Operador no soportado: {operator}"
                )

            next_feasible = []

            for scenario in feasible:

                scenario_value = float(
                    scenario.irrigation_mm
                )

                passed = self._evaluate(
                    scenario_value,
                    operator,
                    value,
                )

                evaluations.append(
                    ConstraintEvaluation(
                        knowledge_id=constraint.knowledge_id,
                        scenario_irrigation_mm=scenario_value,
                        feasible=passed,
                        reason=(
                            f"{scenario_value} {operator} {value}"
                        ),
                    )
                )

                if passed:
                    next_feasible.append(
                        scenario
                    )
                else:
                    rejected.append(
                        scenario
                    )

                    transformations.append(
                        ScenarioTransformation(
                            transformation_id=(
                                f"TR-{uuid4().hex[:10].upper()}"
                            ),

                            transformation_type=(
                                TransformationType.ACTION_REMOVED
                            ),

                            source_knowledge_id=(
                                constraint.knowledge_id
                            ),

                            affected_scenario=(
                                f"irrigation_{scenario_value}_mm"
                            ),

                            before_value={
                                "irrigation_mm": scenario_value,
                                "feasible": True,
                            },

                            after_value={
                                "irrigation_mm": scenario_value,
                                "feasible": False,
                            },

                            reason=(
                                f"Escenario eliminado por "
                                f"restricción "
                                f"{scenario_value} "
                                f"{operator} {value} = False"
                            ),

                            created_at=datetime.now(),

                            metadata={
                                "constraint_type": (
                                    constraint.constraint_type.value
                                    if constraint.constraint_type
                                    else None
                                ),
                                "variable": variable,
                                "operator": operator,
                                "limit": value,
                            },
                        )
                    )

            feasible = next_feasible

        return ConstraintFilterResult(
            feasible_scenarios=feasible,
            rejected_scenarios=rejected,
            evaluations=evaluations,
            transformations=transformations,
        )

    def _evaluate(
        self,
        left: float,
        operator: str,
        right: float,
    ) -> bool:

        if operator == "<=":
            return left <= right

        if operator == "<":
            return left < right

        if operator == ">=":
            return left >= right

        if operator == ">":
            return left > right

        if operator == "==":
            return left == right

        raise ValueError(
            f"Operador no soportado: {operator}"
        )