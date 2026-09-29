from twin.biophysical import (
    BiophysicalScenarioResult,
)

from twin.evidence import (
    MachineEvidence,
)

from twin.farmer_knowledge import (
    FarmerKnowledgeItem,
)

from twin.experiment import (
    ExperimentCondition,
    ExperimentMode,
    ExperimentalRunResult,
)


class UntypedHumanBaseline:

    def run(
        self,
        scenarios: list[
            BiophysicalScenarioResult
        ],
        evidence: list[
            MachineEvidence
        ],
        farmer_knowledge: list[
            FarmerKnowledgeItem
        ],
        condition: ExperimentCondition,
    ) -> ExperimentalRunResult:

        # -------------------------------------------------
        # B1 representa deliberadamente un DT ingenuo:
        #
        # - recibe entradas humanas
        # - NO razona explícitamente según su tipo
        # - NO conserva conflictos formalmente
        # - puede convertir afirmaciones humanas en
        #   modificaciones directas del estado efectivo
        #
        # IMPORTANTE:
        # este comportamiento solo existe como baseline
        # experimental.
        # -------------------------------------------------

        feasible = list(
            scenarios
        )

        rejected = []

        applied_ids = []

        state_overrides = {}

        state_contamination = False

        water_saving_weight = 0.0

        # -------------------------------------------------
        # Interpretación ingenua de payloads
        # -------------------------------------------------

        for item in farmer_knowledge:

            payload = item.payload

            if not isinstance(
                payload,
                dict,
            ):
                continue

            # ---------------------------------------------
            # Restricción detectada solo por estructura
            # del payload, no por tipo epistemológico.
            # ---------------------------------------------

            if (
                "variable" in payload
                and "operator" in payload
                and "value" in payload
            ):

                if (
                    payload["variable"]
                    == "irrigation_mm"
                ):

                    operator = (
                        payload["operator"]
                    )

                    limit = float(
                        payload["value"]
                    )

                    next_feasible = []

                    for scenario in feasible:

                        value = float(
                            scenario.irrigation_mm
                        )

                        passed = (
                            self._compare(
                                value,
                                operator,
                                limit,
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

                    feasible = (
                        next_feasible
                    )

                    applied_ids.append(
                        item.knowledge_id
                    )

            # ---------------------------------------------
            # Preferencia detectada solo porque aparece
            # objective en payload.
            # ---------------------------------------------

            if (
                payload.get("objective")
                == "WATER_SAVING"
            ):

                water_saving_weight = float(
                    payload.get(
                        "weight",
                        1.0,
                    )
                )

                applied_ids.append(
                    item.knowledge_id
                )

            # ---------------------------------------------
            # EVENT humano:
            #
            # Baseline ingenuo:
            # transforma directamente el evento en una
            # propiedad del estado efectivo.
            #
            # Esto representa contaminación epistémica.
            # ---------------------------------------------

            if (
                payload.get("event_type")
                == "IRRIGATION"
                and "amount_mm" in payload
            ):

                state_overrides[
                    "last_irrigation_mm"
                ] = float(
                    payload["amount_mm"]
                )

                state_contamination = True

                applied_ids.append(
                    item.knowledge_id
                )

            # ---------------------------------------------
            # Hipótesis local:
            #
            # Baseline ingenuo la convierte en propiedad
            # del estado en vez de mantenerla como
            # hipótesis separada.
            # ---------------------------------------------

            if (
                "hypothesis" in payload
            ):

                state_overrides[
                    "local_hypothesis"
                ] = payload[
                    "hypothesis"
                ]

                state_contamination = True

                applied_ids.append(
                    item.knowledge_id
                )

        # -------------------------------------------------
        # Ranking ingenuo
        # -------------------------------------------------

        ranking_items = []

        for scenario in feasible:

            score = 0.0

            if (
                scenario.yield_ratio
                is not None
            ):

                score += (
                    scenario.yield_ratio
                    * 100.0
                )

            score -= (
                scenario.irrigation_mm
                * water_saving_weight
            )

            ranking_items.append(
                (
                    scenario,
                    score,
                )
            )

        ranking_items.sort(
            key=lambda item: item[1],
            reverse=True,
        )

        ranking = []

        for position, (
            scenario,
            score,
        ) in enumerate(
            ranking_items,
            start=1,
        ):

            ranking.append(
                {
                    "rank": position,

                    "irrigation_mm":
                        scenario.irrigation_mm,

                    "score":
                        score,

                    "reason":
                        "Untyped human-input ranking",
                }
            )

        recommendation = None

        if ranking_items:

            best_scenario, best_score = (
                ranking_items[0]
            )

            recommendation = {
                "irrigation_mm":
                    best_scenario
                    .irrigation_mm,

                "score":
                    best_score,

                "source":
                    ExperimentMode
                    .B1_UNTYPED_HUMAN
                    .value,
            }

        ignored_ids = [
            item.knowledge_id
            for item in farmer_knowledge
            if (
                item.knowledge_id
                not in applied_ids
            )
        ]

        return ExperimentalRunResult(
            mode=(
                ExperimentMode
                .B1_UNTYPED_HUMAN
            ),

            condition=condition,

            original_scenarios=list(
                scenarios
            ),

            feasible_scenarios=feasible,

            rejected_scenarios=rejected,

            ranking=ranking,

            recommendation=recommendation,

            conflicts=[],

            transformations=[],

            processed_knowledge_ids=[
                item.knowledge_id
                for item in farmer_knowledge
            ],

            applied_knowledge_ids=(
                list(
                    dict.fromkeys(
                        applied_ids
                    )
                )
            ),

            ignored_knowledge_ids=(
                ignored_ids
            ),

            epistemic_separation_preserved=(
                not state_contamination
            ),

            state_contamination_detected=(
                state_contamination
            ),

            metadata={
                "state_overrides":
                    state_overrides,

                "human_input_typed":
                    False,
            },
        )


    @staticmethod
    def _compare(
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

        return True