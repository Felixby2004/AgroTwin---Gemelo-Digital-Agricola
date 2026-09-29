import {
  useMemo,
  useState,
} from "react";

import {
  ArrowDown,
  ArrowUp,
  BrainCircuit,
  ChevronDown,
  ChevronUp,
  CircleMinus,
  Droplets,
  FlaskConical,
  Info,
  Sparkles,
} from "lucide-react";

import type {
  SHAPFeatureContribution,
  SoilMoistureForecast,
  SoilMoistureHistory,
} from "../../api/ml";

import {
  SoilMoistureHistoryChart,
} from "./SoilMoistureHistoryChart";


interface Props {
  forecast: SoilMoistureForecast;

  history?:
    | SoilMoistureHistory
    | null;
}


/* ===================================================== */
/* FEATURE LABELS                                        */
/* ===================================================== */

const FEATURE_LABELS:
Record<string, string> = {

  soil_moisture:
    "Humedad actual",

  soil_moisture_lag_1h:
    "Humedad hace 1 h",

  soil_moisture_lag_3h:
    "Humedad hace 3 h",

  soil_moisture_lag_6h:
    "Humedad hace 6 h",

  soil_moisture_lag_12h:
    "Humedad hace 12 h",

  soil_moisture_lag_24h:
    "Humedad hace 24 h",

  soil_moisture_change_1h:
    "Cambio de humedad 1 h",

  soil_moisture_change_6h:
    "Cambio de humedad 6 h",

  soil_moisture_change_12h:
    "Cambio de humedad 12 h",

  soil_moisture_change_previous_24h:
    "Cambio previo 24 h",

  air_temperature:
    "Temperatura del aire",

  rainfall:
    "Lluvia actual",

  solar_radiation:
    "Radiación solar",

  relative_humidity:
    "Humedad relativa",

  soil_temperature:
    "Temperatura del suelo",

  rainfall_6h:
    "Lluvia últimas 6 h",

  rainfall_24h:
    "Lluvia últimas 24 h",

  rainfall_48h:
    "Lluvia últimas 48 h",

  temperature_6h_mean:
    "Temperatura media 6 h",

  solar_6h_mean:
    "Radiación media 6 h",

  humidity_6h_mean:
    "Humedad relativa media 6 h",

  hour_sin:
    "Componente horaria seno",

  hour_cos:
    "Componente horaria coseno",

  doy_sin:
    "Estacionalidad anual seno",

  doy_cos:
    "Estacionalidad anual coseno",
};


/* ===================================================== */
/* HELPERS                                               */
/* ===================================================== */

function getFeatureLabel(
  feature: string
) {

  return (
    FEATURE_LABELS[
      feature
    ] ||
    feature
  );
}


function formatMoisture(
  value: number
) {

  return value.toFixed(
    3
  );
}


function formatContribution(
  value: number
) {

  const sign =
    value > 0
      ? "+"
      : "";

  return (
    `${sign}${value.toFixed(5)}`
  );
}


function formatTimestamp(
  timestamp: string
) {

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
    "es-PE",
    {
      dateStyle:
        "medium",

      timeStyle:
        "short",
    }
  );
}


function getTrendData(
  trend: string
) {

  switch (
    trend
      .toUpperCase()
  ) {

    case "DECREASING":

      return {
        label:
          "Descenso",

        className:
          "decreasing",

        icon:
          <ArrowDown
            size={17}
          />,
      };


    case "INCREASING":

      return {
        label:
          "Aumento",

        className:
          "increasing",

        icon:
          <ArrowUp
            size={17}
          />,
      };


    default:

      return {
        label:
          "Estable",

        className:
          "stable",

        icon:
          <CircleMinus
            size={17}
          />,
      };
  }
}


/* ===================================================== */
/* SHAP ROW                                              */
/* ===================================================== */

function SHAPRow({
  item,
}: {
  item:
    SHAPFeatureContribution;
}) {

  const positive =
    item
      .contribution_to_delta
      > 0;


  const magnitude =
    Math.min(
      Math.abs(
        item
          .contribution_to_delta
      ) * 3000,
      100
    );


  return (

    <div className="ml-shap-row">

      <div className="ml-shap-name">

        <span>

          {getFeatureLabel(
            item.feature
          )}

        </span>


        <small>

          {positive
            ? "Favorece mayor humedad"
            : "Favorece menor humedad"}

        </small>

      </div>


      <div className="ml-shap-visual">

        <div className="ml-shap-track">

          <span
            className={
              positive
                ? "positive"
                : "negative"
            }
            style={{
              width:
                `${magnitude}%`,
            }}
          />

        </div>

      </div>


      <strong
        className={
          positive
            ? "positive"
            : "negative"
        }
      >

        {formatContribution(
          item
            .contribution_to_delta
        )}

      </strong>

    </div>

  );
}


/* ===================================================== */
/* COMPONENT                                             */
/* ===================================================== */

