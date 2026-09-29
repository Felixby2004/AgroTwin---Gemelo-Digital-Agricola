import {
  useEffect,
  useMemo,
  useState,
} from "react";

import axios from "axios";

import {
  CheckCircle2,
  CircleX,
  Droplets,
  History,
  PencilLine,
  RefreshCw,
  ShieldAlert,
} from "lucide-react";

import {
  getDecisionTracesByParcel,
  registerFarmerResponse,
  type DecisionTrace,
} from "../../api/decisionTraces";

import {
  useLanguage,
} from "../../i18n/LanguageContext";

import {
  HelpTooltip,
} from "../help/HelpTooltip";


interface FarmerDecisionPanelProps {
  parcelId: string;

  onChanged?:
    () =>
      void
      |
      Promise<void>;
}


type DecisionMode =
  | "ACCEPT"
  | "MODIFY"
  | "REJECT"
  | null;


type Translate = (
  es: string,
  en: string
) => string;


/* ===================================================== */
/* API ERROR                                             */
/* ===================================================== */

function getApiError(
  error: unknown,
  tr: Translate
): string {

  if (
    axios.isAxiosError(
      error
    )
  ) {

    const detail =
      error
        .response
        ?.data
        ?.detail;


    if (
      typeof detail ===
      "string"
    ) {
      return detail;
    }


    if (
      Array.isArray(
        detail
      )
    ) {

      return detail
        .map(
          (
            item
          ) =>
            item?.msg
            ??
            tr(
              "Error de validación.",
              "Validation error."
            )
        )
        .join(
          " "
        );
    }
  }


  return tr(
    "No se pudo registrar la respuesta del agricultor.",
    "Could not register the farmer response."
  );
}


/* ===================================================== */
/* HELPERS                                               */
/* ===================================================== */

function getIrrigationMm(
  trace:
    | DecisionTrace
    | null
): number | null {

  const value =
    trace
      ?.provisional_recommendation
      ?.irrigation_mm;


  return typeof value ===
    "number"

    ? value

    : null;
}


function getFinalIrrigationMm(
  trace: DecisionTrace
): number | null {

  const value =
    trace
      ?.final_action
      ?.irrigation_mm;


  return typeof value ===
    "number"

    ? value

    : null;
}


function getDecisionLabel(
  trace: DecisionTrace,
  tr: Translate
): string {

  const responseType =
    trace
      .farmer_response
      ?.response_type;


  switch (
    responseType
  ) {

    case "ACCEPT":

      return tr(
        "Aceptada",
        "Accepted"
      );


    case "MODIFY":

      return tr(
        "Modificada",
        "Modified"
      );


    case "REJECT":

      return tr(
        "Rechazada",
        "Rejected"
      );


    default:

      return tr(
        "Pendiente",
        "Pending"
      );
  }
}


function getDecisionClass(
  trace: DecisionTrace
): string {

  const responseType =
    trace
      .farmer_response
      ?.response_type;


  switch (
    responseType
  ) {

    case "ACCEPT":
      return "accept";


    case "MODIFY":
      return "modify";


    case "REJECT":
      return "reject";


    default:
      return "pending";
  }
}


