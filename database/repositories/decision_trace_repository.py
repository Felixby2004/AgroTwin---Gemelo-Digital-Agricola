from sqlalchemy.orm import Session

from database.models.decision import (
    DecisionTraceModel,
)


class DecisionTraceRepository:

    def __init__(
        self,
        session: Session,
    ):

        self.session = session


    def create(
        self,
        *,
        trace_id: str,
        parcel_id: str | None,
        created_at,
        evidence_ids: list,
        knowledge_ids: list,
        conflict_ids: list,
        transformation_ids: list,
        feasible_scenarios: list,
        rejected_scenarios: list,
        ranking: list,
        provisional_recommendation,
        farmer_response,
        outcome,
        metadata: dict | None = None,
    ) -> DecisionTraceModel:

        item = DecisionTraceModel(
            id=trace_id,
            parcel_id=parcel_id,
            created_at=created_at,
            evidence_ids=evidence_ids,
            knowledge_ids=knowledge_ids,
            conflict_ids=conflict_ids,
            transformation_ids=(
                transformation_ids
            ),
            feasible_scenarios=(
                feasible_scenarios
            ),
            rejected_scenarios=(
                rejected_scenarios
            ),
            ranking=ranking,
            provisional_recommendation=(
                provisional_recommendation
            ),
            farmer_response=farmer_response,
            outcome=outcome,
            metadata_json=metadata,
        )

        self.session.add(
            item
        )

        self.session.flush()

        return item


    def get_by_id(
        self,
        trace_id: str,
    ) -> DecisionTraceModel | None:

        return self.session.get(
            DecisionTraceModel,
            trace_id,
        )


    def list_by_parcel(
        self,
        parcel_id: str,
    ) -> list[
        DecisionTraceModel
    ]:

        return (
            self.session
            .query(
                DecisionTraceModel
            )
            .filter(
                DecisionTraceModel
                .parcel_id
                == parcel_id
            )
            .order_by(
                DecisionTraceModel
                .created_at
                .desc()
            )
            .all()
        )


    def update_from_trace(
        self,
        model: DecisionTraceModel,
        trace,
        final_action: dict | None = None,
    ) -> DecisionTraceModel:

        farmer_response = None

        if trace.farmer_response is not None:

            farmer_response = {
                "response_type":
                    trace.farmer_response
                    .response_type
                    .value,

                "modified_action":
                    trace.farmer_response
                    .modified_action,

                "rationale":
                    trace.farmer_response
                    .rationale,

                "responded_at":
                    (
                        trace.farmer_response
                        .responded_at
                        .isoformat()
                        if trace.farmer_response
                        .responded_at
                        is not None
                        else None
                    ),

                "metadata":
                    trace.farmer_response
                    .metadata,
            }


        metadata = dict(
            model.metadata_json
            or {}
        )

        metadata[
            "final_action"
        ] = final_action


        model.farmer_response = (
            farmer_response
        )

        model.metadata_json = (
            metadata
        )

        self.session.flush()

        return model