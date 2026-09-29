import {
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react";

import {
  Activity,
  AlertTriangle,
  BookOpen,
  BrainCircuit,
  CheckCircle2,
  ChevronDown,
  ChevronUp,
  CircleX,
  Database,
  GitBranch,
  ListOrdered,
  RefreshCw,
  ShieldCheck,
  UserCheck,
} from "lucide-react";

import {
  getDecisionTracesByParcel,
  type DecisionTrace,
} from "../../api/decisionTraces";

import {
  useLanguage,
} from "../../i18n/LanguageContext";


interface Props {
  parcelId: string;
}


type JsonRecord =
  Record<string, unknown>;


type Translate = (
  es: string,
  en: string
) => string;


/* ===================================================== */
/* FORMATTERS                                            */
/* ===================================================== */

function formatDate(
  timestamp: string,
  language: "es" | "en"
): string {

  const date =
    new Date(
      timestamp
    );

  if (
    Number.isNaN(
      date.getTime()
    )
  ) {
    return timestamp;
  }


  return date.toLocaleString(
    language === "es"
      ? "es-PE"
      : "en-US",
    {
      dateStyle:
        "medium",

      timeStyle:
        "short",
    }
  );
}


function shortenId(
  value: string
): string {

  if (
    value.length <= 22
  ) {
    return value;
  }


  return (
    `${value.slice(
      0,
      10
    )}…${value.slice(
      -8
    )}`
  );
}


function humanizeKey(
  key: string,
  tr: Translate
): string {

  const special:
    Record<string, string> = {

      irrigation_mm:
        tr(
          "Riego",
          "Irrigation"
        ),

      score:
        tr(
          "Puntaje",
          "Score"
        ),

      status:
        tr(
          "Estado",
          "Status"
        ),

      scenario_id:
        tr(
          "Escenario",
          "Scenario"
        ),

      response_type:
        tr(
          "Respuesta",
          "Response"
        ),

      modified_action:
        tr(
          "Acción modificada",
          "Modified action"
        ),

      rationale:
        tr(
          "Justificación",
          "Rationale"
        ),

      responded_at:
        tr(
          "Respondido",
          "Responded"
        ),

      final_action:
        tr(
          "Acción final",
          "Final action"
        ),

      predicted_yield:
        tr(
          "Rendimiento",
          "Yield"
        ),

      risk:
        tr(
          "Riesgo",
          "Risk"
        ),

      variable:
        tr(
          "Variable",
          "Variable"
        ),

      value:
        tr(
          "Valor",
          "Value"
        ),

      unit:
        tr(
          "Unidad",
          "Unit"
        ),

      constraint_type:
        tr(
          "Tipo de restricción",
          "Constraint type"
        ),

      preference:
        tr(
          "Preferencia",
          "Preference"
        ),

      priority:
        tr(
          "Prioridad",
          "Priority"
        ),

      description:
        tr(
          "Descripción",
          "Description"
        ),

      event_type:
        tr(
          "Tipo de evento",
          "Event type"
        ),

      confidence:
        tr(
          "Confianza",
          "Confidence"
        ),

      confidence_score:
        tr(
          "Puntaje de confianza",
          "Confidence score"
        ),
    };


  if (
    special[
      key
    ]
  ) {
    return special[
      key
    ];
  }


  return key
    .replace(
      /_/g,
      " "
    )
    .replace(
      /\b\w/g,
      (
        character
      ) =>
        character
          .toUpperCase()
    );
}


function primitiveText(
  value: unknown,
  tr: Translate
): string | null {

  if (
    value === null
    ||
    value === undefined
  ) {
    return "—";
  }


  if (
    typeof value ===
    "boolean"
  ) {

    return value
      ? tr(
          "Sí",
          "Yes"
        )
      : tr(
          "No",
          "No"
        );
  }


  if (
    typeof value ===
    "number"
  ) {

    if (
      Number.isInteger(
        value
      )
    ) {

      return String(
        value
      );
    }


    return value.toFixed(
      4
    );
  }


  if (
    typeof value ===
    "string"
  ) {
    return value;
  }


  return null;
}


/* ===================================================== */
/* OBJECT DETAILS                                        */
/* ===================================================== */

function ObjectDetails({
  value,
  emptyText,
  tr,
}: {
  value:
    | JsonRecord
    | null
    | undefined;

  emptyText: string;

  tr: Translate;
}) {

  if (
    !value
    ||
    Object.keys(
      value
    ).length === 0
  ) {

    return (
      <div className="trace-empty-inline">

        {emptyText}

      </div>
    );
  }


  return (
    <div className="trace-object-grid">

      {Object.entries(
        value
      ).map(
        ([
          key,
          entry,
        ]) => {

          const primitive =
            primitiveText(
              entry,
              tr
            );


          return (

            <div
              className="trace-object-row"
              key={
                key
              }
            >

              <span>

                {humanizeKey(
                  key,
                  tr
                )}

              </span>


              {primitive !==
              null ? (

                <strong>
                  {primitive}
                </strong>

              ) : (

                <pre>
                  {JSON.stringify(
                    entry,
                    null,
                    2
                  )}
                </pre>

              )}

            </div>
          );
        }
      )}

    </div>
  );
}


/* ===================================================== */
/* IDENTIFIER LIST                                       */
/* ===================================================== */

function IdentifierList({
  ids,
  emptyText,
  initialLimit = null,
  collapsible = false,
  tr,
}: {
  ids: string[];

  emptyText: string;

  initialLimit?:
    number | null;

  collapsible?:
    boolean;

  tr: Translate;
}) {

  const [
    expanded,
    setExpanded,
  ] = useState(
    false
  );


  useEffect(
    () => {

      setExpanded(
        false
      );

    },
    [
      ids,
    ]
  );


  const hasOverflow =
    collapsible
    &&
    typeof initialLimit ===
      "number"
    &&
    initialLimit > 0
    &&
    ids.length >
      initialLimit;


  const visibleIds =
    hasOverflow
    &&
    !expanded
      ? ids.slice(
          0,
          initialLimit
        )
      : ids;


  if (
    ids.length === 0
  ) {

    return (
      <div className="trace-empty-inline">

        {emptyText}

      </div>
    );
  }


  return (
    <div className="trace-id-list">

      {visibleIds.map(
        (
          id,
          index
        ) => (

          <div
            className="trace-id-chip"
            key={
              `${id}-${index}`
            }
            title={
              id
            }
          >

            <span>
              {index + 1}
            </span>

            <code>
              {shortenId(
                id
              )}
            </code>

          </div>
        )
      )}


      {hasOverflow && (

        <button
          type="button"
          className="trace-id-more-toggle"
          onClick={() =>
            setExpanded(
              (
                current
              ) =>
                !current
            )
          }
        >

          {expanded ? (

            <>

              <ChevronUp
                size={15}
              />

              {tr(
                "Ocultar evidencias adicionales",
                "Hide additional evidence"
              )}

            </>

          ) : (

            <>

              <ChevronDown
                size={15}
              />

              {tr(
                `Ver ${
                  ids.length
                  -
                  (
                    initialLimit
                    ?? 0
                  )
                } evidencias adicionales`,
                `View ${
                  ids.length
                  -
                  (
                    initialLimit
                    ?? 0
                  )
                } additional evidence items`
              )}

            </>

          )}

        </button>
      )}

    </div>
  );
}


/* ===================================================== */
/* SCENARIOS                                             */
/* ===================================================== */

function ScenarioList({
  items,
  variant,
  emptyText,
  tr,
}: {
  items:
    Array<JsonRecord>;

  variant:
    | "feasible"
    | "rejected"
    | "ranking";

  emptyText: string;

  tr: Translate;
}) {

  if (
    items.length === 0
  ) {

    return (
      <div className="trace-empty-inline">

        {emptyText}

      </div>
    );
  }


  return (
    <div className="trace-scenario-list">

      {items.map(
        (
          item,
          index
        ) => {

          const title =
            typeof item
              .scenario_id ===
              "string"

              ? item
                  .scenario_id

              : typeof item
                  .name ===
                  "string"

                ? item
                    .name

                : variant ===
                    "ranking"

                  ? tr(
                      `Posición ${index + 1}`,
                      `Position ${index + 1}`
                    )

                  : tr(
                      `Escenario ${index + 1}`,
                      `Scenario ${index + 1}`
                    );


          const irrigation =
            typeof item
              .irrigation_mm ===
              "number"

              ? `${item.irrigation_mm} mm`

              : null;


          const score =
            typeof item
              .score ===
              "number"

              ? item
                  .score
                  .toFixed(
                    3
                  )

              : null;


          return (

            <article
              className={
                `trace-scenario-card ${variant}`
              }
              key={
                `${title}-${index}`
              }
            >

              <div className="trace-scenario-card-head">

                <div>

                  <strong>
                    {title}
                  </strong>

                  <span>

                    {variant ===
                    "feasible"

                      ? tr(
                          "Factible",
                          "Feasible"
                        )

                      : variant ===
                        "rejected"

                        ? tr(
                            "Rechazado",
                            "Rejected"
                          )

                        : `${tr(
                            "Ranking",
                            "Ranking"
                          )} #${index + 1}`}

                  </span>

                </div>


                <div className="trace-scenario-quick">

                  {irrigation && (

                    <span>
                      {irrigation}
                    </span>
                  )}

                  {score && (

                    <span>

                      {tr(
                        "puntaje",
                        "score"
                      )}{" "}

                      {score}

                    </span>
                  )}

                </div>

              </div>


              <ObjectDetails
                value={
                  item
                }
                emptyText={tr(
                  "Sin información adicional.",
                  "No additional information."
                )}
                tr={
                  tr
                }
              />

            </article>
          );
        }
      )}

    </div>
  );
}


/* ===================================================== */
/* TRACE STAGE                                           */
/* ===================================================== */

function TraceStage({
  number,
  icon,
  title,
  description,
  children,
  tone = "neutral",
}: {
  number: number;

  icon: ReactNode;

  title: string;

  description: string;

  children: ReactNode;

  tone?:
    | "neutral"
    | "success"
    | "warning"
    | "purple"
    | "danger";
}) {

  return (
    <section
      className={
        `trace-stage ${tone}`
      }
    >

      <div className="trace-stage-rail">

        <div className="trace-stage-number">
          {number}
        </div>

        <div className="trace-stage-line" />

      </div>


      <div className="trace-stage-body">

        <div className="trace-stage-header">

          <div
            className={
              `trace-stage-icon ${tone}`
            }
          >
            {icon}
          </div>


          <div>

            <h3>
              {title}
            </h3>

            <p>
              {description}
            </p>

          </div>

        </div>


        <div className="trace-stage-content">
          {children}
        </div>

      </div>

    </section>
  );
}


/* ===================================================== */
/* TRACE STATUS                                          */
/* ===================================================== */

function traceStatus(
  trace: DecisionTrace,
  tr: Translate
) {

  const response =
    trace
      .farmer_response
      ?.response_type;


  if (
    response ===
    "REJECT"
  ) {

    return {
      label:
        tr(
          "Rechazada por agricultor",
          "Rejected by farmer"
        ),

      className:
        "rejected",
    };
  }


  if (
    response ===
    "MODIFY"
  ) {

    return {
      label:
        tr(
          "Modificada por agricultor",
          "Modified by farmer"
        ),

      className:
        "modified",
    };
  }


  if (
    response ===
    "ACCEPT"
  ) {

    return {
      label:
        tr(
          "Aceptada por agricultor",
          "Accepted by farmer"
        ),

      className:
        "accepted",
    };
  }


  if (
    trace.final_action
  ) {

    return {
      label:
        tr(
          "Acción final registrada",
          "Final action recorded"
        ),

      className:
        "completed",
    };
  }


  return {
    label:
      tr(
        "Pendiente de respuesta humana",
        "Pending human response"
      ),

    className:
      "pending",
  };
}


/* ===================================================== */
/* COMPONENT                                             */
/* ===================================================== */

export function DecisionTracePanel({
  parcelId,
}: Props) {

  const {
    language,
    tr,
  } = useLanguage();


  const [
    traces,
    setTraces,
  ] = useState<
    DecisionTrace[]
  >([]);


  const [
    selectedTraceId,
    setSelectedTraceId,
  ] = useState<
    string | null
  >(null);


  const [
    loading,
    setLoading,
  ] = useState(
    true
  );


  const [
    error,
    setError,
  ] = useState(
    ""
  );


  const [
    showTechnical,
    setShowTechnical,
  ] = useState(
    false
  );


  const [
    historyPage,
    setHistoryPage,
  ] = useState(
    1
  );


  const HISTORY_PAGE_SIZE =
    4;


  const load =
    async () => {

      setLoading(
        true
      );

      setError(
        ""
      );


      try {

        const data =
          await getDecisionTracesByParcel(
            parcelId
          );


        setTraces(
          data
        );


        setHistoryPage(
          1
        );


        setSelectedTraceId(
          (
            current
          ) => {

            if (
              current
              &&
              data.some(
                (
                  trace
                ) =>
                  trace.trace_id ===
                  current
              )
            ) {
              return current;
            }


            return (
              data[0]
                ?.trace_id
              ??
              null
            );
          }
        );


      } catch {

        setError(
          tr(
            "No se pudo cargar la trazabilidad del motor de decisión.",
            "Could not load the decision engine traceability."
          )
        );

      } finally {

        setLoading(
          false
        );
      }
    };


  useEffect(
    () => {

      void load();

    },
    [
      parcelId,
    ]
  );


  const selectedTrace =
    useMemo(
      () => {

        return (
          traces.find(
            (
              trace
            ) =>
              trace.trace_id ===
              selectedTraceId
          )
          ??
          traces[0]
          ??
          null
        );

      },
      [
        traces,
        selectedTraceId,
      ]
    );


  const historyPageCount =
    Math.max(
      1,
      Math.ceil(
        traces.length
        /
        HISTORY_PAGE_SIZE
      )
    );


  const safeHistoryPage =
    Math.min(
      historyPage,
      historyPageCount
    );


  const historyStartIndex =
    (
      safeHistoryPage
      -
      1
    )
    *
    HISTORY_PAGE_SIZE;


  const visibleHistoryTraces =
    traces.slice(
      historyStartIndex,
      historyStartIndex
      +
      HISTORY_PAGE_SIZE
    );


  const changeHistoryPage =
    (
      page: number
    ) => {

      const nextPage =
        Math.max(
          1,
          Math.min(
            historyPageCount,
            page
          )
        );


      setHistoryPage(
        nextPage
      );


      const firstTrace =
        traces[
          (
            nextPage
            -
            1
          )
          *
          HISTORY_PAGE_SIZE
        ];


      if (
        firstTrace
      ) {

        setSelectedTraceId(
          firstTrace.trace_id
        );

        setShowTechnical(
          false
        );
      }
    };


  if (
    loading
  ) {

    return (
      <section className="panel trace-panel trace-loading">

        <Activity
          size={24}
        />

        <strong>
          {tr(
            "Cargando trazabilidad...",
            "Loading traceability..."
          )}
        </strong>

      </section>
    );
  }


  if (
    error
  ) {

    return (
      <section className="panel trace-panel trace-error">

        <AlertTriangle
          size={25}
        />

        <strong>
          {tr(
            "No se pudo cargar DecisionTrace",
            "Could not load DecisionTrace"
          )}
        </strong>

        <span>
          {error}
        </span>

        <button
          type="button"
          className="button-secondary"
          onClick={() =>
            void load()
          }
        >

          <RefreshCw
            size={15}
          />

          {tr(
            "Reintentar",
            "Retry"
          )}

        </button>

      </section>
    );
  }


  if (
    traces.length === 0
    ||
    !selectedTrace
  ) {

    return (
      <section className="panel trace-panel trace-empty">

        <GitBranch
          size={29}
        />

        <strong>
          {tr(
            "Todavía no hay trazas de decisión",
            "There are no decision traces yet"
          )}
        </strong>

        <span>
          {tr(
            "Ejecuta el motor de inferencia para generar una DecisionTrace persistida para esta parcela.",
            "Run the inference engine to generate a persisted DecisionTrace for this parcel."
          )}
        </span>

      </section>
    );
  }


  const status =
    traceStatus(
      selectedTrace,
      tr
    );


  return (
    <div className="decision-trace-view">

      {/* ================================================= */}
      {/* INTRO                                             */}
      {/* ================================================= */}

      <section className="panel trace-intro-panel">

        <div className="panel-header">

          <div className="panel-header-title">

            <div className="panel-icon">

              <GitBranch
                size={20}
              />

            </div>


            <div>

              <h2>
                {tr(
                  "Trazabilidad del motor de decisión",
                  "Decision engine traceability"
                )}
              </h2>

              <p>
                {tr(
                  "DecisionTrace · evidencia → escenarios → HITL → acción final",
                  "DecisionTrace · evidence → scenarios → HITL → final action"
                )}
              </p>

            </div>

          </div>


          <button
            type="button"
            className="button-secondary trace-refresh-button"
            onClick={() =>
              void load()
            }
          >

            <RefreshCw
              size={15}
            />

            {tr(
              "Actualizar",
              "Refresh"
            )}

          </button>

        </div>


        <div className="trace-scope-note">

          <ShieldCheck
            size={18}
          />

          <div>

            <strong>
              {tr(
                "Esta trazabilidad pertenece al motor de inferencia y decisión.",
                "This traceability belongs to the inference and decision engine."
              )}
            </strong>

            <span>
              {tr(
                "El Random Forest complementario no participa en esta DecisionTrace, no altera el ranking de escenarios y no modifica la recomendación.",
                "The complementary Random Forest does not participate in this DecisionTrace, does not alter scenario ranking and does not modify the recommendation."
              )}
            </span>

          </div>

        </div>

      </section>


      <div className="decision-trace-layout">

        {/* ================================================= */}
        {/* HISTORY                                           */}
        {/* ================================================= */}

        <aside className="panel trace-history-panel">

          <div className="trace-history-heading">

            <div>

              <strong>
                {tr(
                  "Ejecuciones",
                  "Executions"
                )}
              </strong>

              <span>

                {traces.length}

                {" "}

                {traces.length === 1
                  ? tr(
                      "traza",
                      "trace"
                    )
                  : tr(
                      "trazas",
                      "traces"
                    )}

              </span>

            </div>

          </div>


          <div className="trace-history-list">

            {visibleHistoryTraces.map(
              (
                trace,
                index
              ) => {

                const itemStatus =
                  traceStatus(
                    trace,
                    tr
                  );


                return (

                  <button
                    type="button"
                    key={
                      trace.trace_id
                    }
                    className={
                      trace.trace_id ===
                        selectedTrace.trace_id

                        ? "trace-history-item active"

                        : "trace-history-item"
                    }
                    onClick={() => {

                      setSelectedTraceId(
                        trace.trace_id
                      );

                      setShowTechnical(
                        false
                      );
                    }}
                  >

                    <div className="trace-history-index">

                      {
                        traces.length
                        -
                        (
                          historyStartIndex
                          +
                          index
                        )
                      }

                    </div>


                    <div className="trace-history-content">

                      <strong>

                        {formatDate(
                          trace.created_at,
                          language
                        )}

                      </strong>


                      <code
                        title={
                          trace.trace_id
                        }
                      >

                        {shortenId(
                          trace.trace_id
                        )}

                      </code>


                      <span
                        className={
                          `trace-status ${itemStatus.className}`
                        }
                      >

                        {itemStatus.label}

                      </span>

                    </div>

                  </button>
                );
              }
            )}

          </div>


          {historyPageCount > 1 && (

            <div className="trace-history-pagination">

              <button
                type="button"
                aria-label={tr(
                  "Página anterior de ejecuciones",
                  "Previous execution page"
                )}
                disabled={
                  safeHistoryPage <=
                  1
                }
                onClick={() =>
                  changeHistoryPage(
                    safeHistoryPage
                    -
                    1
                  )
                }
              >
                ‹
              </button>


              <span>

                {tr(
                  `Página ${safeHistoryPage} de ${historyPageCount}`,
                  `Page ${safeHistoryPage} of ${historyPageCount}`
                )}

              </span>


              <button
                type="button"
                aria-label={tr(
                  "Página siguiente de ejecuciones",
                  "Next execution page"
                )}
                disabled={
                  safeHistoryPage >=
                  historyPageCount
                }
                onClick={() =>
                  changeHistoryPage(
                    safeHistoryPage
                    +
                    1
                  )
                }
              >
                ›
              </button>

            </div>
          )}

        </aside>


        {/* ================================================= */}
        {/* MAIN                                              */}
        {/* ================================================= */}

        <main className="trace-main">

          {/* =============================================== */}
          {/* SUMMARY                                         */}
          {/* =============================================== */}

          <section className="panel trace-summary-panel">

            <div className="trace-summary-header">

              <div>

                <span>
                  {tr(
                    "DecisionTrace seleccionada",
                    "Selected DecisionTrace"
                  )}
                </span>

                <strong
                  title={
                    selectedTrace
                      .trace_id
                  }
                >
                  {
                    selectedTrace
                      .trace_id
                  }
                </strong>

                <small>
                  {formatDate(
                    selectedTrace
                      .created_at,
                    language
                  )}
                </small>

              </div>


              <span
                className={
                  `trace-status large ${status.className}`
                }
              >
                {status.label}
              </span>

            </div>


            <div className="trace-summary-grid">

              <div>

                <Database
                  size={17}
                />

                <span>
                  {tr(
                    "Evidencias",
                    "Evidence"
                  )}
                </span>

                <strong>
                  {
                    selectedTrace
                      .evidence_ids
                      .length
                  }
                </strong>

              </div>


              <div>

                <BookOpen
                  size={17}
                />

                <span>
                  {tr(
                    "Conocimiento",
                    "Knowledge"
                  )}
                </span>

                <strong>
                  {
                    selectedTrace
                      .knowledge_ids
                      .length
                  }
                </strong>

              </div>


              <div>

                <AlertTriangle
                  size={17}
                />

                <span>
                  {tr(
                    "Conflictos",
                    "Conflicts"
                  )}
                </span>

                <strong>
                  {
                    selectedTrace
                      .conflict_ids
                      .length
                  }
                </strong>

              </div>


              <div>

                <CheckCircle2
                  size={17}
                />

                <span>
                  {tr(
                    "Factibles",
                    "Feasible"
                  )}
                </span>

                <strong>
                  {
                    selectedTrace
                      .feasible_scenarios
                      .length
                  }
                </strong>

              </div>


              <div>

                <CircleX
                  size={17}
                />

                <span>
                  {tr(
                    "Rechazados",
                    "Rejected"
                  )}
                </span>

                <strong>
                  {
                    selectedTrace
                      .rejected_scenarios
                      .length
                  }
                </strong>

              </div>


              <div>

                <ListOrdered
                  size={17}
                />

                <span>
                  {tr(
                    "Ranking",
                    "Ranking"
                  )}
                </span>

                <strong>
                  {
                    selectedTrace
                      .ranking
                      .length
                  }
                </strong>

              </div>

            </div>

          </section>


          {/* =============================================== */}
          {/* FLOW                                            */}
          {/* =============================================== */}

          <section className="panel trace-flow-panel">

            <div className="trace-flow-heading">

              <div>

                <strong>
                  {tr(
                    "Flujo explicable de la decisión",
                    "Explainable decision flow"
                  )}
                </strong>

                <span>
                  {tr(
                    "Datos persistidos en la DecisionTrace de esta ejecución",
                    "Data persisted in this execution's DecisionTrace"
                  )}
                </span>

              </div>

            </div>


            <div className="trace-flow">

              {/* STAGE 1 */}

              <TraceStage
                number={1}
                icon={
                  <Database
                    size={18}
                  />
                }
                title={tr(
                  "Evidencia utilizada",
                  "Evidence used"
                )}
                description={tr(
                  "Fuentes de máquina referenciadas por la ejecución.",
                  "Machine sources referenced by the execution."
                )}
              >

                <IdentifierList
                  ids={
                    selectedTrace
                      .evidence_ids
                  }
                  emptyText={tr(
                    "La traza no contiene identificadores de evidencia.",
                    "The trace does not contain evidence identifiers."
                  )}
                  initialLimit={
                    10
                  }
                  collapsible
                  tr={
                    tr
                  }
                />

              </TraceStage>


              {/* STAGE 2 */}

              <TraceStage
                number={2}
                icon={
                  <Activity
                    size={18}
                  />
                }
                title={tr(
                  "Transformaciones del estado",
                  "State transformations"
                )}
                description={tr(
                  "Transformaciones registradas antes de evaluar alternativas.",
                  "Transformations recorded before evaluating alternatives."
                )}
              >

                <IdentifierList
                  ids={
                    selectedTrace
                      .transformation_ids
                  }
                  emptyText={tr(
                    "No hay transformaciones registradas en esta traza.",
                    "No transformations were recorded in this trace."
                  )}
                  tr={
                    tr
                  }
                />

              </TraceStage>


              {/* STAGE 3 */}

              <TraceStage
                number={3}
                icon={
                  <BookOpen
                    size={18}
                  />
                }
                title={tr(
                  "Conocimiento y restricciones del agricultor",
                  "Farmer knowledge and constraints"
                )}
                description={tr(
                  "Entradas participativas referenciadas por el motor para contextualizar, restringir o reordenar alternativas.",
                  "Participatory inputs referenced by the engine to contextualize, constrain or reorder alternatives."
                )}
                tone="purple"
              >

                <IdentifierList
                  ids={
                    selectedTrace
                      .knowledge_ids
                  }
                  emptyText={tr(
                    "Esta ejecución no referencia conocimiento del agricultor.",
                    "This execution does not reference farmer knowledge."
                  )}
                  tr={
                    tr
                  }
                />

              </TraceStage>


              {/* STAGE 4 */}

              <TraceStage
                number={4}
                icon={
                  <AlertTriangle
                    size={18}
                  />
                }
                title={tr(
                  "Conflictos detectados",
                  "Detected conflicts"
                )}
                description={tr(
                  "Inconsistencias o desacuerdos preservados para la toma de decisión.",
                  "Inconsistencies or disagreements preserved for decision-making."
                )}
                tone={
                  selectedTrace
                    .conflict_ids
                    .length > 0

                    ? "warning"

                    : "neutral"
                }
              >

                <IdentifierList
                  ids={
                    selectedTrace
                      .conflict_ids
                  }
                  emptyText={tr(
                    "No se registraron conflictos en esta ejecución.",
                    "No conflicts were recorded in this execution."
                  )}
                  tr={
                    tr
                  }
                />

              </TraceStage>


              {/* STAGE 5 */}

              <TraceStage
                number={5}
                icon={
                  <CheckCircle2
                    size={18}
                  />
                }
                title={tr(
                  "Escenarios factibles",
                  "Feasible scenarios"
                )}
                description={tr(
                  "Alternativas que superaron las restricciones duras y continuaron a evaluación.",
                  "Alternatives that satisfied the hard constraints and continued to evaluation."
                )}
                tone="success"
              >

                <ScenarioList
                  items={
                    selectedTrace
                      .feasible_scenarios
                  }
                  variant="feasible"
                  emptyText={tr(
                    "No hay escenarios factibles registrados.",
                    "No feasible scenarios were recorded."
                  )}
                  tr={
                    tr
                  }
                />

              </TraceStage>


              {/* STAGE 6 */}

              <TraceStage
                number={6}
                icon={
                  <CircleX
                    size={18}
                  />
                }
                title={tr(
                  "Escenarios rechazados",
                  "Rejected scenarios"
                )}
                description={tr(
                  "Alternativas descartadas durante la evaluación; se preserva la información registrada por el motor.",
                  "Alternatives discarded during evaluation; the information recorded by the engine is preserved."
                )}
                tone={
                  selectedTrace
                    .rejected_scenarios
                    .length > 0

                    ? "danger"

                    : "neutral"
                }
              >

                <ScenarioList
                  items={
                    selectedTrace
                      .rejected_scenarios
                  }
                  variant="rejected"
                  emptyText={tr(
                    "No se registraron escenarios rechazados.",
                    "No rejected scenarios were recorded."
                  )}
                  tr={
                    tr
                  }
                />

              </TraceStage>


              {/* STAGE 7 */}

              <TraceStage
                number={7}
                icon={
                  <ListOrdered
                    size={18}
                  />
                }
                title={tr(
                  "Ranking multicriterio",
                  "Multi-criteria ranking"
                )}
                description={tr(
                  "Orden de las alternativas persistido por el motor de decisión.",
                  "Ordering of alternatives persisted by the decision engine."
                )}
                tone="purple"
              >

                <ScenarioList
                  items={
                    selectedTrace
                      .ranking
                  }
                  variant="ranking"
                  emptyText={tr(
                    "No se registró ranking para esta ejecución.",
                    "No ranking was recorded for this execution."
                  )}
                  tr={
                    tr
                  }
                />

              </TraceStage>


              {/* STAGE 8 */}

              <TraceStage
                number={8}
                icon={
                  <BrainCircuit
                    size={18}
                  />
                }
                title={tr(
                  "Recomendación provisional",
                  "Provisional recommendation"
                )}
                description={tr(
                  "Salida propuesta por el motor antes de la intervención humana.",
                  "Output proposed by the engine before human intervention."
                )}
                tone="purple"
              >

                <ObjectDetails
                  value={
                    selectedTrace
                      .provisional_recommendation
                  }
                  emptyText={tr(
                    "No existe recomendación provisional persistida.",
                    "No persisted provisional recommendation exists."
                  )}
                  tr={
                    tr
                  }
                />

              </TraceStage>


              {/* STAGE 9 */}

              <TraceStage
                number={9}
                icon={
                  <UserCheck
                    size={18}
                  />
                }
                title={tr(
                  "Respuesta humana (HITL)",
                  "Human response (HITL)"
                )}
                description={tr(
                  "ACCEPT, MODIFY o REJECT. El conocimiento humano se registra sin sobrescribir silenciosamente la evidencia de máquina.",
                  "ACCEPT, MODIFY or REJECT. Human knowledge is recorded without silently overwriting machine evidence."
                )}
                tone={
                  selectedTrace
                    .farmer_response
                    ?.response_type ===
                    "REJECT"

                    ? "danger"

                    : selectedTrace
                        .farmer_response

                      ? "success"

                      : "warning"
                }
              >

                <ObjectDetails
                  value={
                    selectedTrace
                      .farmer_response

                      ? {
                          ...selectedTrace
                            .farmer_response,
                        }

                      : null
                  }
                  emptyText={tr(
                    "Esta DecisionTrace todavía no tiene respuesta humana.",
                    "This DecisionTrace does not yet have a human response."
                  )}
                  tr={
                    tr
                  }
                />

              </TraceStage>


              {/* STAGE 10 */}

              <TraceStage
                number={10}
                icon={
                  <ShieldCheck
                    size={18}
                  />
                }
                title={tr(
                  "Acción final y resultado",
                  "Final action and outcome"
                )}
                description={tr(
                  "Resultado posterior al HITL. La acción final puede diferir de la recomendación provisional o quedar vacía si fue rechazada.",
                  "Result after HITL. The final action may differ from the provisional recommendation or remain empty if it was rejected."
                )}
                tone={
                  selectedTrace
                    .final_action

                    ? "success"

                    : selectedTrace
                        .farmer_response
                        ?.response_type ===
                        "REJECT"

                      ? "danger"

                      : "neutral"
                }
              >

                <div className="trace-final-grid">

                  <div>

                    <h4>
                      {tr(
                        "Acción final",
                        "Final action"
                      )}
                    </h4>

                    <ObjectDetails
                      value={
                        selectedTrace
                          .final_action
                      }
                      emptyText={tr(
                        "Sin acción final registrada.",
                        "No final action recorded."
                      )}
                      tr={
                        tr
                      }
                    />

                  </div>


                  <div>

                    <h4>
                      {tr(
                        "Resultado",
                        "Outcome"
                      )}
                    </h4>

                    <ObjectDetails
                      value={
                        selectedTrace
                          .outcome
                      }
                      emptyText={tr(
                        "Sin resultado adicional registrado.",
                        "No additional outcome recorded."
                      )}
                      tr={
                        tr
                      }
                    />

                  </div>

                </div>

              </TraceStage>

            </div>

          </section>


          {/* =============================================== */}
          {/* TECHNICAL METADATA                              */}
          {/* =============================================== */}

          <section className="panel trace-technical-panel">

            <button
              type="button"
              className="trace-technical-toggle"
              onClick={() =>
                setShowTechnical(
                  (
                    current
                  ) =>
                    !current
                )
              }
            >

              <div>

                <strong>
                  {tr(
                    "Metadatos técnicos de la ejecución",
                    "Execution technical metadata"
                  )}
                </strong>

                <span>
                  {tr(
                    "Información adicional persistida por el motor",
                    "Additional information persisted by the engine"
                  )}
                </span>

              </div>


              {showTechnical

                ? (
                    <ChevronUp
                      size={18}
                    />
                  )

                : (
                    <ChevronDown
                      size={18}
                    />
                  )}

            </button>


            {showTechnical && (

              <div className="trace-technical-content">

                <ObjectDetails
                  value={
                    selectedTrace
                      .metadata
                  }
                  emptyText={tr(
                    "La traza no contiene metadatos adicionales.",
                    "The trace does not contain additional metadata."
                  )}
                  tr={
                    tr
                  }
                />

              </div>
            )}

          </section>

        </main>

      </div>

    </div>
  );
}