function getDecisionSummary(
  trace: DecisionTrace,
  tr: Translate
): string {

  const responseType =
    trace
      .farmer_response
      ?.response_type;


  const recommendedMm =
    getIrrigationMm(
      trace
    );


  const finalMm =
    getFinalIrrigationMm(
      trace
    );


  if (
    responseType ===
    "ACCEPT"
  ) {

    if (
      finalMm !== null
    ) {

      return tr(
        `Se confirmó la recomendación de aplicar ${finalMm} mm de riego.`,
        `The recommendation to apply ${finalMm} mm of irrigation was confirmed.`
      );
    }


    if (
      recommendedMm !==
      null
    ) {

      return tr(
        `Se aceptó la recomendación de aplicar ${recommendedMm} mm de riego.`,
        `The recommendation to apply ${recommendedMm} mm of irrigation was accepted.`
      );
    }


    return tr(
      "La recomendación fue aceptada por el agricultor.",
      "The recommendation was accepted by the farmer."
    );
  }


  if (
    responseType ===
    "MODIFY"
  ) {

    if (
      recommendedMm !==
        null
      &&
      finalMm !==
        null
    ) {

      return tr(
        `La recomendación cambió de ${recommendedMm} mm a ${finalMm} mm.`,
        `The recommendation changed from ${recommendedMm} mm to ${finalMm} mm.`
      );
    }


    if (
      finalMm !== null
    ) {

      return tr(
        `El agricultor definió una acción final de ${finalMm} mm de riego.`,
        `The farmer defined a final irrigation action of ${finalMm} mm.`
      );
    }


    return tr(
      "La recomendación fue modificada por el agricultor.",
      "The recommendation was modified by the farmer."
    );
  }


  if (
    responseType ===
    "REJECT"
  ) {

    return tr(
      "La recomendación fue rechazada. No se registró una acción final de riego.",
      "The recommendation was rejected. No final irrigation action was recorded."
    );
  }


  if (
    recommendedMm !==
    null
  ) {

    return tr(
      `Recomendación de ${recommendedMm} mm pendiente de respuesta del agricultor.`,
      `Recommendation of ${recommendedMm} mm pending farmer response.`
    );
  }


  return tr(
    "Recomendación pendiente de respuesta del agricultor.",
    "Recommendation pending farmer response."
  );
}


/* ===================================================== */
/* COMPONENT                                             */
/* ===================================================== */

