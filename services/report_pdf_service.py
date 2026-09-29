from io import BytesIO
from html import escape
import json

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import (
    getSampleStyleSheet,
    ParagraphStyle,
)
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak,
)


class ReportPDFService:

    @staticmethod
    def _text(value) -> str:

        if value is None:
            return "-"

        if isinstance(
            value,
            (dict, list),
        ):
            return json.dumps(
                value,
                ensure_ascii=False,
                default=str,
            )

        return str(value)


    @staticmethod
    def _origin(item: dict) -> str:

        metadata = (
            item.get("metadata")
            or {}
        )

        provenance = (
            item.get("provenance")
            or {}
        )

        if metadata.get("data_origin"):
            return str(
                metadata["data_origin"]
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
    def _paragraph(
        value,
        style,
    ):

        text = (
            "-"
            if value is None
            else str(value)
        )

        return Paragraph(
            escape(text),
            style,
        )


    def generate(
        self,
        report: dict,
    ) -> bytes:

        buffer = BytesIO()

        document = SimpleDocTemplate(
            buffer,
            pagesize=landscape(A4),
            rightMargin=1.2 * cm,
            leftMargin=1.2 * cm,
            topMargin=1.2 * cm,
            bottomMargin=1.2 * cm,
            title=(
                "Reporte del Gemelo "
                "Digital Agrícola"
            ),
        )


        styles = (
            getSampleStyleSheet()
        )


        title_style = ParagraphStyle(
            "ReportTitle",
            parent=styles["Title"],
            alignment=TA_CENTER,
            fontSize=20,
            leading=24,
            spaceAfter=14,
        )


        body_small = ParagraphStyle(
            "BodySmall",
            parent=styles["BodyText"],
            fontSize=7.5,
            leading=9,
        )


        table_header = ParagraphStyle(
            "TableHeader",
            parent=body_small,
            fontSize=7.5,
            leading=9,
        )


        story = []


        # =================================================
        # TITLE
        # =================================================

        story.append(
            Paragraph(
                (
                    "Reporte del Gemelo "
                    "Digital Agrícola"
                ),
                title_style,
            )
        )


        story.append(
            Paragraph(
                (
                    "Estado operativo, evidencia, "
                    "recomendaciones, conocimiento "
                    "del agricultor y gobernanza"
                ),
                styles["BodyText"],
            )
        )


        story.append(
            Spacer(
                1,
                14,
            )
        )


        parcel = (
            report.get(
                "parcel",
                {},
            )
        )

        summary = (
            report.get(
                "summary",
                {},
            )
        )


        # =================================================
        # 1. PARCEL
        # =================================================

        story.append(
            Paragraph(
                "1. Parcela",
                styles["Heading2"],
            )
        )


        parcel_rows = [
            [
                "Campo",
                "Valor",
            ],
            [
                "ID",
                parcel.get("id"),
            ],
            [
                "Nombre",
                parcel.get("name"),
            ],
            [
                "Cultivo",
                parcel.get(
                    "crop_type"
                ),
            ],
            [
                "Área (ha)",
                parcel.get(
                    "area_ha"
                ),
            ],
            [
                "Generado",
                report.get(
                    "generated_at"
                ),
            ],
        ]


        parcel_table = Table(
            [
                [
                    self._paragraph(
                        cell,
                        table_header,
                    )
                    for cell
                    in row
                ]
                for row
                in parcel_rows
            ],
            colWidths=[
                5 * cm,
                20 * cm,
            ],
        )


        parcel_table.setStyle(
            TableStyle(
                [
                    (
                        "GRID",
                        (0, 0),
                        (-1, -1),
                        0.5,
                        colors.grey,
                    ),
                    (
                        "BACKGROUND",
                        (0, 0),
                        (-1, 0),
                        colors.lightgrey,
                    ),
                    (
                        "FONTNAME",
                        (0, 0),
                        (-1, 0),
                        "Helvetica-Bold",
                    ),
                    (
                        "VALIGN",
                        (0, 0),
                        (-1, -1),
                        "TOP",
                    ),
                ]
            )
        )


        story.append(
            parcel_table
        )

        story.append(
            Spacer(
                1,
                14,
            )
        )


        # =================================================
        # 2. SUMMARY
        # =================================================

        story.append(
            Paragraph(
                "2. Resumen",
                styles["Heading2"],
            )
        )

        summary_labels = {

            "evidence_count":
                "Evidencias totales",

            "active_evidence_count":
                "Evidencias activas",

            "stale_evidence_count":
                "Evidencias desactualizadas",

            "sensor_count":
                "Sensores registrados",

            "active_sensor_count":
                "Sensores activos",

            "farmer_knowledge_count":
                "Aportes del agricultor",

            "constraint_count":
                "Restricciones registradas",

            "hard_constraint_count":
                "Restricciones HARD",

            "decision_trace_count":
                "Trazas de decisión",

            "latest_conflict_count":
                "Conflictos última decisión",

            "latest_feasible_scenario_count":
                "Escenarios factibles",

            "latest_rejected_scenario_count":
                "Escenarios rechazados",

            "active_consent_count":
                "Consentimientos activos",

            "ml_forecast_available":
                "Pronóstico ML complementario",
        }

        summary_rows = [
            [
                "Indicador",
                "Valor",
            ]
        ]


        for key, value in (
            summary.items()
        ):

            summary_rows.append(
                [
                    summary_labels.get(
                        key,
                        key,
                    ),
                    value,
                ]
            )


        summary_table = Table(
            [
                [
                    self._paragraph(
                        cell,
                        table_header,
                    )
                    for cell
                    in row
                ]
                for row
                in summary_rows
            ],
            colWidths=[
                12 * cm,
                6 * cm,
            ],
        )


        summary_table.setStyle(
            TableStyle(
                [
                    (
                        "GRID",
                        (0, 0),
                        (-1, -1),
                        0.5,
                        colors.grey,
                    ),
                    (
                        "BACKGROUND",
                        (0, 0),
                        (-1, 0),
                        colors.lightgrey,
                    ),
                    (
                        "FONTNAME",
                        (0, 0),
                        (-1, 0),
                        "Helvetica-Bold",
                    ),
                ]
            )
        )


        story.append(
            summary_table
        )

        story.append(
            Spacer(
                1,
                14,
            )
        )


        # =================================================
        # 3. LATEST DECISION
        # =================================================

        story.append(
            Paragraph(
                "3. Última decisión",
                styles["Heading2"],
            )
        )


        latest = (
            report.get(
                "latest_decision"
            )
        )


        if latest:

            recommendation = (
                latest.get(
                    "provisional_recommendation"
                )
                or {}
            )

            farmer_response = (
                latest.get(
                    "farmer_response"
                )
                or {}
            )

            final_action = (
                latest.get(
                    "final_action"
                )
            )


            decision_rows = [
                [
                    "Campo",
                    "Valor",
                ],
                [
                    "Trace ID",
                    latest.get(
                        "trace_id"
                    ),
                ],
                [
                    "Fecha",
                    latest.get(
                        "created_at"
                    ),
                ],
                [
                    "Riego recomendado (mm)",
                    recommendation.get(
                        "irrigation_mm"
                    ),
                ],
                [
                    "Score",
                    recommendation.get(
                        "score"
                    ),
                ],
                [
                    "Estado",
                    recommendation.get(
                        "status"
                    ),
                ],
                [
                    "Fuente",
                    recommendation.get(
                        "source"
                    ),
                ],
                [
                    "Razones",
                    " | ".join(
                        recommendation.get(
                            "reasons",
                            [],
                        )
                    ),
                ],
                [
                    "Respuesta agricultor",
                    (
                        farmer_response.get(
                            "response_type"
                        )
                        if farmer_response
                        else "-"
                    ),
                ],
                [
                    "Acción final",
                    self._text(
                        final_action
                    ),
                ],
            ]


            decision_table = Table(
                [
                    [
                        self._paragraph(
                            cell,
                            body_small,
                        )
                        for cell
                        in row
                    ]
                    for row
                    in decision_rows
                ],
                colWidths=[
                    7 * cm,
                    18 * cm,
                ],
            )


            decision_table.setStyle(
                TableStyle(
                    [
                        (
                            "GRID",
                            (0, 0),
                            (-1, -1),
                            0.5,
                            colors.grey,
                        ),
                        (
                            "BACKGROUND",
                            (0, 0),
                            (-1, 0),
                            colors.lightgrey,
                        ),
                        (
                            "FONTNAME",
                            (0, 0),
                            (-1, 0),
                            "Helvetica-Bold",
                        ),
                        (
                            "VALIGN",
                            (0, 0),
                            (-1, -1),
                            "TOP",
                        ),
                    ]
                )
            )


            story.append(
                decision_table
            )

        else:

            story.append(
                Paragraph(
                    (
                        "No existen decisiones "
                        "registradas."
                    ),
                    styles["BodyText"],
                )
            )


        story.append(
            PageBreak()
        )


        # =================================================
        # 4. EVIDENCE
        # =================================================

        story.append(
            Paragraph(
                "4. Evidencia",
                styles["Heading2"],
            )
        )


        evidence_rows = [
            [
                "Variable",
                "Valor",
                "Unidad",
                "Estado",
                "Calidad",
                "Origen",
                "Fecha",
            ]
        ]


        for item in (
            report.get(
                "evidence",
                [],
            )
        ):

            evidence_rows.append(
                [
                    item.get(
                        "variable"
                    ),

                    self._text(
                        item.get(
                            "value"
                        )
                    ),

                    item.get(
                        "unit"
                    ),

                    item.get(
                        "status"
                    ),

                    item.get(
                        "quality_score"
                    ),

                    self._origin(
                        item
                    ),

                    item.get(
                        "observed_at"
                    ),
                ]
            )


        evidence_table = Table(
            [
                [
                    self._paragraph(
                        cell,
                        body_small,
                    )
                    for cell
                    in row
                ]
                for row
                in evidence_rows
            ],
            repeatRows=1,
            colWidths=[
                4 * cm,
                7 * cm,
                2.5 * cm,
                2.5 * cm,
                2.5 * cm,
                4 * cm,
                5 * cm,
            ],
        )


        evidence_table.setStyle(
            TableStyle(
                [
                    (
                        "GRID",
                        (0, 0),
                        (-1, -1),
                        0.4,
                        colors.grey,
                    ),
                    (
                        "BACKGROUND",
                        (0, 0),
                        (-1, 0),
                        colors.lightgrey,
                    ),
                    (
                        "FONTNAME",
                        (0, 0),
                        (-1, 0),
                        "Helvetica-Bold",
                    ),
                    (
                        "VALIGN",
                        (0, 0),
                        (-1, -1),
                        "TOP",
                    ),
                ]
            )
        )


        story.append(
            evidence_table
        )


        story.append(
            Spacer(
                1,
                16,
            )
        )


        # =================================================
        # 5. FARMER KNOWLEDGE
        # =================================================

        story.append(
            Paragraph(
                (
                    "5. Conocimiento "
                    "del agricultor"
                ),
                styles["Heading2"],
            )
        )


        knowledge_rows = [
            [
                "Tipo",
                "Fuente",
                "Rol",
                "Contenido",
                "Validación",
                "Confianza",
            ]
        ]


        for item in (
            report.get(
                "farmer_knowledge",
                [],
            )
        ):

            knowledge_rows.append(
                [
                    item.get(
                        "knowledge_type"
                    ),

                    item.get(
                        "source_id"
                    ),

                    item.get(
                        "source_role"
                    ),

                    self._text(
                        item.get(
                            "payload"
                        )
                    ),

                    item.get(
                        "validation_status"
                    ),

                    item.get(
                        "reported_confidence"
                    ),
                ]
            )


        knowledge_table = Table(
            [
                [
                    self._paragraph(
                        cell,
                        body_small,
                    )
                    for cell
                    in row
                ]
                for row
                in knowledge_rows
            ],
            repeatRows=1,
            colWidths=[
                3.5 * cm,
                4 * cm,
                3 * cm,
                9 * cm,
                3.5 * cm,
                3 * cm,
            ],
        )


        knowledge_table.setStyle(
            TableStyle(
                [
                    (
                        "GRID",
                        (0, 0),
                        (-1, -1),
                        0.4,
                        colors.grey,
                    ),
                    (
                        "BACKGROUND",
                        (0, 0),
                        (-1, 0),
                        colors.lightgrey,
                    ),
                    (
                        "FONTNAME",
                        (0, 0),
                        (-1, 0),
                        "Helvetica-Bold",
                    ),
                    (
                        "VALIGN",
                        (0, 0),
                        (-1, -1),
                        "TOP",
                    ),
                ]
            )
        )


        story.append(
            knowledge_table
        )


        story.append(
            Spacer(
                1,
                16,
            )
        )


        # =================================================
        # 6. GOVERNANCE
        # =================================================

        story.append(
            Paragraph(
                "6. Gobernanza",
                styles["Heading2"],
            )
        )


        governance = (
            report.get(
                "governance",
                {},
            )
        )


        governance_rows = [
            [
                "Indicador",
                "Valor",
            ],
            [
                "Consentimientos totales",
                governance.get(
                    "consent_count"
                ),
            ],
            [
                "Consentimientos activos",
                governance.get(
                    "active_consent_count"
                ),
            ],
            [
                "Eventos de auditoría",
                governance.get(
                    "audit_event_count"
                ),
            ],
        ]


        governance_table = Table(
            [
                [
                    self._paragraph(
                        cell,
                        body_small,
                    )
                    for cell
                    in row
                ]
                for row
                in governance_rows
            ],
            colWidths=[
                10 * cm,
                8 * cm,
            ],
        )


        governance_table.setStyle(
            TableStyle(
                [
                    (
                        "GRID",
                        (0, 0),
                        (-1, -1),
                        0.5,
                        colors.grey,
                    ),
                    (
                        "BACKGROUND",
                        (0, 0),
                        (-1, 0),
                        colors.lightgrey,
                    ),
                    (
                        "FONTNAME",
                        (0, 0),
                        (-1, 0),
                        "Helvetica-Bold",
                    ),
                ]
            )
        )


        story.append(
            governance_table
        )


        audit_events = (
            governance.get(
                "latest_audit_events",
                [],
            )
        )


        if audit_events:

            story.append(
                Spacer(
                    1,
                    12,
                )
            )

            story.append(
                Paragraph(
                    (
                        "Últimos eventos "
                        "de auditoría"
                    ),
                    styles["Heading3"],
                )
            )


            audit_rows = [
                [
                    "Fecha",
                    "Actor",
                    "Acción",
                    "Permitido",
                    "Consentimiento",
                ]
            ]


            for item in (
                audit_events
            ):

                audit_rows.append(
                    [
                        item.get(
                            "created_at"
                        ),

                        item.get(
                            "actor_id"
                        ),

                        item.get(
                            "action"
                        ),

                        item.get(
                            "allowed"
                        ),

                        item.get(
                            "consent_id"
                        ),
                    ]
                )


            audit_table = Table(
                [
                    [
                        self._paragraph(
                            cell,
                            body_small,
                        )
                        for cell
                        in row
                    ]
                    for row
                    in audit_rows
                ],
                repeatRows=1,
                colWidths=[
                    6 * cm,
                    5 * cm,
                    5 * cm,
                    3 * cm,
                    6 * cm,
                ],
            )


            audit_table.setStyle(
                TableStyle(
                    [
                        (
                            "GRID",
                            (0, 0),
                            (-1, -1),
                            0.4,
                            colors.grey,
                        ),
                        (
                            "BACKGROUND",
                            (0, 0),
                            (-1, 0),
                            colors.lightgrey,
                        ),
                        (
                            "FONTNAME",
                            (0, 0),
                            (-1, 0),
                            "Helvetica-Bold",
                        ),
                        (
                            "VALIGN",
                            (0, 0),
                            (-1, -1),
                            "TOP",
                        ),
                    ]
                )
            )


            story.append(
                audit_table
            )


        # =================================================
        # 7. SENSORS
        # =================================================

        story.append(
            PageBreak()
        )

        story.append(
            Paragraph(
                "7. Sensores registrados",
                styles["Heading2"],
            )
        )


        sensors = (
            report.get(
                "sensors",
                [],
            )
        )


        if sensors:

            sensor_rows = [
                [
                    "ID",
                    "Nombre",
                    "Tipo",
                    "Variables",
                    "Activo",
                    "Fabricante / Modelo",
                    "Ubicación",
                ]
            ]


            for sensor in sensors:

                sensor_rows.append(
                    [
                        sensor.get(
                            "id"
                        ),

                        sensor.get(
                            "name"
                        ),

                        sensor.get(
                            "sensor_type"
                        ),

                        ", ".join(
                            sensor.get(
                                "variables",
                                [],
                            )
                        ),

                        (
                            "Sí"
                            if sensor.get(
                                "is_active"
                            )
                            else "No"
                        ),

                        (
                            f"{sensor.get('manufacturer') or '-'} "
                            f"/ "
                            f"{sensor.get('model') or '-'}"
                        ),

                        (
                            f"{sensor.get('latitude') or '-'}, "
                            f"{sensor.get('longitude') or '-'}"
                        ),
                    ]
                )


            sensor_table = Table(
                [
                    [
                        self._paragraph(
                            cell,
                            body_small,
                        )
                        for cell
                        in row
                    ]
                    for row
                    in sensor_rows
                ],
                repeatRows=1,
            )


            sensor_table.setStyle(
                TableStyle(
                    [
                        (
                            "GRID",
                            (0, 0),
                            (-1, -1),
                            0.4,
                            colors.grey,
                        ),
                        (
                            "BACKGROUND",
                            (0, 0),
                            (-1, 0),
                            colors.lightgrey,
                        ),
                        (
                            "FONTNAME",
                            (0, 0),
                            (-1, 0),
                            "Helvetica-Bold",
                        ),
                        (
                            "VALIGN",
                            (0, 0),
                            (-1, -1),
                            "TOP",
                        ),
                    ]
                )
            )


            story.append(
                sensor_table
            )

        else:

            story.append(
                Paragraph(
                    "No existen sensores registrados.",
                    styles["BodyText"],
                )
            )


        # =================================================
        # 8. FARMER CONSTRAINTS
        # =================================================

        story.append(
            Spacer(
                1,
                16,
            )
        )

        story.append(
            Paragraph(
                (
                    "8. Restricciones aportadas "
                    "por el agricultor"
                ),
                styles["Heading2"],
            )
        )


        constraints = [
            item
            for item
            in report.get(
                "farmer_knowledge",
                [],
            )
            if (
                item.get(
                    "knowledge_type"
                )
                == "CONSTRAINT"
            )
        ]


        if constraints:

            constraint_rows = [
                [
                    "Tipo",
                    "Afecta",
                    "Contenido",
                    "Justificación",
                    "Validación",
                ]
            ]


            for item in constraints:

                constraint_rows.append(
                    [
                        item.get(
                            "constraint_type"
                        ),

                        ", ".join(
                            item.get(
                                "affects",
                                [],
                            )
                        ),

                        self._text(
                            item.get(
                                "payload"
                            )
                        ),

                        item.get(
                            "rationale"
                        ),

                        item.get(
                            "validation_status"
                        ),
                    ]
                )


            constraint_table = Table(
                [
                    [
                        self._paragraph(
                            cell,
                            body_small,
                        )
                        for cell
                        in row
                    ]
                    for row
                    in constraint_rows
                ],
                repeatRows=1,
            )


            constraint_table.setStyle(
                TableStyle(
                    [
                        (
                            "GRID",
                            (0, 0),
                            (-1, -1),
                            0.4,
                            colors.grey,
                        ),
                        (
                            "BACKGROUND",
                            (0, 0),
                            (-1, 0),
                            colors.lightgrey,
                        ),
                        (
                            "FONTNAME",
                            (0, 0),
                            (-1, 0),
                            "Helvetica-Bold",
                        ),
                        (
                            "VALIGN",
                            (0, 0),
                            (-1, -1),
                            "TOP",
                        ),
                    ]
                )
            )


            story.append(
                constraint_table
            )

        else:

            story.append(
                Paragraph(
                    (
                        "No existen restricciones "
                        "participativas registradas."
                    ),
                    styles["BodyText"],
                )
            )


        # =================================================
        # 9. DECISION TRACE
        # =================================================

        story.append(
            PageBreak()
        )

        story.append(
            Paragraph(
                (
                    "9. Trazabilidad del motor "
                    "de inferencia y decisión"
                ),
                styles["Heading2"],
            )
        )


        story.append(
            Paragraph(
                (
                    "Esta sección corresponde al motor "
                    "de inferencia y decisión. "
                    "El Random Forest complementario "
                    "no participa en el ranking ni en "
                    "la recomendación."
                ),
                styles["BodyText"],
            )
        )


        traces = (
            report.get(
                "decision_traces",
                [],
            )
        )


        if traces:

            history_rows = [
                [
                    "Trace ID",
                    "Fecha",
                    "Riego",
                    "Respuesta HITL",
                    "Factibles",
                    "Rechazados",
                    "Conflictos",
                ]
            ]


            for trace in traces[:10]:

                recommendation = (
                    trace.get(
                        "provisional_recommendation"
                    )
                    or {}
                )

                response = (
                    trace.get(
                        "farmer_response"
                    )
                    or {}
                )


                history_rows.append(
                    [
                        trace.get(
                            "trace_id"
                        ),

                        trace.get(
                            "created_at"
                        ),

                        recommendation.get(
                            "irrigation_mm"
                        ),

                        response.get(
                            "response_type"
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


            history_table = Table(
                [
                    [
                        self._paragraph(
                            cell,
                            body_small,
                        )
                        for cell
                        in row
                    ]
                    for row
                    in history_rows
                ],
                repeatRows=1,
            )


            history_table.setStyle(
                TableStyle(
                    [
                        (
                            "GRID",
                            (0, 0),
                            (-1, -1),
                            0.4,
                            colors.grey,
                        ),
                        (
                            "BACKGROUND",
                            (0, 0),
                            (-1, 0),
                            colors.lightgrey,
                        ),
                        (
                            "FONTNAME",
                            (0, 0),
                            (-1, 0),
                            "Helvetica-Bold",
                        ),
                        (
                            "VALIGN",
                            (0, 0),
                            (-1, -1),
                            "TOP",
                        ),
                    ]
                )
            )


            story.append(
                history_table
            )


            latest_trace = traces[0]


            story.append(
                Spacer(
                    1,
                    14,
                )
            )

            story.append(
                Paragraph(
                    "Detalle de la última DecisionTrace",
                    styles["Heading3"],
                )
            )

            # =================================================
            # FULL TRACE DETAIL
            #
            # Important:
            # Large DecisionTrace structures must NOT be placed
            # inside one table cell because ReportLab cannot
            # split an oversized table row across pages.
            #
            # Paragraphs can split naturally between pages.
            # =================================================

            trace_detail = [

                (
                    "Evidencias",
                    latest_trace.get(
                        "evidence_ids",
                        [],
                    ),
                ),

                (
                    "Transformaciones",
                    latest_trace.get(
                        "transformation_ids",
                        [],
                    ),
                ),

                (
                    "Conocimiento del agricultor",
                    latest_trace.get(
                        "knowledge_ids",
                        [],
                    ),
                ),

                (
                    "Conflictos",
                    latest_trace.get(
                        "conflict_ids",
                        [],
                    ),
                ),

                (
                    "Escenarios factibles",
                    latest_trace.get(
                        "feasible_scenarios",
                        [],
                    ),
                ),

                (
                    "Escenarios rechazados",
                    latest_trace.get(
                        "rejected_scenarios",
                        [],
                    ),
                ),

                (
                    "Ranking multicriterio",
                    latest_trace.get(
                        "ranking",
                        [],
                    ),
                ),

                (
                    "Recomendación provisional",
                    latest_trace.get(
                        "provisional_recommendation"
                    ),
                ),

                (
                    "Respuesta humana HITL",
                    latest_trace.get(
                        "farmer_response"
                    ),
                ),

                (
                    "Acción final",
                    latest_trace.get(
                        "final_action"
                    ),
                ),

                (
                    "Outcome",
                    latest_trace.get(
                        "outcome"
                    ),
                ),
            ]


            for label, value in trace_detail:

                story.append(
                    Paragraph(
                        (
                            "<b>"
                            + escape(
                                label
                            )
                            + "</b>"
                        ),
                        body_small,
                    )
                )


                story.append(
                    Spacer(
                        1,
                        4,
                    )
                )


                if isinstance(
                    value,
                    (
                        dict,
                        list,
                    ),
                ):

                    raw_value = json.dumps(
                        value,
                        ensure_ascii=False,
                        default=str,
                        indent=2,
                    )

                elif value is None:

                    raw_value = "-"

                else:

                    raw_value = str(
                        value
                    )


                safe_value = (
                    escape(
                        raw_value
                    )
                    .replace(
                        "\n",
                        "<br/>",
                    )
                )


                story.append(
                    Paragraph(
                        safe_value,
                        body_small,
                    )
                )


                story.append(
                    Spacer(
                        1,
                        10,
                    )
                )

        else:

            story.append(
                Paragraph(
                    (
                        "No existen DecisionTrace "
                        "registradas."
                    ),
                    styles["BodyText"],
                )
            )


        # =================================================
        # 10. COMPLEMENTARY ML
        # =================================================

        story.append(
            Spacer(
                1,
                16,
            )
        )

        story.append(
            Paragraph(
                (
                    "10. Random Forest "
                    "complementario"
                ),
                styles["Heading2"],
            )
        )


        ml = (
            report.get(
                "ml_complementary",
                {},
            )
        )

        forecast = (
            ml.get(
                "forecast"
            )
            or {}
        )

        uncertainty = (
            forecast.get(
                "uncertainty"
            )
            or {}
        )


        ml_rows = [
            [
                "Campo",
                "Valor",
            ],
            [
                "Rol",
                (
                    "Predicción complementaria "
                    "sin autoridad decisional"
                ),
            ],
            [
                "Modelo",
                ml.get(
                    "model"
                ),
            ],
            [
                "Estado del modelo",
                ml.get(
                    "model_status"
                ),
            ],
            [
                "Pronóstico disponible",
                ml.get(
                    "forecast_available"
                ),
            ],
            [
                "Horizonte (h)",
                ml.get(
                    "prediction_horizon_hours"
                ),
            ],
            [
                "Humedad actual",
                forecast.get(
                    "current_soil_moisture"
                ),
            ],
            [
                "Humedad prevista +24 h",
                forecast.get(
                    "predicted_soil_moisture_24h"
                ),
            ],
            [
                "P10",
                uncertainty.get(
                    "p10"
                ),
            ],
            [
                "P90",
                uncertainty.get(
                    "p90"
                ),
            ],
            [
                "Tendencia",
                forecast.get(
                    "trend"
                ),
            ],
            [
                "Modifica TrustedState",
                False,
            ],
            [
                "Modifica recomendación",
                False,
            ],
            [
                "Mensaje",
                ml.get(
                    "message"
                ),
            ],
        ]


        ml_table = Table(
            [
                [
                    self._paragraph(
                        cell,
                        body_small,
                    )
                    for cell
                    in row
                ]
                for row
                in ml_rows
            ],
            colWidths=[
                8 * cm,
                17 * cm,
            ],
        )


        ml_table.setStyle(
            TableStyle(
                [
                    (
                        "GRID",
                        (0, 0),
                        (-1, -1),
                        0.4,
                        colors.grey,
                    ),
                    (
                        "BACKGROUND",
                        (0, 0),
                        (-1, 0),
                        colors.lightgrey,
                    ),
                    (
                        "FONTNAME",
                        (0, 0),
                        (-1, 0),
                        "Helvetica-Bold",
                    ),
                    (
                        "VALIGN",
                        (0, 0),
                        (-1, -1),
                        "TOP",
                    ),
                ]
            )
        )


        story.append(
            ml_table
        )

        document.build(
            story
        )


        return (
            buffer.getvalue()
        )