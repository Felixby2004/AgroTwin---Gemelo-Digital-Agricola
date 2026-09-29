import {
  useMemo,
  useState,
} from "react";

import axios from "axios";

import {
  BookOpenCheck,
  CheckCircle2,
  CircleAlert,
  CloudRain,
  Droplets,
  Gauge,
  Leaf,
  Save,
  ShieldCheck,
  SlidersHorizontal,
  Sprout,
} from "lucide-react";

import {
  createFarmerKnowledge,
  type ConstraintType,
  type FarmerKnowledgeType,
} from "../../api/farmerKnowledge";

import {
  useLanguage,
} from "../../i18n/LanguageContext";


interface FarmerKnowledgeFormProps {
  parcelId: string;

  onCreated?:
    () =>
      void
      |
      Promise<void>;
}


interface ObservationOption {
  labelEs: string;
  labelEn: string;

  value: string;

  unit: string;

  placeholderEs: string;
  placeholderEn: string;
}


interface EventOption {
  labelEs: string;
  labelEn: string;

  value: string;
}


interface ConstraintPreset {
  labelEs: string;
  labelEn: string;

  variable: string;

  unit: string;

  operator:
    | "<="
    | ">=";

  questionEs: string;
  questionEn: string;

  placeholderEs: string;
  placeholderEn: string;
}


interface PreferenceOption {
  labelEs: string;
  labelEn: string;

  code: string;

  variable:
    | string
    | null;

  descriptionEs: string;
  descriptionEn: string;
}


type Translate = (
  es: string,
  en: string
) => string;


/* ===================================================== */
/* OPTIONS                                               */
/* ===================================================== */

const OBSERVATION_OPTIONS:
ObservationOption[] = [

  {
    labelEs:
      "Humedad del suelo",

    labelEn:
      "Soil moisture",

    value:
      "soil_moisture",

    unit:
      "m³/m³",

    placeholderEs:
      "Ej. 0.22",

    placeholderEn:
      "e.g. 0.22",
  },

  {
    labelEs:
      "Temperatura del aire",

    labelEn:
      "Air temperature",

    value:
      "air_temperature",

    unit:
      "°C",

    placeholderEs:
      "Ej. 28",

    placeholderEn:
      "e.g. 28",
  },

  {
    labelEs:
      "Temperatura del suelo",

    labelEn:
      "Soil temperature",

    value:
      "soil_temperature",

    unit:
      "°C",

    placeholderEs:
      "Ej. 24",

    placeholderEn:
      "e.g. 24",
  },

  {
    labelEs:
      "Lluvia observada",

    labelEn:
      "Observed rainfall",

    value:
      "rainfall",

    unit:
      "mm",

    placeholderEs:
      "Ej. 12",

    placeholderEn:
      "e.g. 12",
  },

  {
    labelEs:
      "Humedad relativa",

    labelEn:
      "Relative humidity",

    value:
      "relative_humidity",

    unit:
      "%",

    placeholderEs:
      "Ej. 68",

    placeholderEn:
      "e.g. 68",
  },
];


const EVENT_OPTIONS:
EventOption[] = [

  {
    labelEs:
      "Riego realizado",

    labelEn:
      "Irrigation performed",

    value:
      "IRRIGATION_EVENT",
  },

  {
    labelEs:
      "Lluvia observada",

    labelEn:
      "Observed rainfall",

    value:
      "RAINFALL_EVENT",
  },

  {
    labelEs:
      "Fertilización",

    labelEn:
      "Fertilization",

    value:
      "FERTILIZATION_EVENT",
  },

  {
    labelEs:
      "Aplicación fitosanitaria",

    labelEn:
      "Phytosanitary application",

    value:
      "PHYTOSANITARY_EVENT",
  },

  {
    labelEs:
      "Siembra",

    labelEn:
      "Sowing",

    value:
      "SOWING_EVENT",
  },

  {
    labelEs:
      "Cosecha",

    labelEn:
      "Harvest",

    value:
      "HARVEST_EVENT",
  },

  {
    labelEs:
      "Falla o mantenimiento de sensor",

    labelEn:
      "Sensor failure or maintenance",

    value:
      "SENSOR_EVENT",
  },

  {
    labelEs:
      "Plaga o enfermedad",

    labelEn:
      "Pest or disease",

    value:
      "PEST_DISEASE_EVENT",
  },

  {
    labelEs:
      "Daño o estrés visible del cultivo",

    labelEn:
      "Visible crop damage or stress",

    value:
      "CROP_STRESS_EVENT",
  },

  {
    labelEs:
      "Otro evento de campo",

    labelEn:
      "Other field event",

    value:
      "FIELD_EVENT",
  },
];