export function FarmerDecisionPanel({
  parcelId,
  onChanged,
}: FarmerDecisionPanelProps) {

  const {
    language,
    tr,
  } = useLanguage();


  const [
    traces,
    setTraces,
  ] =
    useState<
      DecisionTrace[]
    >([]);


  const [
    loading,
    setLoading,
  ] =
    useState(
      true
    );


  const [
    submitting,
    setSubmitting,
  ] =
    useState(
      false
    );


  const [
    mode,
    setMode,
  ] =
    useState<
      DecisionMode
    >(
      null
    );


  const [
    irrigationMm,
    setIrrigationMm,
  ] =
    useState(
      ""
    );


  const [
    rationale,
    setRationale,
  ] =
    useState(
      ""
    );


  const [
    error,
    setError,
  ] =
    useState(
      ""
    );


  const [
    success,
    setSuccess,
  ] =
    useState(
      ""
    );


  /* =================================================== */
  /* LOAD TRACES                                         */
  /* =================================================== */

  const loadTraces =
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


      } catch (
        loadError
      ) {

        setError(
          getApiError(
            loadError,
            tr
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

      void loadTraces();

    },
    [
      parcelId,
    ]
  );


  /* =================================================== */
  /* CURRENT PENDING TRACE                               */
  /* =================================================== */

  const pendingTrace =
    useMemo(
      () =>

        traces.find(
          (
            trace
          ) =>
            trace
              .farmer_response ===
              null
            &&
            trace
              .provisional_recommendation !==
              null
        )
        ??
        null,

      [
        traces,
      ]
    );


  const recentTraces =
    traces.slice(
      0,
      4
    );


  /* =================================================== */
  /* SELECT DECISION                                     */
  /* =================================================== */

  const selectMode =
    (
      nextMode:
        Exclude<
          DecisionMode,
          null
        >
    ) => {

      setMode(
        nextMode
      );

      setError(
        ""
      );

      setSuccess(
        ""
      );


      if (
        nextMode ===
        "MODIFY"
      ) {

        const recommended =
          getIrrigationMm(
            pendingTrace
          );


        setIrrigationMm(
          recommended !==
            null

            ? String(
                recommended
              )

            : ""
        );


      } else {

        setIrrigationMm(
          ""
        );
      }
    };


  /* =================================================== */
  /* SUBMIT                                              */
  /* =================================================== */

  const submitResponse =
    async () => {

      if (
        !pendingTrace
        ||
        !mode
      ) {
        return;
      }


      if (
        mode ===
        "MODIFY"
      ) {

        const numericValue =
          Number(
            irrigationMm
          );


        if (
          !Number.isFinite(
            numericValue
          )
          ||
          numericValue < 0
        ) {

          setError(
            tr(
              "Ingresa una dosis de riego válida.",
              "Enter a valid irrigation amount."
            )
          );

          return;
        }
      }


      if (
        mode ===
          "REJECT"
        &&
        !rationale.trim()
      ) {

        setError(
          tr(
            "El rechazo requiere una justificación.",
            "A rejection requires a rationale."
          )
        );

        return;
      }


      setSubmitting(
        true
      );

      setError(
        ""
      );

      setSuccess(
        ""
      );


      try {

        const result =
          await registerFarmerResponse(
            pendingTrace
              .trace_id,
            {

              response_type:
                mode,

              modified_action:
                mode ===
                  "MODIFY"

                  ? {
                      irrigation_mm:
                        Number(
                          irrigationMm
                        ),
                    }

                  : null,

              rationale:
                rationale
                  .trim()
                ||
                null,
            }
          );


        const finalMm =
          result
            .final_action
            ?.irrigation_mm;


        if (
          mode ===
          "ACCEPT"
        ) {

          setSuccess(
            typeof finalMm ===
              "number"

              ? tr(
                  `Decisión registrada: se aceptó aplicar ${finalMm} mm de riego.`,
                  `Decision recorded: applying ${finalMm} mm of irrigation was accepted.`
                )

              : tr(
                  "Decisión registrada: la recomendación fue aceptada.",
                  "Decision recorded: the recommendation was accepted."
                )
          );


        } else if (
          mode ===
          "MODIFY"
        ) {

          setSuccess(
            tr(
              `Decisión registrada: la dosis final será de ${irrigationMm} mm.`,
              `Decision recorded: the final irrigation amount will be ${irrigationMm} mm.`
            )
          );


        } else {

          setSuccess(
            tr(
              "Decisión registrada: la recomendación fue rechazada y quedó guardada en la trazabilidad.",
              "Decision recorded: the recommendation was rejected and stored in the traceability record."
            )
          );
        }


        setMode(
          null
        );

        setRationale(
          ""
        );

        setIrrigationMm(
          ""
        );


        await loadTraces();


        if (
          onChanged
        ) {

          await onChanged();
        }


      } catch (
        submitError
      ) {

        setError(
          getApiError(
            submitError,
            tr
          )
        );


      } finally {

        setSubmitting(
          false
        );
      }
    };


  /* =================================================== */
  /* VIEW                                                */
  /* =================================================== */

  return (

    <section className="panel hitl-panel">

      {/* =============================================== */}
      {/* HEADER                                          */}
      {/* =============================================== */}

      <div className="panel-header">

        <div className="panel-header-title">

          <div className="panel-icon">

            <Droplets
              size={20}
            />

          </div>


          <div>

            <h2>

              {tr(
                "Decisión participativa",
                "Participatory decision"
              )}

              <HelpTooltip
                term={tr(
                  "Decisión participativa",
                  "Participatory decision"
                )}
                text={tr(
                  "Permite al agricultor aceptar, modificar o rechazar la recomendación propuesta por el sistema. La respuesta queda registrada en la trazabilidad.",
                  "Allows the farmer to accept, modify or reject the recommendation proposed by the system. The response is recorded in the traceability record."
                )}
              />

            </h2>


            <p>
              {tr(
                "Revise la recomendación y confirme qué desea hacer",
                "Review the recommendation and confirm what you want to do"
              )}
            </p>

          </div>

        </div>


        <button
          className="text-button"
          onClick={() =>
            void loadTraces()
          }
          disabled={
            loading
          }
        >

          <RefreshCw
            size={14}
          />

          {tr(
            "Actualizar",
            "Refresh"
          )}

        </button>

      </div>


      <div className="hitl-content">

        {/* ============================================= */}
        {/* LOADING                                       */}
        {/* ============================================= */}

        {loading ? (

          <div className="hitl-empty">

            {tr(
              "Cargando decisiones...",
              "Loading decisions..."
            )}

          </div>

        ) : pendingTrace ? (

          <>

            {/* ========================================= */}
            {/* PENDING RECOMMENDATION                    */}
            {/* ========================================= */}

            <div className="hitl-recommendation">

              <span>
                {tr(
                  "Recomendación pendiente de respuesta",
                  "Recommendation pending response"
                )}
              </span>


              <strong>

                {getIrrigationMm(
                  pendingTrace
                ) ?? "—"}

                <small>
                  mm
                </small>

              </strong>


              <p className="hitl-recommendation-help">

                {tr(
                  "El sistema propone esta dosis de riego. Usted puede aceptarla, cambiarla o rechazarla.",
                  "The system proposes this irrigation amount. You can accept, modify or reject it."
                )}

              </p>


              <em>

                {tr(
                  "ID técnico:",
                  "Technical ID:"
                )}{" "}

                {
                  pendingTrace
                    .trace_id
                }

              </em>

            </div>


            {/* ========================================= */}
            {/* ACTION BUTTONS                            */}
            {/* ========================================= */}

            <div className="hitl-actions">

              <button
                className={
                  mode ===
                    "ACCEPT"

                    ? "hitl-action accept selected"

                    : "hitl-action accept"
                }
                onClick={() =>
                  selectMode(
                    "ACCEPT"
                  )
                }
              >

                <CheckCircle2
                  size={18}
                />

                {tr(
                  "Aceptar recomendación",
                  "Accept recommendation"
                )}

              </button>


              <button
                className={
                  mode ===
                    "MODIFY"

                    ? "hitl-action modify selected"

                    : "hitl-action modify"
                }
                onClick={() =>
                  selectMode(
                    "MODIFY"
                  )
                }
              >

                <PencilLine
                  size={18}
                />

                {tr(
                  "Cambiar dosis",
                  "Change amount"
                )}

              </button>


              <button
                className={
                  mode ===
                    "REJECT"

                    ? "hitl-action reject selected"

                    : "hitl-action reject"
                }
                onClick={() =>
                  selectMode(
                    "REJECT"
                  )
                }
              >

                <CircleX
                  size={18}
                />

                {tr(
                  "Rechazar recomendación",
                  "Reject recommendation"
                )}

              </button>

            </div>


            {/* ========================================= */}
            {/* RESPONSE FORM                             */}
            {/* ========================================= */}

            {mode && (

              <div className="hitl-response-form">

                {/* ACCEPT */}

                {mode ===
                  "ACCEPT" && (

                  <div className="hitl-decision-explanation accept">

                    <strong>
                      {tr(
                        "¿Qué ocurrirá?",
                        "What will happen?"
                      )}
                    </strong>

                    <span>
                      {tr(
                        "Se registrará que acepta la dosis recomendada por el sistema.",
                        "Your acceptance of the irrigation amount recommended by the system will be recorded."
                      )}
                    </span>

                  </div>
                )}


                {/* MODIFY */}

                {mode ===
                  "MODIFY" && (

                  <>

                    <div className="hitl-decision-explanation modify">

                      <strong>
                        {tr(
                          "¿Qué ocurrirá?",
                          "What will happen?"
                        )}
                      </strong>

                      <span>
                        {tr(
                          "Puede indicar otra dosis. El sistema comprobará automáticamente que no viole restricciones obligatorias.",
                          "You can specify a different amount. The system will automatically verify that it does not violate mandatory constraints."
                        )}
                      </span>

                    </div>


                    <label>

                      {tr(
                        "Nueva dosis de riego",
                        "New irrigation amount"
                      )}


                      <div className="hitl-number-input">

                        <input
                          type="number"
                          min="0"
                          step="1"
                          value={
                            irrigationMm
                          }
                          onChange={
                            (
                              event
                            ) =>
                              setIrrigationMm(
                                event
                                  .target
                                  .value
                              )
                          }
                        />

                        <span>
                          mm
                        </span>

                      </div>

                    </label>

                  </>
                )}


                {/* REJECT */}

                {mode ===
                  "REJECT" && (

                  <div className="hitl-decision-explanation reject">

                    <strong>
                      {tr(
                        "¿Qué ocurrirá?",
                        "What will happen?"
                      )}
                    </strong>

                    <span>
                      {tr(
                        "No se registrará una acción final de riego para esta recomendación y el motivo quedará guardado.",
                        "No final irrigation action will be recorded for this recommendation, and the reason will be stored."
                      )}
                    </span>

                  </div>
                )}


                {/* RATIONALE */}

                <label>

                  {mode ===
                    "REJECT"

                    ? tr(
                        "¿Por qué rechaza la recomendación?",
                        "Why are you rejecting the recommendation?"
                      )

                    : tr(
                        "Comentario del agricultor",
                        "Farmer comment"
                      )}


                  <textarea
                    rows={3}
                    value={
                      rationale
                    }
                    onChange={
                      (
                        event
                      ) =>
                        setRationale(
                          event
                            .target
                            .value
                        )
                    }
                    placeholder={
                      mode ===
                        "REJECT"

                        ? tr(
                            "Explique brevemente por qué no aplicará esta recomendación...",
                            "Briefly explain why you will not apply this recommendation..."
                          )

                        : tr(
                            "Comentario opcional sobre su decisión...",
                            "Optional comment about your decision..."
                          )
                    }
                  />

                </label>


                {/* FORM ACTIONS */}

                <div className="hitl-form-actions">

                  <button
                    className="button-secondary"
                    onClick={() => {

                      setMode(
                        null
                      );

                      setError(
                        ""
                      );
                    }}
                    disabled={
                      submitting
                    }
                  >

                    {tr(
                      "Cancelar",
                      "Cancel"
                    )}

                  </button>


                  <button
                    className="button-primary"
                    onClick={() =>
                      void submitResponse()
                    }
                    disabled={
                      submitting
                    }
                  >

                    {submitting
                      ? tr(
                          "Registrando...",
                          "Saving..."
                        )
                      : tr(
                          "Confirmar decisión",
                          "Confirm decision"
                        )}

                  </button>

                </div>

              </div>
            )}

          </>

        ) : (

          /* ============================================= */
          /* NO PENDING RECOMMENDATIONS                    */
          /* ============================================= */

          <div className="hitl-empty">

            <CheckCircle2
              size={26}
            />

            <strong>
              {tr(
                "No hay recomendaciones pendientes",
                "No pending recommendations"
              )}
            </strong>

            <span>
              {tr(
                "Las decisiones anteriores permanecen guardadas en el historial y la trazabilidad.",
                "Previous decisions remain stored in the history and traceability record."
              )}
            </span>

          </div>
        )}


        {/* ============================================= */}
        {/* ERROR                                         */}
        {/* ============================================= */}

        {error && (

          <div className="hitl-message error-message">

            <ShieldAlert
              size={16}
            />

            {error}

          </div>
        )}


        {/* ============================================= */}
        {/* SUCCESS                                       */}
        {/* ============================================= */}

        {success && (

          <div className="hitl-message success-message">

            <CheckCircle2
              size={16}
            />

            {success}

          </div>
        )}


        {/* ============================================= */}
        {/* HISTORY                                       */}
        {/* ============================================= */}

        {recentTraces.length >
          0 && (

          <div className="hitl-history">

            <div className="hitl-history-title">

              <History
                size={15}
              />

              <strong>
                {tr(
                  "Decisiones recientes",
                  "Recent decisions"
                )}
              </strong>

              <HelpTooltip
                term={tr(
                  "Decisiones recientes",
                  "Recent decisions"
                )}
                text={tr(
                  "Historial de recomendaciones y respuestas del agricultor. El ID técnico se conserva para auditoría y trazabilidad.",
                  "History of recommendations and farmer responses. The technical ID is preserved for audit and traceability."
                )}
              />

            </div>


            {recentTraces.map(
              (
                trace
              ) => (

                <div
                  className="hitl-history-row hitl-history-row-friendly"
                  key={
                    trace.trace_id
                  }
                >

                  <div className="hitl-history-main">

                    <div className="hitl-history-heading">

                      <strong>
                        {getDecisionLabel(
                          trace,
                          tr
                        )}
                      </strong>


                      <span
                        className={
                          `hitl-status-badge ${
                            getDecisionClass(
                              trace
                            )
                          }`
                        }
                      >
                        {getDecisionLabel(
                          trace,
                          tr
                        )}
                      </span>

                    </div>


                    <p>
                      {getDecisionSummary(
                        trace,
                        tr
                      )}
                    </p>


                    <span>

                      {new Date(
                        trace.created_at
                      ).toLocaleString(
                        language ===
                          "es"

                          ? "es-PE"

                          : "en-US"
                      )}

                    </span>


                    <em>

                      {tr(
                        "ID técnico:",
                        "Technical ID:"
                      )}{" "}

                      {trace.trace_id}

                    </em>

                  </div>

                </div>
              )
            )}

          </div>
        )}

      </div>

    </section>
  );
}