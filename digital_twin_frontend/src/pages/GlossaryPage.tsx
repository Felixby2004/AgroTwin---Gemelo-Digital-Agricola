import type {
  ReactNode,
} from "react";

import {
  BookOpenText,
  BrainCircuit,
  Database,
  Leaf,
  Satellite,
  ShieldCheck,
  Sprout,
} from "lucide-react";

import {
  useLanguage,
} from "../i18n/LanguageContext";


type BilingualText = {
  es: string;
  en: string;
};


type GlossaryItem = {
  term: BilingualText;
  description: BilingualText;
};


type GlossarySection = {
  title: BilingualText;
  description: BilingualText;
  icon: ReactNode;
  items: GlossaryItem[];
};


const SECTIONS:
GlossarySection[] = [
  {
    title: {
      es: "Gemelo digital",
      en: "Digital twin",
    },
    description: {
      es: "Conceptos básicos para interpretar el estado digital de una parcela.",
      en: "Core concepts for interpreting the digital state of a parcel.",
    },
    icon: <Leaf size={20} />,
    items: [
      {
        term: {
          es: "Gemelo digital",
          en: "Digital twin",
        },
        description: {
          es: "Representación digital dinámica de la parcela que integra datos, modelos y conocimiento del agricultor.",
          en: "Dynamic digital representation of the parcel integrating data, models and farmer knowledge.",
        },
      },
      {
        term: {
          es: "TwinState",
          en: "TwinState",
        },
        description: {
          es: "Estado consolidado que el sistema considera confiable en un momento determinado.",
          en: "Consolidated state that the system considers trustworthy at a given time.",
        },
      },
      {
        term: {
          es: "Confianza del gemelo",
          en: "Twin confidence",
        },
        description: {
          es: "Nivel de confiabilidad asignado al estado actual según calidad, consistencia y procedencia de los datos.",
          en: "Reliability level assigned to the current state based on data quality, consistency and provenance.",
        },
      },
      {
        term: {
          es: "Variable por actualizar",
          en: "Variable requiring update",
        },
        description: {
          es: "Dato cuya vigencia o calidad requiere una nueva medición o actualización.",
          en: "A data item whose freshness or quality requires a new measurement or update.",
        },
      },
    ],
  },
  {
    title: {
      es: "Recomendaciones e IA explicable",
      en: "Recommendations and explainable AI",
    },
    description: {
      es: "Términos usados para explicar por qué el sistema recomienda una acción.",
      en: "Terms used to explain why the system recommends an action.",
    },
    icon: <BrainCircuit size={20} />,
    items: [
      {
        term: {
          es: "Recomendación de riego",
          en: "Irrigation recommendation",
        },
        description: {
          es: "Cantidad de agua sugerida por el motor de decisión para la condición actual de la parcela.",
          en: "Amount of water suggested by the decision engine for the parcel's current condition.",
        },
      },
      {
        term: {
          es: "Puntaje",
          en: "Score",
        },
        description: {
          es: "Valor agregado utilizado para comparar alternativas considerando criterios agronómicos, preferencias y confianza.",
          en: "Aggregate value used to compare alternatives considering agronomic criteria, preferences and confidence.",
        },
      },
      {
        term: {
          es: "Motor multicriterio",
          en: "Multi-criteria engine",
        },
        description: {
          es: "Mecanismo que combina varios criterios para comparar escenarios y producir una recomendación.",
          en: "Mechanism that combines multiple criteria to compare scenarios and produce a recommendation.",
        },
      },
      {
        term: {
          es: "Explicabilidad",
          en: "Explainability",
        },
        description: {
          es: "Capacidad del sistema para mostrar los factores, restricciones y evidencias que influyeron en una recomendación.",
          en: "System capability to show the factors, constraints and evidence that influenced a recommendation.",
        },
      },
      {
        term: {
          es: "SHAP",
          en: "SHAP",
        },
        description: {
          es: "Método de explicabilidad que estima cuánto aportó cada variable a una predicción del modelo de aprendizaje automático.",
          en: "Explainability method that estimates how much each variable contributed to a machine-learning prediction.",
        },
      },
    ],
  },
  {
    title: {
      es: "Evidencia y confianza",
      en: "Evidence and confidence",
    },
    description: {
      es: "Cómo se interpreta la información que sustenta el estado de la parcela.",
      en: "How the information supporting the parcel state is interpreted.",
    },
    icon: <Database size={20} />,
    items: [
      {
        term: {
          es: "Evidencia operacional",
          en: "Operational evidence",
        },
        description: {
          es: "Datos disponibles y utilizables por el gemelo digital, como sensores, satélite, modelos o registros.",
          en: "Data available to and usable by the digital twin, such as sensors, satellite, models or records.",
        },
      },
      {
        term: {
          es: "Conflicto",
          en: "Conflict",
        },
        description: {
          es: "Inconsistencia detectada entre fuentes o afirmaciones que requiere ser registrada y evaluada.",
          en: "Detected inconsistency between sources or claims that must be recorded and evaluated.",
        },
      },
      {
        term: {
          es: "Riesgo",
          en: "Risk",
        },
        description: {
          es: "Nivel de precaución asociado a la recomendación según incertidumbre, calidad de datos y condiciones actuales.",
          en: "Level of caution associated with a recommendation based on uncertainty, data quality and current conditions.",
        },
      },
      {
        term: {
          es: "Procedencia",
          en: "Provenance",
        },
        description: {
          es: "Registro del origen de un dato o conocimiento, por ejemplo sensor, satélite, modelo o agricultor.",
          en: "Record of the origin of data or knowledge, for example sensor, satellite, model or farmer.",
        },
      },
    ],
  },
  {
    title: {
      es: "Satélite e índices",
      en: "Satellite and indices",
    },
    description: {
      es: "Indicadores derivados de observaciones remotas de la parcela.",
      en: "Indicators derived from remote observations of the parcel.",
    },
    icon: <Satellite size={20} />,
    items: [
      {
        term: {
          es: "NDVI",
          en: "NDVI",
        },
        description: {
          es: "Índice de vegetación que ayuda a representar vigor y actividad de la cobertura vegetal.",
          en: "Vegetation index that helps represent vigor and activity of plant cover.",
        },
      },
      {
        term: {
          es: "NDMI",
          en: "NDMI",
        },
        description: {
          es: "Índice relacionado con el contenido de humedad de la vegetación observado mediante imágenes satelitales.",
          en: "Index related to vegetation moisture content observed through satellite imagery.",
        },
      },
      {
        term: {
          es: "Copernicus",
          en: "Copernicus",
        },
        description: {
          es: "Programa europeo de observación de la Tierra utilizado como fuente de información satelital.",
          en: "European Earth observation programme used as a source of satellite information.",
        },
      },
    ],
  },
  {
    title: {
      es: "Conocimiento del agricultor",
      en: "Farmer knowledge",
    },
    description: {
      es: "Cómo participa la experiencia humana sin reemplazar silenciosamente la evidencia del gemelo.",
      en: "How human experience participates without silently replacing digital-twin evidence.",
    },
    icon: <Sprout size={20} />,
    items: [
      {
        term: {
          es: "Observación",
          en: "Observation",
        },
        description: {
          es: "Dato o condición reportada directamente por el agricultor a partir de lo que observa en campo.",
          en: "Data or condition reported directly by the farmer from field observations.",
        },
      },
      {
        term: {
          es: "Evento",
          en: "Event",
        },
        description: {
          es: "Hecho ocurrido en la parcela, como riego, lluvia, fertilización, plaga o mantenimiento.",
          en: "Event occurring in the parcel, such as irrigation, rain, fertilization, pest occurrence or maintenance.",
        },
      },
      {
        term: {
          es: "Restricción obligatoria",
          en: "Mandatory constraint",
        },
        description: {
          es: "Límite que el motor de decisión no debe violar, por ejemplo un máximo de agua disponible.",
          en: "Limit that the decision engine must not violate, for example a maximum available amount of water.",
        },
      },
      {
        term: {
          es: "Restricción preferible",
          en: "Preferred constraint",
        },
        description: {
          es: "Condición deseable que puede influir en la decisión, pero no bloquea automáticamente una alternativa.",
          en: "Desired condition that may influence the decision but does not automatically block an alternative.",
        },
      },
      {
        term: {
          es: "Preferencia",
          en: "Preference",
        },
        description: {
          es: "Prioridad expresada por el agricultor, como ahorrar agua, reducir riesgo o favorecer rendimiento.",
          en: "Priority expressed by the farmer, such as saving water, reducing risk or favoring yield.",
        },
      },
      {
        term: {
          es: "Conocimiento local",
          en: "Local knowledge",
        },
        description: {
          es: "Experiencia contextual del agricultor sobre patrones o particularidades de su parcela.",
          en: "Farmer contextual experience about patterns or specific characteristics of the parcel.",
        },
      },
    ],
  },
  {
    title: {
      es: "Gobernanza y trazabilidad",
      en: "Governance and traceability",
    },
    description: {
      es: "Conceptos relacionados con control, permisos y seguimiento de decisiones.",
      en: "Concepts related to control, permissions and decision tracking.",
    },
    icon: <ShieldCheck size={20} />,
    items: [
      {
        term: {
          es: "Trazabilidad",
          en: "Traceability",
        },
        description: {
          es: "Capacidad de reconstruir qué datos, conocimientos y decisiones participaron en un resultado.",
          en: "Ability to reconstruct which data, knowledge and decisions contributed to an outcome.",
        },
      },
      {
        term: {
          es: "Decision Trace",
          en: "Decision Trace",
        },
        description: {
          es: "Registro técnico de una recomendación, sus evidencias, escenarios, respuesta humana y acción final.",
          en: "Technical record of a recommendation, its evidence, scenarios, human response and final action.",
        },
      },
      {
        term: {
          es: "Soberanía de datos",
          en: "Data sovereignty",
        },
        description: {
          es: "Principio según el cual los usuarios mantienen control sobre acceso, uso y finalidad de sus datos.",
          en: "Principle under which users retain control over access to, use of and purpose of their data.",
        },
      },
      {
        term: {
          es: "Human-in-the-loop (HITL)",
          en: "Human-in-the-loop (HITL)",
        },
        description: {
          es: "Proceso en el que una persona puede aceptar, modificar o rechazar una recomendación del sistema.",
          en: "Process in which a person can accept, modify or reject a system recommendation.",
        },
      },
    ],
  },
];


