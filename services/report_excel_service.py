from io import BytesIO
import json

from openpyxl import Workbook

from openpyxl.styles import (
    Font,
    Alignment,
)

from openpyxl.utils import (
    get_column_letter,
)


class ReportExcelService:

    @staticmethod
    def _value(
        value,
    ):

        if value is None:
            return None


        # Native Excel scalar values
        if isinstance(
            value,
            (
                str,
                int,
                float,
                bool,
            ),
        ):
            return value


        # Datetime / date-like objects
        if hasattr(
            value,
            "isoformat",
        ):

            try:

                return (
                    value.isoformat()
                )

            except Exception:
                pass


        # Structured values must be serialized
        if isinstance(
            value,
            (
                dict,
                list,
                tuple,
                set,
            ),
        ):

            try:

                serializable_value = (
                    list(value)
                    if isinstance(
                        value,
                        set,
                    )
                    else value
                )


                return json.dumps(
                    serializable_value,
                    ensure_ascii=False,
                    default=str,
                )

            except Exception:

                return str(
                    value
                )


        # Enum-like objects
        if hasattr(
            value,
            "value",
        ):

            try:

                enum_value = (
                    value.value
                )

                if isinstance(
                    enum_value,
                    (
                        str,
                        int,
                        float,
                        bool,
                    ),
                ):
                    return enum_value

                return str(
                    enum_value
                )

            except Exception:
                pass


        # Final safety net:
        # openpyxl must never receive arbitrary objects.
        return str(
            value
        )

    @staticmethod
    def _origin(
        item: dict,
    ) -> str:

        metadata = (
            item.get(
                "metadata"
            )
            or {}
        )

        provenance = (
            item.get(
                "provenance"
            )
            or {}
        )


        if metadata.get(
            "data_origin"
        ):

            return str(
                metadata[
                    "data_origin"
                ]
            )


        if metadata.get(
            "ingestion_type"
        ):

            return str(
                metadata[
                    "ingestion_type"
                ]
            )


        if provenance.get(
            "source_name"
        ):

            return str(
                provenance[
                    "source_name"
                ]
            )


        if provenance.get(
            "source_type"
        ):

            return str(
                provenance[
                    "source_type"
                ]
            )


        return "-"


    @staticmethod
    def _configure_sheet(
        sheet,
        freeze_panes: str = "A2",
    ) -> None:

        sheet.freeze_panes = (
            freeze_panes
        )

        sheet.auto_filter.ref = (
            sheet.dimensions
        )


        for cell in (
            sheet[1]
        ):

            cell.font = Font(
                bold=True
            )

            cell.alignment = (
                Alignment(
                    vertical="top",
                )
            )


        for row in (
            sheet.iter_rows()
        ):

            for cell in row:

                cell.alignment = (
                    Alignment(
                        vertical="top",
                        wrap_text=True,
                    )
                )


        for column_cells in (
            sheet.columns
        ):

            max_length = 0

            column_index = (
                column_cells[
                    0
                ].column
            )


            for cell in (
                column_cells
            ):

                value = (
                    ""
                    if cell.value
                    is None
                    else str(
                        cell.value
                    )
                )

                max_length = max(
                    max_length,
                    min(
                        len(
                            value
                        ),
                        60,
                    ),
                )


            sheet.column_dimensions[
                get_column_letter(
                    column_index
                )
            ].width = max(
                12,
                min(
                    max_length + 2,
                    60,
                ),
            )


    def generate(
        self,
        report: dict,
    ) -> bytes:

        workbook = (
            Workbook()
        )


        workbook.remove(
            workbook.active
        )


        parcel = (
            report.get(
                "parcel",
                {},
            )
        )


        # =================================================
        # RESUMEN
        # =================================================

        sheet = (
            workbook.create_sheet(
                "Resumen"
            )
        )


        sheet.append(
            [
                "Campo",
                "Valor",
            ]
        )


        values = {

            "parcel_id":
                parcel.get(
                    "id"
                ),

            "name":
                parcel.get(
                    "name"
                ),

            "crop_type":
                parcel.get(
                    "crop_type"
                ),

            "area_ha":
                parcel.get(
                    "area_ha"
                ),

            "generated_at":
                report.get(
                    "generated_at"
                ),
        }


        values.update(
            report.get(
                "summary",
                {},
            )
        )


        for key, value in (
            values.items()
        ):

            sheet.append(
                [
                    key,
                    self._value(
                        value
                    ),
                ]
            )


        self._configure_sheet(
            sheet
        )


        # =================================================
        # EVIDENCIA
        # =================================================

        sheet = (
            workbook.create_sheet(
                "Evidencia"
            )
        )


        headers = [
            "id",
            "variable",
            "value",
            "unit",
            "observed_at",
            "status",
            "quality_score",
            "uncertainty",
            "origin",
            "provenance",
            "metadata",
        ]


        sheet.append(
            headers
        )


        for item in (
            report.get(
                "evidence",
                [],
            )
        ):

            row_values = [

                item.get(
                    "id"
                ),

                item.get(
                    "variable"
                ),

                item.get(
                    "value"
                ),

                item.get(
                    "unit"
                ),

                item.get(
                    "observed_at"
                ),

                item.get(
                    "status"
                ),

                item.get(
                    "quality_score"
                ),

                item.get(
                    "uncertainty"
                ),

                self._origin(
                    item
                ),

                item.get(
                    "provenance"
                ),

                item.get(
                    "metadata"
                ),
            ]


            sheet.append(
                [
                    self._value(
                        value
                    )
                    for value
                    in row_values
                ]
            )

        self._configure_sheet(
            sheet
        )


        # =================================================
        # CONOCIMIENTO
        # =================================================

        sheet = (
            workbook.create_sheet(
                "Conocimiento"
            )
        )


        headers = [
            "id",
            "knowledge_type",
            "source_id",
            "source_role",
            "payload",
            "validation_status",
            "constraint_type",
            "affects",
            "rationale",
            "created_at",
            "valid_from",
            "valid_until",
            "reported_confidence",
            "metadata",
        ]


        sheet.append(
            headers
        )


        for item in (
            report.get(
                "farmer_knowledge",
                [],
            )
        ):

            sheet.append(
                [
                    self._value(
                        item.get(
                            header
                        )
                    )

                    for header
                    in headers
                ]
            )


        self._configure_sheet(
            sheet
        )


        # =================================================
        # DECISIONES
        # =================================================

        sheet = (
            workbook.create_sheet(
                "Decisiones"
            )
        )


        headers = [
            "trace_id",
            "created_at",
            "recommended_irrigation_mm",
            "recommendation_score",
            "recommendation_status",
            "recommendation_source",
            "farmer_response",
            "final_action",
            "feasible_scenario_count",
            "rejected_scenario_count",
            "conflict_count",
        ]


        sheet.append(
            headers
        )


        for trace in (
            report.get(
                "decision_traces",
                [],
            )
        ):

            recommendation = (
                trace.get(
                    "provisional_recommendation"
                )
                or {}
            )

            farmer_response = (
                trace.get(
                    "farmer_response"
                )
                or {}
            )


            sheet.append(
                [
                    trace.get(
                        "trace_id"
                    ),

                    self._value(
                        trace.get(
                            "created_at"
                        )
                    ),

                    recommendation.get(
                        "irrigation_mm"
                    ),

                    recommendation.get(
                        "score"
                    ),

                    recommendation.get(
                        "status"
                    ),

                    self._value(
                        recommendation.get(
                            "source"
                        )
                    ),

                    farmer_response.get(
                        "response_type"
                    ),

                    self._value(
                        trace.get(
                            "final_action"
                        )
                    ),

                    len(
                        trace.get(
                            "feasible_scenarios",
                            [],
                        )
                    ),

                    len(
                        trace.get(
                            "rejected_scenarios",
                            [],
                        )
                    ),

                    len(
                        trace.get(
                            "conflict_ids",
                            [],
                        )
                    ),
                ]
            )


        self._configure_sheet(
            sheet
        )


        # =================================================
        # GOBERNANZA
        # =================================================

        governance = (
            report.get(
                "governance",
                {},
            )
        )


        sheet = (
            workbook.create_sheet(
                "Gobernanza"
            )
        )


        sheet.append(
            [
                "Indicador",
                "Valor",
            ]
        )


        governance_values = {

            "consent_count":
                governance.get(
                    "consent_count"
                ),

            "active_consent_count":
                governance.get(
                    "active_consent_count"
                ),

            "audit_event_count":
                governance.get(
                    "audit_event_count"
                ),
        }


        for key, value in (
            governance_values.items()
        ):

            sheet.append(
                [
                    key,
                    self._value(
                        value
                    ),
                ]
            )


        self._configure_sheet(
            sheet
        )


        # =================================================
        # AUDITORIA
        # =================================================

        sheet = (
            workbook.create_sheet(
                "Auditoria"
            )
        )


        headers = [
            "id",
            "created_at",
            "actor_id",
            "action",
            "allowed",
            "consent_id",
            "purpose",
            "data_category",
            "details",
        ]


        sheet.append(
            headers
        )


        for item in (
            governance.get(
                "latest_audit_events",
                [],
            )
        ):

            sheet.append(
                [
                    self._value(
                        item.get(
                            header
                        )
                    )

                    for header
                    in headers
                ]
            )


        self._configure_sheet(
            sheet
        )


        # =================================================
        # SENSORES
        # =================================================

        sheet = workbook.create_sheet(
            "Sensores"
        )

        headers = [
            "id",
            "name",
            "sensor_type",
            "variables",
            "latitude",
            "longitude",
            "manufacturer",
            "model",
            "installed_at",
            "is_active",
            "metadata",
        ]

        sheet.append(
            headers
        )


        for item in report.get(
            "sensors",
            [],
        ):

            sheet.append(
                [
                    self._value(
                        item.get(
                            header
                        )
                    )
                    for header
                    in headers
                ]
            )


        self._configure_sheet(
            sheet
        )


        # =================================================
        # RESTRICCIONES
        # =================================================

        sheet = workbook.create_sheet(
            "Restricciones"
        )

        headers = [
            "id",
            "constraint_type",
            "affects",
            "payload",
            "rationale",
            "validation_status",
            "source_id",
            "source_role",
        ]

        sheet.append(
            headers
        )


        for item in report.get(
            "farmer_knowledge",
            [],
        ):

            if (
                item.get(
                    "knowledge_type"
                )
                != "CONSTRAINT"
            ):
                continue


            sheet.append(
                [
                    self._value(
                        item.get(
                            header
                        )
                    )
                    for header
                    in headers
                ]
            )


        self._configure_sheet(
            sheet
        )


        # =================================================
        # DECISION TRACE COMPLETA
        # =================================================

        sheet = workbook.create_sheet(
            "DecisionTrace"
        )

        headers = [
            "trace_id",
            "created_at",
            "evidence_ids",
            "transformation_ids",
            "knowledge_ids",
            "conflict_ids",
            "feasible_scenarios",
            "rejected_scenarios",
            "ranking",
            "provisional_recommendation",
            "farmer_response",
            "final_action",
            "outcome",
            "metadata",
        ]

        sheet.append(
            headers
        )


        for trace in report.get(
            "decision_traces",
            [],
        ):

            row_values = [

                trace.get(
                    "trace_id"
                ),

                trace.get(
                    "created_at"
                ),

                recommendation.get(
                    "irrigation_mm"
                ),

                recommendation.get(
                    "score"
                ),

                recommendation.get(
                    "status"
                ),

                recommendation.get(
                    "source"
                ),

                farmer_response.get(
                    "response_type"
                ),

                trace.get(
                    "final_action"
                ),

                len(
                    trace.get(
                        "feasible_scenarios",
                        [],
                    )
                ),

                len(
                    trace.get(
                        "rejected_scenarios",
                        [],
                    )
                ),

                len(
                    trace.get(
                        "conflict_ids",
                        [],
                    )
                ),
            ]


            sheet.append(
                [
                    self._value(
                        value
                    )
                    for value
                    in row_values
                ]
            )

        self._configure_sheet(
            sheet
        )


        # =================================================
        # ML COMPLEMENTARIO
        # =================================================

        sheet = workbook.create_sheet(
            "ML Complementario"
        )

        sheet.append(
            [
                "Campo",
                "Valor",
            ]
        )


        ml = report.get(
            "ml_complementary",
            {},
        )

        forecast = (
            ml.get(
                "forecast"
            )
            or {}
        )


        ml_values = {

            "module":
                ml.get(
                    "module"
                ),

            "role":
                ml.get(
                    "role"
                ),

            "model":
                ml.get(
                    "model"
                ),

            "model_status":
                ml.get(
                    "model_status"
                ),

            "forecast_available":
                ml.get(
                    "forecast_available"
                ),

            "prediction_horizon_hours":
                ml.get(
                    "prediction_horizon_hours"
                ),

            "decision_authority":
                False,

            "modifies_trusted_state":
                False,

            "modifies_recommendation":
                False,

            "current_soil_moisture":
                forecast.get(
                    "current_soil_moisture"
                ),

            "predicted_delta_24h":
                forecast.get(
                    "predicted_delta_24h"
                ),

            "predicted_soil_moisture_24h":
                forecast.get(
                    "predicted_soil_moisture_24h"
                ),

            "delta_percent":
                forecast.get(
                    "delta_percent"
                ),

            "trend":
                forecast.get(
                    "trend"
                ),

            "uncertainty":
                forecast.get(
                    "uncertainty"
                ),

            "explanation":
                forecast.get(
                    "explanation"
                ),

            "message":
                ml.get(
                    "message"
                ),
        }


        for key, value in (
            ml_values.items()
        ):

            sheet.append(
                [
                    key,
                    self._value(
                        value
                    ),
                ]
            )


        self._configure_sheet(
            sheet,
            freeze_panes="A2",
        )

        # =================================================
        # GEOMETRY
        # =================================================

        sheet = (
            workbook.create_sheet(
                "Geometria"
            )
        )


        sheet.append(
            [
                "geojson"
            ]
        )


        geometry = (
            parcel.get(
                "geometry"
            )
        )


        sheet.append(
            [
                self._value(
                    geometry
                )
            ]
        )


        self._configure_sheet(
            sheet
        )


        # =================================================
        # SAVE
        # =================================================

        buffer = BytesIO()

        if report.get("publication_admin"):
            from services.publication_service import table_explanation
            for item in workbook:
                headers = [cell.value for cell in item[1]]
                item.append([])
                item.append([table_explanation(headers, max(0, item.max_row - 1))])
                item.cell(item.max_row, 1).alignment = Alignment(wrap_text=True, vertical="top")
                item.row_dimensions[item.max_row].height = 110

        workbook.save(
            buffer
        )


        return (
            buffer.getvalue()
        )