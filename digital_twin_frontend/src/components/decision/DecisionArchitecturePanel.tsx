import {
  BrainCircuit,
  CheckCircle2,
  GitBranch,
  ShieldCheck,
} from "lucide-react";

import {
  useLanguage,
} from "../../i18n/LanguageContext";


interface Props {
  mlAvailable: boolean;

  recommendationAvailable: boolean;
}


export function DecisionArchitecturePanel({
  mlAvailable,
  recommendationAvailable,
}: Props) {

  const {
    tr,
  } = useLanguage();


  return (
    <section className="panel decision-ml-separation">

      <div className="panel-header">

        <div className="panel-header-title">

          <div className="panel-icon green-icon">

            <GitBranch
              size={20}
            />

          </div>


          <div>

            <h2>
              {tr(
                "Arquitectura de decisión y predicción",
                "Decision and prediction architecture"
              )}
            </h2>

            <p>
              {tr(
                "Dos módulos separados con responsabilidades distintas",
                "Two separate modules with different responsibilities"
              )}
            </p>

          </div>

        </div>

      </div>


      <div className="decision-ml-columns">

        <article className="decision-engine-card">

          <div className="decision-module-head">

            <div className="decision-module-icon engine">

              <ShieldCheck
                size={21}
              />

            </div>


            <div>

              <strong>
                {tr(
                  "Motor de inferencia y decisión",
                  "Inference and decision engine"
                )}
              </strong>

              <span className="decision-authority-badge">
                {tr(
                  "Autoridad decisional",
                  "Decision authority"
                )}
              </span>

            </div>

          </div>


          <p>
            {tr(
              "Es el núcleo que construye la recomendación operativa de AgroTwin.",
              "This is the core module that builds AgroTwin's operational recommendation."
            )}
          </p>


          <div className="decision-module-flow">

            <span>
              {tr(
                "Evidencia + TwinState",
                "Evidence + TwinState"
              )}
            </span>

            <span>
              {tr(
                "Conocimiento del agricultor",
                "Farmer knowledge"
              )}
            </span>

            <span>
              {tr(
                "Restricciones y conflictos",
                "Constraints and conflicts"
              )}
            </span>

            <span>
              {tr(
                "Escenarios y ranking",
                "Scenarios and ranking"
              )}
            </span>

            <span>
              {tr(
                "Recomendación + HITL",
                "Recommendation + HITL"
              )}
            </span>

          </div>


          <div className="decision-module-status">

            <CheckCircle2
              size={15}
            />

            {recommendationAvailable
              ? tr(
                  "Recomendación operativa disponible",
                  "Operational recommendation available"
                )
              : tr(
                  "Sin recomendación operativa actual",
                  "No current operational recommendation"
                )}

          </div>

        </article>


        <div className="decision-module-separator">

          <span>
            {tr(
              "INDEPENDIENTES",
              "INDEPENDENT"
            )}
          </span>

        </div>


        <article className="decision-ml-card">

          <div className="decision-module-head">

            <div className="decision-module-icon ml">

              <BrainCircuit
                size={21}
              />

            </div>


            <div>

              <strong>
                {tr(
                  "Random Forest complementario",
                  "Complementary Random Forest"
                )}
              </strong>

              <span className="ml-no-authority-badge">
                {tr(
                  "Sin autoridad decisional",
                  "No decision authority"
                )}
              </span>

            </div>

          </div>


          <p>
            {tr(
              "Pronostica humedad del suelo a +24 h y aporta incertidumbre y explicabilidad.",
              "Forecasts soil moisture at +24 h and provides uncertainty and explainability."
            )}
          </p>


          <div className="decision-module-flow ml">

            <span>
              {tr(
                "Histórico observado",
                "Observed history"
              )}
            </span>

            <span>
              {tr(
                "Δ humedad +24 h",
                "Δ moisture +24 h"
              )}
            </span>

            <span>
              P10 / P90
            </span>

            <span>
              SHAP
            </span>

          </div>


          <div className="decision-module-guards">

            <span>
              {tr(
                "No modifica TrustedState",
                "Does not modify TrustedState"
              )}
            </span>

            <span>
              {tr(
                "No participa en el ranking de escenarios",
                "Does not participate in scenario ranking"
              )}
            </span>

            <span>
              {tr(
                "No modifica la recomendación",
                "Does not modify the recommendation"
              )}
            </span>

            <span>
              {tr(
                "No ejecuta acciones",
                "Does not execute actions"
              )}
            </span>

          </div>


          <div
            className={
              mlAvailable
                ? "decision-module-status ml available"
                : "decision-module-status ml"
            }
          >

            <BrainCircuit
              size={15}
            />

            {mlAvailable
              ? tr(
                  "Pronóstico complementario disponible",
                  "Complementary forecast available"
                )
              : tr(
                  "Pronóstico complementario no disponible",
                  "Complementary forecast unavailable"
                )}

          </div>

        </article>

      </div>

    </section>
  );
}