export function SoilMoistureForecastCard({
  forecast,
  history = null,
}: Props) {

  const [
    expanded,
    setExpanded,
  ] = useState(
    false
  );


  const trendData =
    getTrendData(
      forecast.trend
    );


  const features =
    forecast
      .explanation
      ?.features ||
    [];


  const visibleFeatures =
    useMemo(
      () => {

        if (expanded) {
          return features;
        }

        return features.slice(
          0,
          5
        );

      },
      [
        expanded,
        features,
      ]
    );


  const range =
    forecast
      .uncertainty
      .p90
    -
    forecast
      .uncertainty
      .p10;


  const predictionPosition =
    range > 0
      ? (
          (
            forecast
              .predicted_soil_moisture_24h
            -
            forecast
              .uncertainty
              .p10
          )
          /
          range
          *
          100
        )
      : 50;


  return (

    <section className="panel ml-forecast-panel">

      {/* ============================================= */}
      {/* HEADER                                        */}
      {/* ============================================= */}

      <div className="panel-header">

        <div className="panel-header-title">

          <div className="panel-icon purple-icon">

            <BrainCircuit
              size={20}
            />

          </div>


          <div>

            <h2>
              Módulo predictivo complementario · 24 h
            </h2>

            <p>
              Random Forest residual ·
              separado del motor de inferencia
            </p>

          </div>

        </div>


        <span className="ml-experimental-badge">

          <FlaskConical
            size={13}
          />

          Sin autoridad decisional

        </span>

      </div>


      {/* ============================================= */}
      {/* METRICS                                       */}
      {/* ============================================= */}

      <div className="ml-forecast-content">

        <div className="ml-forecast-metrics">

          <div className="ml-forecast-stat">

            <div className="ml-stat-icon current">

              <Droplets
                size={19}
              />

            </div>


            <span>
              Humedad actual
            </span>


            <strong>

              {formatMoisture(
                forecast
                  .current_soil_moisture
              )}

              <small>
                m³/m³
              </small>

            </strong>

          </div>


          <div className="ml-forecast-arrow">

            <ArrowDown
              size={18}
            />

            <span>
              +24 h
            </span>

          </div>


          <div className="ml-forecast-stat">

            <div className="ml-stat-icon forecast">

              <Sparkles
                size={19}
              />

            </div>


            <span>
              Predicción +24 h
            </span>


            <strong>

              {formatMoisture(
                forecast
                  .predicted_soil_moisture_24h
              )}

              <small>
                m³/m³
              </small>

            </strong>

          </div>


          <div className="ml-forecast-stat">

            <div
              className={
                `ml-stat-icon ${
                  trendData
                    .className
                }`
              }
            >

              {trendData.icon}

            </div>


            <span>
              Cambio previsto
            </span>


            <strong
              className={
                `ml-change ${
                  trendData
                    .className
                }`
              }
            >

              {forecast
                .delta_percent !==
              null
                ? `${forecast.delta_percent > 0
                    ? "+"
                    : ""
                  }${forecast.delta_percent.toFixed(2)}%`
                : "—"}

            </strong>


            <small className="ml-trend-label">

              {trendData.label}

            </small>

          </div>

        </div>


        {history && (

          <SoilMoistureHistoryChart
            history={
              history
            }
            forecast={
              forecast
            }
          />

        )}


        {/* =========================================== */}
        {/* UNCERTAINTY                                 */}
        {/* =========================================== */}

        <div className="ml-uncertainty-card">

          <div className="ml-uncertainty-header">

            <div>

              <strong>
                Rango del ensemble
              </strong>

              <span>
                Dispersión entre árboles
                del Random Forest
              </span>

            </div>


            <span className="ml-feature-count">

              {
                forecast
                  .feature_availability
                  .available
              }

              /

              {
                forecast
                  .feature_availability
                  .total
              }

              {" "}
              variables

            </span>

          </div>


          <div className="ml-range-values">

            <span>

              P10{" "}

              <strong>
                {formatMoisture(
                  forecast
                    .uncertainty
                    .p10
                )}
              </strong>

            </span>


            <span>

              Predicción{" "}

              <strong>
                {formatMoisture(
                  forecast
                    .predicted_soil_moisture_24h
                )}
              </strong>

            </span>


            <span>

              P90{" "}

              <strong>
                {formatMoisture(
                  forecast
                    .uncertainty
                    .p90
                )}
              </strong>

            </span>

          </div>


          <div className="ml-range-track">

            <span
              className="ml-range-marker"
              style={{
                left:
                  `${Math.min(
                    100,
                    Math.max(
                      0,
                      predictionPosition
                    )
                  )}%`,
              }}
            />

          </div>


          <div className="ml-range-footer">

            <span>

              σ ensemble:{" "}

              {
                forecast
                  .uncertainty
                  .ensemble_std
                  .toFixed(4)
              }

            </span>


            <span>

              Referencia:{" "}

              {formatTimestamp(
                forecast
                  .reference_timestamp
              )}

            </span>

          </div>

        </div>


        {/* =========================================== */}
        {/* SHAP                                        */}
        {/* =========================================== */}

        <div className="ml-explanation">

          <div className="ml-explanation-header">

            <div>

              <strong>
                ¿Por qué predice este cambio?
              </strong>

              <span>
                Contribuciones locales
                calculadas con SHAP
              </span>

            </div>


            <span>
              SHAP TreeExplainer
            </span>

          </div>


          <div className="ml-shap-list">

            {visibleFeatures.map(
              (
                item
              ) => (

                <SHAPRow
                  key={
                    item.feature
                  }
                  item={
                    item
                  }
                />

              )
            )}

          </div>


          {features.length > 5 && (

            <button
              type="button"
              className="ml-expand-button"
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

                  Mostrar solo las
                  principales
                </>

              ) : (

                <>
                  <ChevronDown
                    size={15}
                  />

                  Ver explicación completa
                </>

              )}

            </button>

          )}

        </div>


        {/* =========================================== */}
        {/* GOVERNANCE WARNING                          */}
        {/* =========================================== */}

        <div className="ml-governance-note">

          <Info
            size={18}
          />


          <div>

            <strong>
              Módulo predictivo complementario
            </strong>


            <p>
              El Random Forest no forma parte del
              motor de inferencia y decisión. No modifica
              el TwinState, no participa en el ranking de
              escenarios, no altera la recomendación de
              riego y no ejecuta acciones. Su función es
              exclusivamente predictiva y complementaria.
            </p>

          </div>

        </div>

      </div>

    </section>

  );
}