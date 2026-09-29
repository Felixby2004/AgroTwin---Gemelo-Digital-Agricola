from datetime import (
    datetime,
    timezone,
)

from typing import Any


from database.repositories.parcel_repository import (
    ParcelRepository,
)

from database.repositories.evidence_repository import (
    EvidenceRepository,
)

from database.repositories.farmer_knowledge_repository import (
    FarmerKnowledgeRepository,
)

from database.repositories.decision_trace_repository import (
    DecisionTraceRepository,
)

from database.repositories.data_consent_repository import (
    DataConsentRepository,
)

from database.repositories.data_audit_repository import (
    DataAuditRepository,
)

from database.repositories.sensor_repository import (
    SensorRepository,
)

from database.adapters.decision_trace_adapter import (
    DecisionTraceAdapter,
)

from services.ml_prediction_service import (
    MLPredictionService,
)

from services.parcel_ml_forecast_service import (
    ParcelMLForecastService,
)


class ReportDataService:

    def build(
        self,
        *,
        db,
        parcel_id: str,
    ) -> dict[str, Any]:

        # =================================================
        # PARCEL
        # =================================================

        parcel_repo = ParcelRepository(
            db
        )

        parcel = (
            parcel_repo.get_by_id(
                parcel_id
            )
        )

        if parcel is None:

            raise ValueError(
                "Parcel not found."
            )


        geometry = (
            parcel_repo
            .get_geometry_geojson(
                parcel_id
            )
        )


        parcel_data = {
            "id":
                parcel.id,

            "name":
                parcel.name,

            "crop_type":
                parcel.crop_type,

            "area_ha":
                parcel.area_ha,

            "geometry":
                geometry,
        }


        # =================================================
        # MACHINE EVIDENCE
        # =================================================

        evidence_repo = (
            EvidenceRepository(
                db
            )
        )

        evidence_models = (
            evidence_repo
            .list_by_parcel(
                parcel_id
            )
        )


        evidence = []

        for item in evidence_models:

            evidence.append(
                {
                    "id":
                        item.id,

                    "variable":
                        item.variable,

                    "value":
                        item.value,

                    "unit":
                        item.unit,

                    "observed_at":
                        item.observed_at,

                    "status":
                        item.status,

                    "quality_score":
                        item.quality_score,

                    "uncertainty":
                        item.uncertainty,

                    "provenance":
                        (
                            item.provenance
                            or {}
                        ),

                    "metadata":
                        (
                            item.metadata_json
                            or {}
                        ),
                }
            )


        # =================================================
        # PHYSICAL SENSOR REGISTRY
        # =================================================

        sensor_repo = (
            SensorRepository(
                db
            )
        )

        sensor_models = (
            sensor_repo.list_by_parcel(
                parcel_id
            )
        )


        sensors = []

        for item in sensor_models:

            sensors.append(
                {
                    "id":
                        item.id,

                    "name":
                        item.name,

                    "sensor_type":
                        item.sensor_type,

                    "variables":
                        (
                            item.variables
                            or []
                        ),

                    "latitude":
                        item.latitude,

                    "longitude":
                        item.longitude,

                    "manufacturer":
                        item.manufacturer,

                    "model":
                        item.model_name,

                    "installed_at":
                        item.installed_at,

                    "is_active":
                        item.is_active,

                    "created_at":
                        item.created_at,

                    "updated_at":
                        item.updated_at,

                    "metadata":
                        (
                            item.metadata_json
                            or {}
                        ),
                }
            )


        # =================================================
        # FARMER KNOWLEDGE
        # =================================================

        knowledge_repo = (
            FarmerKnowledgeRepository(
                db
            )
        )

        knowledge_models = (
            knowledge_repo
            .list_by_parcel(
                parcel_id
            )
        )


        farmer_knowledge = []

        for item in knowledge_models:

            farmer_knowledge.append(
                {
                    "id":
                        item.id,

                    "knowledge_type":
                        item.knowledge_type,

                    "source_id":
                        item.source_id,

                    "source_role":
                        item.source_role,

                    "payload":
                        item.payload,

                    "validation_status":
                        item.validation_status,

                    "constraint_type":
                        item.constraint_type,

                    "affects":
                        (
                            item.affects
                            or []
                        ),

                    "rationale":
                        item.rationale,

                    "created_at":
                        item.created_at,

                    "valid_from":
                        getattr(
                            item,
                            "valid_from",
                            None,
                        ),

                    "valid_until":
                        getattr(
                            item,
                            "valid_until",
                            None,
                        ),

                    "reported_confidence":
                        getattr(
                            item,
                            "reported_confidence",
                            None,
                        ),

                    "metadata":
                        (
                            item.metadata_json
                            or {}
                        ),
                }
            )


        # =================================================
        # DECISION TRACES
        # =================================================

        trace_repo = (
            DecisionTraceRepository(
                db
            )
        )

        trace_models = (
            trace_repo.list_by_parcel(
                parcel_id
            )
        )


        decision_traces = [
            DecisionTraceAdapter
            .from_model(
                item
            )

            for item
            in trace_models
        ]


        latest_decision = (
            decision_traces[0]
            if decision_traces
            else None
        )


        # =================================================
        # COMPLEMENTARY RANDOM FOREST
        # =================================================
        #
        # IMPORTANT:
        # This block is intentionally non-blocking.
        #
        # A report must still be generated even if:
        # - the model is not trained,
        # - history is insufficient,
        # - forecast construction fails.
        #
        # Random Forest has no decision authority.
        # =================================================

        ml_service = (
            MLPredictionService()
        )

        ml_status = (
            ml_service.status()
        )


        ml_complementary = {
            "module":
                "Random Forest",

            "role":
                "COMPLEMENTARY_PREDICTION",

            "available":
                bool(
                    ml_status.get(
                        "available"
                    )
                ),

            "forecast_available":
                False,

            "model":
                ml_status.get(
                    "model"
                ),

            "model_status":
                ml_status.get(
                    "model_status"
                ),

            "purpose":
                ml_status.get(
                    "purpose"
                ),

            "target":
                ml_status.get(
                    "target"
                ),

            "prediction_horizon_hours":
                ml_status.get(
                    "prediction_horizon_hours"
                ),

            "provenance":
                ml_status.get(
                    "provenance"
                ),

            "decision_authority":
                False,

            "modifies_trusted_state":
                False,

            "modifies_recommendation":
                False,

            "forecast":
                None,

            "message":
                None,
        }


        if ml_complementary[
            "available"
        ]:

            try:

                forecast_service = (
                    ParcelMLForecastService(
                        db
                    )
                )

                forecast = (
                    forecast_service
                    .forecast(
                        parcel_id
                    )
                )


                ml_complementary[
                    "forecast"
                ] = forecast

                ml_complementary[
                    "forecast_available"
                ] = True


            except (
                FileNotFoundError,
                ValueError,
            ) as exc:

                ml_complementary[
                    "message"
                ] = str(
                    exc
                )


            except Exception:

                # ML is complementary.
                # Failure here must never prevent
                # the main operational report.
                ml_complementary[
                    "message"
                ] = (
                    "El pronóstico complementario "
                    "no está disponible para esta "
                    "parcela."
                )

        else:

            ml_complementary[
                "message"
            ] = (
                "El modelo Random Forest "
                "complementario no está disponible."
            )


        # =================================================
        # GOVERNANCE
        # =================================================

        consent_repo = (
            DataConsentRepository(
                db
            )
        )

        consents = (
            consent_repo.list_by_parcel(
                parcel_id
            )
        )


        active_consents = [
            item
            for item
            in consents
            if item.status == "ACTIVE"
        ]


        audit_repo = (
            DataAuditRepository(
                db
            )
        )

        audit_events = (
            audit_repo.list_by_parcel(
                parcel_id
            )
        )


        governance = {

            "consent_count":
                len(
                    consents
                ),

            "active_consent_count":
                len(
                    active_consents
                ),

            "audit_event_count":
                len(
                    audit_events
                ),

            "latest_audit_events": [
                {
                    "id":
                        item.id,

                    "actor_id":
                        item.actor_id,

                    "action":
                        item.action,

                    "allowed":
                        item.allowed,

                    "consent_id":
                        item.consent_id,

                    "purpose":
                        item.purpose,

                    "data_category":
                        item.data_category,

                    "created_at":
                        item.created_at,

                    "details":
                        (
                            item.details
                            or {}
                        ),
                }

                for item
                in audit_events[:10]
            ],
        }


        # =================================================
        # SUMMARY
        # =================================================

        active_evidence_count = sum(
            1
            for item
            in evidence
            if item["status"] == "ACTIVE"
        )


        stale_evidence_count = sum(
            1
            for item
            in evidence
            if item["status"] == "STALE"
        )


        active_sensor_count = sum(
            1
            for item
            in sensors
            if item["is_active"]
        )


        constraint_count = sum(
            1
            for item
            in farmer_knowledge
            if (
                item[
                    "knowledge_type"
                ]
                == "CONSTRAINT"
            )
        )


        hard_constraint_count = sum(
            1
            for item
            in farmer_knowledge
            if (
                item[
                    "knowledge_type"
                ]
                == "CONSTRAINT"
                and
                item[
                    "constraint_type"
                ]
                == "HARD"
            )
        )


        latest_conflict_count = 0
        latest_feasible_count = 0
        latest_rejected_count = 0


        if latest_decision:

            latest_conflict_count = len(
                latest_decision.get(
                    "conflict_ids",
                    [],
                )
            )

            latest_feasible_count = len(
                latest_decision.get(
                    "feasible_scenarios",
                    [],
                )
            )

            latest_rejected_count = len(
                latest_decision.get(
                    "rejected_scenarios",
                    [],
                )
            )


        summary = {

            "evidence_count":
                len(
                    evidence
                ),

            "active_evidence_count":
                active_evidence_count,

            "stale_evidence_count":
                stale_evidence_count,

            "sensor_count":
                len(
                    sensors
                ),

            "active_sensor_count":
                active_sensor_count,

            "farmer_knowledge_count":
                len(
                    farmer_knowledge
                ),

            "constraint_count":
                constraint_count,

            "hard_constraint_count":
                hard_constraint_count,

            "decision_trace_count":
                len(
                    decision_traces
                ),

            "latest_conflict_count":
                latest_conflict_count,

            "latest_feasible_scenario_count":
                latest_feasible_count,

            "latest_rejected_scenario_count":
                latest_rejected_count,

            "active_consent_count":
                len(
                    active_consents
                ),

            "ml_forecast_available":
                bool(
                    ml_complementary[
                        "forecast_available"
                    ]
                ),
        }


        # =================================================
        # FINAL REPORT PAYLOAD
        # =================================================

        return {

            "parcel_id":
                parcel_id,

            "generated_at":
                datetime.now(
                    timezone.utc
                ),

            "parcel":
                parcel_data,

            "summary":
                summary,

            "latest_decision":
                latest_decision,

            "evidence":
                evidence,

            "sensors":
                sensors,

            "farmer_knowledge":
                farmer_knowledge,

            "decision_traces":
                decision_traces,

            "ml_complementary":
                ml_complementary,

            "governance":
                governance,
        }