export function GlossaryPage() {

  const {
    language,
    t,
  } = useLanguage();


  return (
    <div>

      <section className="page-header">

        <div>

          <h1>
            {t("glossary.title")}
          </h1>

          <p>
            {t("glossary.subtitle")}
          </p>

        </div>

        <div className="glossary-header-icon">
          <BookOpenText size={24} />
        </div>

      </section>


      <section className="glossary-grid">

        {SECTIONS.map(
          (
            section
          ) => (

            <article
              className="panel glossary-section"
              key={
                section.title.es
              }
            >

              <div className="panel-header">

                <div className="panel-header-title">

                  <div className="panel-icon">
                    {section.icon}
                  </div>

                  <div>

                    <h2>
                      {section.title[
                        language
                      ]}
                    </h2>

                    <p>
                      {section.description[
                        language
                      ]}
                    </p>

                  </div>

                </div>

              </div>


              <div className="glossary-list">

                {section.items.map(
                  (
                    item
                  ) => (

                    <div
                      className="glossary-item"
                      key={
                        item.term.es
                      }
                    >

                      <strong>
                        {item.term[
                          language
                        ]}
                      </strong>

                      <p>
                        {item.description[
                          language
                        ]}
                      </p>

                    </div>

                  )
                )}

              </div>

            </article>

          )
        )}

      </section>

    </div>
  );
}