const CONSTRAINT_PRESETS:
ConstraintPreset[] = [

  {
    labelEs:
      "Máximo de riego por evento",

    labelEn:
      "Maximum irrigation per event",

    variable:
      "irrigation_mm",

    unit:
      "mm",

    operator:
      "<=",

    questionEs:
      "¿Cuál es el máximo de agua que puede aplicar en un evento de riego?",

    questionEn:
      "What is the maximum amount of water that can be applied in one irrigation event?",

    placeholderEs:
      "Ej. 20",

    placeholderEn:
      "e.g. 20",
  },

  {
    labelEs:
      "Mínimo de riego por evento",

    labelEn:
      "Minimum irrigation per event",

    variable:
      "irrigation_mm",

    unit:
      "mm",

    operator:
      ">=",

    questionEs:
      "¿Cuál es el mínimo de agua que considera útil aplicar por evento?",

    questionEn:
      "What is the minimum amount of water you consider useful to apply per event?",

    placeholderEs:
      "Ej. 5",

    placeholderEn:
      "e.g. 5",
  },
];


const PREFERENCE_OPTIONS:
PreferenceOption[] = [

  {
    labelEs:
      "Ahorrar agua",

    labelEn:
      "Save water",

    code:
      "WATER_SAVING",

    variable:
      "irrigation_mm",

    descriptionEs:
      "Priorizar alternativas que utilicen menos agua cuando sea razonable.",

    descriptionEn:
      "Prioritize alternatives that use less water when reasonable.",
  },

  {
    labelEs:
      "Maximizar rendimiento",

    labelEn:
      "Maximize yield",

    code:
      "YIELD_PRIORITY",

    variable:
      "irrigation_mm",

    descriptionEs:
      "Dar mayor importancia al rendimiento esperado del cultivo.",

    descriptionEn:
      "Give greater importance to expected crop yield.",
  },

  {
    labelEs:
      "Reducir riesgo hídrico",

    labelEn:
      "Reduce water risk",

    code:
      "WATER_RISK_REDUCTION",

    variable:
      "irrigation_mm",

    descriptionEs:
      "Favorecer decisiones conservadoras frente a déficit o incertidumbre hídrica.",

    descriptionEn:
      "Favor conservative decisions when facing water deficit or uncertainty.",
  },

  {
    labelEs:
      "Reducir frecuencia de riego",

    labelEn:
      "Reduce irrigation frequency",

    code:
      "LOWER_IRRIGATION_FREQUENCY",

    variable:
      "irrigation_mm",

    descriptionEs:
      "Preferir menos intervenciones de riego cuando las alternativas sean similares.",

    descriptionEn:
      "Prefer fewer irrigation interventions when alternatives are similar.",
  },

  {
    labelEs:
      "Reducir costos operativos",

    labelEn:
      "Reduce operating costs",

    code:
      "COST_SAVING",

    variable:
      null,

    descriptionEs:
      "Favorecer decisiones que eviten intervenciones innecesarias.",

    descriptionEn:
      "Favor decisions that avoid unnecessary interventions.",
  },
];


/* ===================================================== */
/* HELPERS                                               */
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
    "No se pudo registrar el conocimiento del agricultor.",
    "Could not register the farmer knowledge."
  );
}


function parseNumber(
  value: string
): number | null {

  const numeric =
    Number(
      value
    );


  return Number.isFinite(
    numeric
  )
    ? numeric
    : null;
}


/* ===================================================== */
/* COMPONENT                                             */
/* ===================================================== */

