from datetime import datetime

from twin.decision_trace import (
    HumanTwinDecisionTrace,
    DecisionResponse,
    DecisionResponseType,
)

from twin.farmer_knowledge import (
    FarmerKnowledgeItem,
    FarmerKnowledgeType,
    KnowledgeValidationStatus,
    ConstraintType,
)


class FarmerResponseEngine:

    def register_response(
        self,
        trace: HumanTwinDecisionTrace,
        response_type: DecisionResponseType,
        modified_action: dict | None = None,
        rationale: str | None = None,
        farmer_knowledge: list[
            FarmerKnowledgeItem
        ] | None = None,

    ) -> HumanTwinDecisionTrace:

        # -------------------------------------------------
        # Validaciones generales
        # -------------------------------------------------

        if trace.provisional_recommendation is None:
            raise ValueError(
                "No existe una recomendación provisional "
                "sobre la cual registrar respuesta."
            )

        # -------------------------------------------------
        # ACCEPT
        # -------------------------------------------------

        if response_type == DecisionResponseType.ACCEPT:

            if modified_action is not None:
                raise ValueError(
                    "ACCEPT no debe incluir modified_action."
                )

            response = DecisionResponse(
                response_type=(
                    DecisionResponseType.ACCEPT
                ),

                responded_at=datetime.now(),

                modified_action=None,

                rationale=rationale,

                metadata={
                    "accepted_recommendation": (
                        trace.provisional_recommendation
                    )
                },
            )

        # -------------------------------------------------
        # MODIFY
        # -------------------------------------------------

        elif response_type == DecisionResponseType.MODIFY:

            if modified_action is None:
                raise ValueError(
                    "MODIFY requiere modified_action."
                )

            if farmer_knowledge:

                self._validate_modified_action(
                    modified_action=modified_action,
                    farmer_knowledge=farmer_knowledge,
                )

            response = DecisionResponse(
                response_type=(
                    DecisionResponseType.MODIFY
                ),

                responded_at=datetime.now(),

                modified_action=(
                    modified_action
                ),

                rationale=rationale,

                metadata={
                    "original_recommendation": (
                        trace.provisional_recommendation
                    )
                },
            )

        # -------------------------------------------------
        # REJECT
        # -------------------------------------------------

        elif response_type == DecisionResponseType.REJECT:

            if modified_action is not None:
                raise ValueError(
                    "REJECT no debe incluir modified_action."
                )

            response = DecisionResponse(
                response_type=(
                    DecisionResponseType.REJECT
                ),

                responded_at=datetime.now(),

                modified_action=None,

                rationale=rationale,

                metadata={
                    "rejected_recommendation": (
                        trace.provisional_recommendation
                    )
                },
            )

        else:
            raise ValueError(
                f"Tipo de respuesta no soportado: "
                f"{response_type}"
            )

        # -------------------------------------------------
        # Registrar respuesta dentro del trace
        # -------------------------------------------------

        trace.farmer_response = response

        return trace


    def _validate_modified_action(
        self,
        modified_action: dict,
        farmer_knowledge: list[
            FarmerKnowledgeItem
        ],
    ) -> None:

        hard_constraints = [
            item
            for item in farmer_knowledge
            if (
                item.knowledge_type
                == FarmerKnowledgeType.CONSTRAINT
                and
                item.validation_status
                == KnowledgeValidationStatus.CONFIRMED
                and
                item.constraint_type
                == ConstraintType.HARD
            )
        ]

        for constraint in hard_constraints:

            payload = (
                constraint.payload
                or {}
            )

            variable = payload.get(
                "variable"
            )

            operator = payload.get(
                "operator"
            )

            limit = payload.get(
                "value"
            )

            if (
                variable is None
                or operator is None
                or limit is None
            ):
                continue

            if variable not in modified_action:
                continue

            actual = (
                modified_action[
                    variable
                ]
            )

            if self._violates(
                actual=actual,
                operator=operator,
                limit=limit,
            ):

                raise ValueError(
                    (
                        "Modified action violates "
                        f"HARD constraint "
                        f"{constraint.knowledge_id}: "
                        f"{variable} {operator} {limit}. "
                        f"Received: {actual}."
                    )
                )


    def _violates(
        self,
        actual,
        operator,
        limit,
    ) -> bool:

        if operator == "<=":
            return not (
                actual <= limit
            )

        if operator == "<":
            return not (
                actual < limit
            )

        if operator == ">=":
            return not (
                actual >= limit
            )

        if operator == ">":
            return not (
                actual > limit
            )

        if operator == "==":
            return not (
                actual == limit
            )

        raise ValueError(
            f"Unsupported constraint operator: {operator}"
        )