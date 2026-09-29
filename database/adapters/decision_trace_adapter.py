from datetime import datetime

from twin.decision_trace import (
    DecisionResponse,
    DecisionResponseType,
    HumanTwinDecisionTrace,
)

from database.models.decision import (
    DecisionTraceModel,
)


class DecisionTraceAdapter:

    @staticmethod
    def to_model_dict(
        trace: HumanTwinDecisionTrace,
    ) -> dict:

        farmer_response = None


        if (
            trace.farmer_response
            is not None
        ):

            farmer_response = {

                "response_type":
                    trace
                    .farmer_response
                    .response_type
                    .value,

                "modified_action":
                    trace
                    .farmer_response
                    .modified_action,

                "rationale":
                    trace
                    .farmer_response
                    .rationale,

                "responded_at":
                    (
                        trace
                        .farmer_response
                        .responded_at
                        .isoformat()

                        if trace
                        .farmer_response
                        .responded_at
                        is not None

                        else None
                    ),

                "metadata":
                    trace
                    .farmer_response
                    .metadata,
            }


        metadata = dict(
            trace.metadata
            or {}
        )


        if hasattr(
            trace,
            "final_action",
        ):

            metadata[
                "final_action"
            ] = (
                trace.final_action
            )


        return {

            "trace_id":
                trace.trace_id,

            "parcel_id":
                trace.parcel_id,

            "created_at":
                trace.created_at,

            "evidence_ids":
                trace.evidence_ids,

            "knowledge_ids":
                trace.knowledge_ids,

            "conflict_ids":
                trace.conflict_ids,

            "transformation_ids":
                trace.transformation_ids,

            "feasible_scenarios":
                trace.feasible_scenarios,

            "rejected_scenarios":
                trace.rejected_scenarios,

            "ranking":
                trace.ranking,

            "provisional_recommendation":
                trace
                .provisional_recommendation,

            "farmer_response":
                farmer_response,

            "outcome":
                trace.outcome,

            "metadata":
                metadata,
        }


    # ==================================================
    # DATABASE -> DOMAIN
    # ==================================================

    @staticmethod
    def to_domain(
        model: DecisionTraceModel,
    ) -> HumanTwinDecisionTrace:

        farmer_response = None


        if model.farmer_response:

            response_data = (
                model.farmer_response
            )


            response_type_raw = (
                response_data.get(
                    "response_type"
                )
            )


            if response_type_raw:

                responded_at_raw = (
                    response_data.get(
                        "responded_at"
                    )
                )


                responded_at = None


                if responded_at_raw:

                    if isinstance(
                        responded_at_raw,
                        datetime,
                    ):

                        responded_at = (
                            responded_at_raw
                        )

                    else:

                        responded_at = (
                            datetime
                            .fromisoformat(
                                responded_at_raw
                            )
                        )


                farmer_response = (
                    DecisionResponse(
                        response_type=(
                            DecisionResponseType(
                                response_type_raw
                            )
                        ),

                        responded_at=(
                            responded_at
                        ),

                        modified_action=(
                            response_data.get(
                                "modified_action"
                            )
                        ),

                        rationale=(
                            response_data.get(
                                "rationale"
                            )
                        ),

                        metadata=(
                            response_data.get(
                                "metadata"
                            )
                        ),
                    )
                )


        return HumanTwinDecisionTrace(

            trace_id=
                model.id,

            parcel_id=
                model.parcel_id,

            created_at=
                model.created_at,

            evidence_ids=(
                model.evidence_ids
                or []
            ),

            knowledge_ids=(
                model.knowledge_ids
                or []
            ),

            conflict_ids=(
                model.conflict_ids
                or []
            ),

            transformation_ids=(
                model.transformation_ids
                or []
            ),

            feasible_scenarios=(
                model.feasible_scenarios
                or []
            ),

            rejected_scenarios=(
                model.rejected_scenarios
                or []
            ),

            ranking=(
                model.ranking
                or []
            ),

            provisional_recommendation=(
                model
                .provisional_recommendation
            ),

            farmer_response=(
                farmer_response
            ),

            outcome=(
                model.outcome
            ),

            metadata=(
                model.metadata_json
                or {}
            ),
        )


    # ==================================================
    # DATABASE -> API
    # ==================================================

    @staticmethod
    def from_model(
        model: DecisionTraceModel,
    ) -> dict:

        metadata = (
            model.metadata_json
            or {}
        )


        return {

            "trace_id":
                model.id,

            "parcel_id":
                model.parcel_id,

            "created_at":
                model.created_at,

            "evidence_ids":
                model.evidence_ids
                or [],

            "knowledge_ids":
                model.knowledge_ids
                or [],

            "conflict_ids":
                model.conflict_ids
                or [],

            "transformation_ids":
                model.transformation_ids
                or [],

            "feasible_scenarios":
                model.feasible_scenarios
                or [],

            "rejected_scenarios":
                model.rejected_scenarios
                or [],

            "ranking":
                model.ranking
                or [],

            "provisional_recommendation":
                model
                .provisional_recommendation,

            "farmer_response":
                model.farmer_response,

            "final_action":
                metadata.get(
                    "final_action"
                ),

            "outcome":
                model.outcome,

            "metadata":
                metadata,
        }