export function FarmerKnowledgeForm(
  {
    parcelId,
    onCreated,
  }:
    FarmerKnowledgeFormProps
) {

  const {
    tr,
  } = useLanguage();


  const [
    knowledgeType,
    setKnowledgeType,
  ] = useState<
    FarmerKnowledgeType
  >(
    "OBSERVATION"
  );


  const [
    observationVariable,
    setObservationVariable,
  ] = useState(
    OBSERVATION_OPTIONS[0]
      .value
  );


  const [
    observationValue,
    setObservationValue,
  ] = useState(
    ""
  );


  const [
    eventType,
    setEventType,
  ] = useState(
    EVENT_OPTIONS[0]
      .value
  );


  const [
    constraintPreset,
    setConstraintPreset,
  ] = useState(
    CONSTRAINT_PRESETS[0]
      .variable
      +
      "|"
      +
      CONSTRAINT_PRESETS[0]
        .operator
  );


  const [
    constraintValue,
    setConstraintValue,
  ] = useState(
    ""
  );


  const [
    constraintRequired,
    setConstraintRequired,
  ] = useState(
    true
  );


  const [
    preferenceCode,
    setPreferenceCode,
  ] = useState(
    PREFERENCE_OPTIONS[0]
      .code
  );


  const [
    priority,
    setPriority,
  ] = useState(
    "MEDIUM"
  );


  const [
    note,
    setNote,
  ] = useState(
    ""
  );


  const [
    confidence,
    setConfidence,
  ] = useState(
    "0.80"
  );


  const [
    submitting,
    setSubmitting,
  ] = useState(
    false
  );


  const [
    error,
    setError,
  ] = useState(
    ""
  );


  const [
    success,
    setSuccess,
  ] = useState(
    ""
  );


  /* =================================================== */
  /* SELECTED OPTIONS                                    */
  /* =================================================== */

  const observationOption =
    useMemo(
      () =>
        OBSERVATION_OPTIONS
          .find(
            (
              option
            ) =>
              option.value ===
              observationVariable
          )
        ??
        OBSERVATION_OPTIONS[0],

      [
        observationVariable,
      ]
    );


  const selectedConstraint =
    useMemo(
      () => {

        const [
          variable,
          operator,
        ] =
          constraintPreset
            .split(
              "|"
            );


        return (
          CONSTRAINT_PRESETS
            .find(
              (
                preset
              ) =>
                preset.variable ===
                  variable
                &&
                preset.operator ===
                  operator
            )
          ??
          CONSTRAINT_PRESETS[0]
        );
      },

      [
        constraintPreset,
      ]
    );


  const selectedPreference =
    useMemo(
      () =>
        PREFERENCE_OPTIONS
          .find(
            (
              option
            ) =>
              option.code ===
              preferenceCode
          )
        ??
        PREFERENCE_OPTIONS[0],

      [
        preferenceCode,
      ]
    );


  /* =================================================== */
  /* RESET                                               */
  /* =================================================== */

  const resetTransientFields =
    () => {

      setObservationValue(
        ""
      );

      setConstraintValue(
        ""
      );

      setNote(
        ""
      );

      setConfidence(
        "0.80"
      );
    };


  /* =================================================== */
  /* SUBMIT                                              */
  /* =================================================== */

  const submit =
    async () => {

      setError(
        ""
      );

      setSuccess(
        ""
      );


      const confidenceValue =
        parseNumber(
          confidence
        );


      if (
        confidenceValue ===
          null
        ||
        confidenceValue < 0
        ||
        confidenceValue > 1
      ) {

        setError(
          tr(
            "La confianza debe estar entre 0 y 1.",
            "Confidence must be between 0 and 1."
          )
        );

        return;
      }


      let payload:
        Record<
          string,
          unknown
        >;


      let affects:
        string[] = [];


      let constraintType:
        ConstraintType
        |
        null =
          null;


      let rationale:
        string
        |
        null =
          note.trim()
          ||
          null;


      /* ================================================= */
      /* OBSERVATION                                       */
      /* ================================================= */

      if (
        knowledgeType ===
        "OBSERVATION"
      ) {

        const numericValue =
          parseNumber(
            observationValue
          );


        if (
          numericValue ===
          null
        ) {

          setError(
            tr(
              "Ingresa un valor numérico para la observación.",
              "Enter a numeric value for the observation."
            )
          );

          return;
        }


        payload = {

          variable:
            observationOption
              .value,

          value:
            numericValue,

          unit:
            observationOption
              .unit,

          observation:
            rationale,
        };


        affects = [
          observationOption
            .value,
        ];


      /* ================================================= */
      /* EVENT                                             */
      /* ================================================= */

      } else if (
        knowledgeType ===
        "EVENT"
      ) {

        if (
          !note.trim()
        ) {

          setError(
            tr(
              "Describe brevemente qué ocurrió en la parcela.",
              "Briefly describe what happened in the parcel."
            )
          );

          return;
        }


        payload = {

          event_type:
            eventType,

          description:
            note.trim(),

          occurred_at:
            new Date()
              .toISOString(),
        };


      /* ================================================= */
      /* CONSTRAINT                                        */
      /* ================================================= */

      } else if (
        knowledgeType ===
        "CONSTRAINT"
      ) {

        const numericLimit =
          parseNumber(
            constraintValue
          );


        if (
          numericLimit ===
          null
        ) {

          setError(
            tr(
              "Ingresa un límite numérico válido.",
              "Enter a valid numeric limit."
            )
          );

          return;
        }


        payload = {

          variable:
            selectedConstraint
              .variable,

          operator:
            selectedConstraint
              .operator,

          value:
            numericLimit,

          unit:
            selectedConstraint
              .unit,
        };


        affects = [
          selectedConstraint
            .variable,
        ];


        constraintType =
          constraintRequired
            ? "HARD"
            : "SOFT";


      /* ================================================= */
      /* PREFERENCE                                        */
      /* ================================================= */

      } else if (
        knowledgeType ===
        "PREFERENCE"
      ) {

        payload = {

          variable:
            selectedPreference
              .variable,

          preference:
            selectedPreference
              .code,

          /*
           * Canonical internal label.
           * We keep it stable regardless of the UI language.
           */
          label:
            selectedPreference
              .labelEs,

          priority,
        };


        if (
          selectedPreference
            .variable
        ) {

          affects = [
            selectedPreference
              .variable,
          ];
        }


        if (
          !rationale
        ) {

          /*
           * Keep the persisted fallback rationale stable.
           * Only the presentation layer is translated.
           */
          rationale =
            selectedPreference
              .descriptionEs;
        }


      /* ================================================= */
      /* LOCAL KNOWLEDGE                                   */
      /* ================================================= */

      } else {

        if (
          !note.trim()
        ) {

          setError(
            tr(
              "Describe el conocimiento local que desea aportar.",
              "Describe the local knowledge you want to contribute."
            )
          );

          return;
        }


        payload = {

          statement:
            note.trim(),

          context:
            "FARMER_LOCAL_KNOWLEDGE",
        };
      }


      setSubmitting(
        true
      );


      try {

        const result =
          await createFarmerKnowledge(
            {

              parcel_id:
                parcelId,

              knowledge_type:
                knowledgeType,

              payload,

              affects,

              constraint_type:
                constraintType,

              rationale,

              reported_confidence:
                confidenceValue,

              metadata: {

                user_entered:
                  true,

                farmer_friendly_form:
                  true,

                does_not_overwrite_machine_evidence:
                  true,
              },
            }
          );


        setSuccess(
          tr(
            `Conocimiento registrado: ${result.knowledge_id}`,
            `Knowledge recorded: ${result.knowledge_id}`
          )
        );


        resetTransientFields();


        if (
          onCreated
        ) {

          await onCreated();
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

    <section className="panel farmer-knowledge-panel">

      {/* ================================================= */}
      {/* HEADER                                            */}
      {/* ================================================= */}

      <div className="panel-header">

        <div className="panel-header-title">

          <div className="panel-icon purple-icon">

            <BookOpenCheck
              size={20}
            />

          </div>


          <div>

            <h2>
              {tr(
                "Conocimiento del agricultor",
                "Farmer knowledge"
              )}
            </h2>

            <p>
              {tr(
                "Registre lo que conoce de la parcela en lenguaje sencillo",
                "Record what you know about the parcel using simple language"
              )}
            </p>

          </div>

        </div>

      </div>


      <div className="farmer-knowledge-form friendly">

        {/* ================================================= */}
        {/* KNOWLEDGE TYPE                                    */}
        {/* ================================================= */}

        <div className="knowledge-type-cards">

          <button
            className={
              knowledgeType ===
                "OBSERVATION"
                ? "knowledge-type-card active"
                : "knowledge-type-card"
            }
            onClick={() =>
              setKnowledgeType(
                "OBSERVATION"
              )
            }
            type="button"
          >

            <Gauge
              size={19}
            />

            <strong>
              {tr(
                "Observé algo",
                "I observed something"
              )}
            </strong>

            <span>
              {tr(
                "Valor o condición vista en campo",
                "A value or condition observed in the field"
              )}
            </span>

          </button>


          <button
            className={
              knowledgeType ===
                "EVENT"
                ? "knowledge-type-card active"
                : "knowledge-type-card"
            }
            onClick={() =>
              setKnowledgeType(
                "EVENT"
              )
            }
            type="button"
          >

            <CloudRain
              size={19}
            />

            <strong>
              {tr(
                "Ocurrió un evento",
                "An event occurred"
              )}
            </strong>

            <span>
              {tr(
                "Riego, lluvia, fertilización, plaga…",
                "Irrigation, rainfall, fertilization, pest…"
              )}
            </span>

          </button>


          <button
            className={
              knowledgeType ===
                "CONSTRAINT"
                ? "knowledge-type-card active"
                : "knowledge-type-card"
            }
            onClick={() =>
              setKnowledgeType(
                "CONSTRAINT"
              )
            }
            type="button"
          >

            <ShieldCheck
              size={19}
            />

            <strong>
              {tr(
                "Tengo un límite",
                "I have a constraint"
              )}
            </strong>

            <span>
              {tr(
                "Algo que el sistema debe respetar",
                "Something the system must respect"
              )}
            </span>

          </button>


          <button
            className={
              knowledgeType ===
                "PREFERENCE"
                ? "knowledge-type-card active"
                : "knowledge-type-card"
            }
            onClick={() =>
              setKnowledgeType(
                "PREFERENCE"
              )
            }
            type="button"
          >

            <SlidersHorizontal
              size={19}
            />

            <strong>
              {tr(
                "Tengo una preferencia",
                "I have a preference"
              )}
            </strong>

            <span>
              {tr(
                "Lo que desea priorizar",
                "What you want to prioritize"
              )}
            </span>

          </button>


          <button
            className={
              knowledgeType ===
                "LOCAL_KNOWLEDGE"
                ? "knowledge-type-card active"
                : "knowledge-type-card"
            }
            onClick={() =>
              setKnowledgeType(
                "LOCAL_KNOWLEDGE"
              )
            }
            type="button"
          >

            <Leaf
              size={19}
            />

            <strong>
              {tr(
                "Conocimiento local",
                "Local knowledge"
              )}
            </strong>

            <span>
              {tr(
                "Experiencia propia sobre la parcela",
                "Your own experience with the parcel"
              )}
            </span>

          </button>

        </div>


        <div className="knowledge-friendly-section">

          {/* ================================================= */}
          {/* OBSERVATION                                       */}
          {/* ================================================= */}

          {knowledgeType ===
            "OBSERVATION" && (

            <>

              <h3>
                {tr(
                  "¿Qué observó?",
                  "What did you observe?"
                )}
              </h3>


              <div className="knowledge-form-grid">

                <label>

                  {tr(
                    "Variable observada",
                    "Observed variable"
                  )}


                  <select
                    value={
                      observationVariable
                    }
                    onChange={
                      (
                        event
                      ) =>
                        setObservationVariable(
                          event
                            .target
                            .value
                        )
                    }
                  >

                    {OBSERVATION_OPTIONS
                      .map(
                        (
                          option
                        ) => (

                          <option
                            key={
                              option.value
                            }
                            value={
                              option.value
                            }
                          >

                            {tr(
                              option.labelEs,
                              option.labelEn
                            )}

                          </option>
                        )
                      )}

                  </select>

                </label>


                <label>

                  {tr(
                    "Valor observado",
                    "Observed value"
                  )}


                  <div className="friendly-value-input">

                    <input
                      type="number"
                      step="any"
                      value={
                        observationValue
                      }
                      onChange={
                        (
                          event
                        ) =>
                          setObservationValue(
                            event
                              .target
                              .value
                          )
                      }
                      placeholder={tr(
                        observationOption
                          .placeholderEs,
                        observationOption
                          .placeholderEn
                      )}
                    />


                    <span>
                      {
                        observationOption
                          .unit
                      }
                    </span>

                  </div>

                </label>

              </div>


              <label>

                {tr(
                  "Comentario opcional",
                  "Optional comment"
                )}


                <textarea
                  rows={3}
                  value={
                    note
                  }
                  onChange={
                    (
                      event
                    ) =>
                      setNote(
                        event
                          .target
                          .value
                      )
                  }
                  placeholder={tr(
                    "Ej. La zona norte se siente más seca que el resto de la parcela.",
                    "e.g. The northern area feels drier than the rest of the parcel."
                  )}
                />

              </label>

            </>
          )}


          {/* ================================================= */}
          {/* EVENT                                             */}
          {/* ================================================= */}

          {knowledgeType ===
            "EVENT" && (

            <>

              <h3>
                {tr(
                  "¿Qué ocurrió en la parcela?",
                  "What happened in the parcel?"
                )}
              </h3>


              <label>

                {tr(
                  "Tipo de evento",
                  "Event type"
                )}


                <select
                  value={
                    eventType
                  }
                  onChange={
                    (
                      event
                    ) =>
                      setEventType(
                        event
                          .target
                          .value
                      )
                  }
                >

                  {EVENT_OPTIONS
                    .map(
                      (
                        option
                      ) => (

                        <option
                          key={
                            option.value
                          }
                          value={
                            option.value
                          }
                        >

                          {tr(
                            option.labelEs,
                            option.labelEn
                          )}

                        </option>
                      )
                    )}

                </select>

              </label>


              <label>

                {tr(
                  "Descripción",
                  "Description"
                )}


                <textarea
                  rows={4}
                  value={
                    note
                  }
                  onChange={
                    (
                      event
                    ) =>
                      setNote(
                        event
                          .target
                          .value
                      )
                  }
                  placeholder={tr(
                    "Ej. Se aplicó un riego de aproximadamente 10 mm esta mañana.",
                    "e.g. Approximately 10 mm of irrigation was applied this morning."
                  )}
                />

              </label>

            </>
          )}


          {/* ================================================= */}
          {/* CONSTRAINT                                        */}
          {/* ================================================= */}

          {knowledgeType ===
            "CONSTRAINT" && (

            <>

              <h3>
                {tr(
                  "¿Qué límite debe considerar el sistema?",
                  "What constraint should the system consider?"
                )}
              </h3>


              <label>

                {tr(
                  "Tipo de límite",
                  "Constraint type"
                )}


                <select
                  value={
                    constraintPreset
                  }
                  onChange={
                    (
                      event
                    ) =>
                      setConstraintPreset(
                        event
                          .target
                          .value
                      )
                  }
                >

                  {CONSTRAINT_PRESETS
                    .map(
                      (
                        preset
                      ) => (

                        <option
                          key={
                            `${preset.variable}|${preset.operator}`
                          }
                          value={
                            `${preset.variable}|${preset.operator}`
                          }
                        >

                          {tr(
                            preset.labelEs,
                            preset.labelEn
                          )}

                        </option>
                      )
                    )}

                </select>

              </label>


              <div className="friendly-question-box">

                <Droplets
                  size={19}
                />

                <span>

                  {tr(
                    selectedConstraint
                      .questionEs,
                    selectedConstraint
                      .questionEn
                  )}

                </span>

              </div>


              <label>

                {tr(
                  "Límite",
                  "Limit"
                )}


                <div className="friendly-value-input">

                  <input
                    type="number"
                    min="0"
                    step="any"
                    value={
                      constraintValue
                    }
                    onChange={
                      (
                        event
                      ) =>
                        setConstraintValue(
                          event
                            .target
                            .value
                        )
                    }
                    placeholder={tr(
                      selectedConstraint
                        .placeholderEs,
                      selectedConstraint
                        .placeholderEn
                    )}
                  />


                  <span>
                    {
                      selectedConstraint
                        .unit
                    }
                  </span>

                </div>

              </label>


              <div className="friendly-choice">

                <span>
                  {tr(
                    "¿Debe cumplirse obligatoriamente?",
                    "Must it be strictly enforced?"
                  )}
                </span>


                <div>

                  <button
                    type="button"
                    className={
                      constraintRequired
                        ? "selected"
                        : ""
                    }
                    onClick={() =>
                      setConstraintRequired(
                        true
                      )
                    }
                  >

                    {tr(
                      "Sí, es obligatorio",
                      "Yes, mandatory"
                    )}

                  </button>


                  <button
                    type="button"
                    className={
                      !constraintRequired
                        ? "selected"
                        : ""
                    }
                    onClick={() =>
                      setConstraintRequired(
                        false
                      )
                    }
                  >

                    {tr(
                      "Preferiblemente",
                      "Preferably"
                    )}

                  </button>

                </div>

              </div>


              <label>

                {tr(
                  "Motivo opcional",
                  "Optional reason"
                )}


                <textarea
                  rows={3}
                  value={
                    note
                  }
                  onChange={
                    (
                      event
                    ) =>
                      setNote(
                        event
                          .target
                          .value
                      )
                  }
                  placeholder={tr(
                    "Ej. La disponibilidad de agua del reservorio es limitada.",
                    "e.g. Water availability in the reservoir is limited."
                  )}
                />

              </label>

            </>
          )}


          {/* ================================================= */}
          {/* PREFERENCE                                        */}
          {/* ================================================= */}

          {knowledgeType ===
            "PREFERENCE" && (

            <>

              <h3>
                {tr(
                  "¿Qué desea priorizar?",
                  "What do you want to prioritize?"
                )}
              </h3>


              <div className="preference-option-list">

                {PREFERENCE_OPTIONS
                  .map(
                    (
                      option
                    ) => (

                      <button
                        key={
                          option.code
                        }
                        type="button"
                        className={
                          preferenceCode ===
                            option.code
                            ? "preference-option selected"
                            : "preference-option"
                        }
                        onClick={() =>
                          setPreferenceCode(
                            option.code
                          )
                        }
                      >

                        <div>

                          <strong>

                            {tr(
                              option.labelEs,
                              option.labelEn
                            )}

                          </strong>


                          <span>

                            {tr(
                              option.descriptionEs,
                              option.descriptionEn
                            )}

                          </span>

                        </div>

                      </button>
                    )
                  )}

              </div>


              <label>

                {tr(
                  "¿Qué tan importante es?",
                  "How important is it?"
                )}


                <select
                  value={
                    priority
                  }
                  onChange={
                    (
                      event
                    ) =>
                      setPriority(
                        event
                          .target
                          .value
                      )
                  }
                >

                  <option value="LOW">

                    {tr(
                      "Baja",
                      "Low"
                    )}

                  </option>


                  <option value="MEDIUM">

                    {tr(
                      "Media",
                      "Medium"
                    )}

                  </option>


                  <option value="HIGH">

                    {tr(
                      "Alta",
                      "High"
                    )}

                  </option>

                </select>

              </label>


              <label>

                {tr(
                  "Comentario opcional",
                  "Optional comment"
                )}


                <textarea
                  rows={3}
                  value={
                    note
                  }
                  onChange={
                    (
                      event
                    ) =>
                      setNote(
                        event
                          .target
                          .value
                      )
                  }
                  placeholder={tr(
                    "Ej. En esta campaña quiero reducir el consumo de agua.",
                    "e.g. During this season I want to reduce water consumption."
                  )}
                />

              </label>

            </>
          )}


          {/* ================================================= */}
          {/* LOCAL KNOWLEDGE                                   */}
          {/* ================================================= */}

          {knowledgeType ===
            "LOCAL_KNOWLEDGE" && (

            <>

              <h3>
                {tr(
                  "¿Qué sabe de esta parcela por experiencia?",
                  "What do you know about this parcel from experience?"
                )}
              </h3>


              <div className="local-knowledge-examples">

                <Sprout
                  size={18}
                />


                <div>

                  <strong>
                    {tr(
                      "Ejemplos",
                      "Examples"
                    )}
                  </strong>


                  <span>

                    {tr(
                      "“La zona baja retiene humedad más tiempo.”",
                      "“The lower area retains moisture for longer.”"
                    )}

                  </span>


                  <span>

                    {tr(
                      "“El sector norte suele encharcarse después de lluvias fuertes.”",
                      "“The northern sector usually becomes waterlogged after heavy rainfall.”"
                    )}

                  </span>


                  <span>

                    {tr(
                      "“En septiembre esta parcela normalmente necesita menos riego.”",
                      "“In September this parcel normally requires less irrigation.”"
                    )}

                  </span>

                </div>

              </div>


              <label>

                {tr(
                  "Conocimiento local",
                  "Local knowledge"
                )}


                <textarea
                  rows={5}
                  value={
                    note
                  }
                  onChange={
                    (
                      event
                    ) =>
                      setNote(
                        event
                          .target
                          .value
                      )
                  }
                  placeholder={tr(
                    "Escriba aquí su experiencia sobre la parcela...",
                    "Write your experience with this parcel here..."
                  )}
                />

              </label>

            </>
          )}


          {/* ================================================= */}
          {/* CONFIDENCE                                        */}
          {/* ================================================= */}

          <div className="knowledge-confidence-row">

            <label>

              {tr(
                "¿Qué tan seguro está de este dato?",
                "How confident are you about this information?"
              )}


              <select
                value={
                  confidence
                }
                onChange={
                  (
                    event
                  ) =>
                    setConfidence(
                      event
                        .target
                        .value
                    )
                }
              >

                <option value="0.60">

                  {tr(
                    "Poco seguro",
                    "Low confidence"
                  )}

                </option>


                <option value="0.80">

                  {tr(
                    "Bastante seguro",
                    "Fairly confident"
                  )}

                </option>


                <option value="0.95">

                  {tr(
                    "Muy seguro",
                    "Very confident"
                  )}

                </option>

              </select>

            </label>

          </div>


          {/* ================================================= */}
          {/* GOVERNANCE NOTE                                   */}
          {/* ================================================= */}

          <div className="knowledge-governance-note">

            <CircleAlert
              size={17}
            />

            <span>

              {tr(
                "Su aporte se guarda separado de sensores y satélite. El sistema conserva su procedencia y lo utiliza como contexto, preferencia o restricción según corresponda.",
                "Your contribution is stored separately from sensor and satellite data. The system preserves its provenance and uses it as context, a preference or a constraint as appropriate."
              )}

            </span>

          </div>


          {/* ================================================= */}
          {/* ERROR                                             */}
          {/* ================================================= */}

          {error && (

            <div className="hitl-message error-message">

              <CircleAlert
                size={16}
              />

              {error}

            </div>
          )}


          {/* ================================================= */}
          {/* SUCCESS                                           */}
          {/* ================================================= */}

          {success && (

            <div className="hitl-message success-message">

              <CheckCircle2
                size={16}
              />

              {success}

            </div>
          )}


          {/* ================================================= */}
          {/* SUBMIT                                            */}
          {/* ================================================= */}

          <div className="knowledge-submit-row">

            <button
              className="button-primary"
              onClick={() =>
                void submit()
              }
              disabled={
                submitting
              }
            >

              <Save
                size={16}
              />

              {submitting
                ? tr(
                    "Guardando...",
                    "Saving..."
                  )
                : tr(
                    "Registrar conocimiento",
                    "Register knowledge"
                  )}

            </button>

          </div>

        </div>

      </div>

    </section>
  );
}