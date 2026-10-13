import {
  useMemo,
} from "react";

import type {
  SoilMoistureForecast,
  SoilMoistureHistory,
} from "../../api/ml";


interface Props {
  history:
    | SoilMoistureHistory
    | null;

  forecast?:
    | SoilMoistureForecast
    | null;

  compact?: boolean;
}


interface ChartPoint {
  timestamp: number;

  value: number;
}


function formatTime(
  timestamp: number
): string {

  return new Date(
    timestamp
  ).toLocaleString(
    "es-PE",
    {
      day: "2-digit",
      month: "2-digit",
      hour: "2-digit",
      minute: "2-digit",
    }
  );
}


function formatValue(
  value: number
): string {

  return value.toFixed(
    3
  );
}


export function SoilMoistureHistoryChart({
  history,
  forecast = null,
  compact = false,
}: Props) {

  const observed =
    useMemo(
      () => {

        return (
          history
            ?.points
            .map(
              (point) => ({
                timestamp:
                  new Date(
                    point.timestamp
                  ).getTime(),

                value:
                  point.soil_moisture,
              })
            )
            .filter(
              (point) =>
                Number.isFinite(
                  point.timestamp
                )
                &&
                Number.isFinite(
                  point.value
                )
            )
          ?? []
        );
      },
      [
        history,
      ]
    );


  const chart =
    useMemo(
      () => {

        if (
          observed.length === 0
          &&
          !forecast
        ) {
          return null;
        }


        const forecastReference =
          forecast
            ? new Date(
                forecast
                  .reference_timestamp
              ).getTime()
            : null;


        const futureTimestamp =
          forecastReference !== null
          &&
          Number.isFinite(
            forecastReference
          )
            ? forecastReference
              +
              forecast
                .prediction_horizon_hours
              *
              60
              *
              60
              *
              1000
            : null;


        const timestamps =
          observed.map(
            (point) =>
              point.timestamp
          );


        if (
          forecastReference !== null
          &&
          Number.isFinite(
            forecastReference
          )
        ) {
          timestamps.push(
            forecastReference
          );
        }


        if (
          futureTimestamp !== null
        ) {
          timestamps.push(
            futureTimestamp
          );
        }


        const values =
          observed.map(
            (point) =>
              point.value
          );


        if (forecast) {

          values.push(
            forecast
              .current_soil_moisture,

            forecast
              .predicted_soil_moisture_24h,

            forecast
              .uncertainty
              .p10,

            forecast
              .uncertainty
              .p90
          );
        }


        if (
          timestamps.length === 0
          ||
          values.length === 0
        ) {
          return null;
        }


        const minX =
          Math.min(
            ...timestamps
          );

        const maxX =
          Math.max(
            ...timestamps
          );


        const rawMinY =
          Math.min(
            ...values
          );

        const rawMaxY =
          Math.max(
            ...values
          );


        const spanY =
          Math.max(
            0.025,
            rawMaxY
            -
            rawMinY
          );


        const minY =
          Math.max(
            0,
            rawMinY
            -
            spanY
            *
            0.18
          );


        const maxY =
          Math.min(
            1,
            rawMaxY
            +
            spanY
            *
            0.18
          );


        const width =
          820;

        const height =
          compact
            ? 190
            : 235;


        const padding = {
          left: 48,
          right: 24,
          top: 20,
          bottom: 34,
        };


        const innerWidth =
          width
          -
          padding.left
          -
          padding.right;


        const innerHeight =
          height
          -
          padding.top
          -
          padding.bottom;


        const x =
          (
            timestamp: number
          ) => {

            if (
              maxX === minX
            ) {
              return (
                padding.left
                +
                innerWidth
                /
                2
              );
            }


            return (
              padding.left
              +
              (
                timestamp
                -
                minX
              )
              /
              (
                maxX
                -
                minX
              )
              *
              innerWidth
            );
          };


        const y =
          (
            value: number
          ) => {

            if (
              maxY === minY
            ) {
              return (
                padding.top
                +
                innerHeight
                /
                2
              );
            }


            return (
              padding.top
              +
              (
                maxY
                -
                value
              )
              /
              (
                maxY
                -
                minY
              )
              *
              innerHeight
            );
          };


        const observedPolyline =
          observed
            .map(
              (point) =>
                `${x(
                  point.timestamp
                )},${y(
                  point.value
                )}`
            )
            .join(
              " "
            );


        return {
          width,
          height,
          padding,
          innerWidth,
          innerHeight,
          minX,
          maxX,
          minY,
          maxY,
          x,
          y,
          observedPolyline,
          forecastReference,
          futureTimestamp,
        };
      },
      [
        observed,
        forecast,
        compact,
      ]
    );


  if (!chart) {

    return (
      <div className="ml-history-empty">

        No hay observaciones históricas de humedad disponibles.

      </div>
    );
  }


  const yTicks =
    [
      chart.minY,
      (
        chart.minY
        +
        chart.maxY
      )
      /
      2,
      chart.maxY,
    ];


  const xTicks =
    [
      chart.minX,
      (
        chart.minX
        +
        chart.maxX
      )
      /
      2,
      chart.maxX,
    ];


  return (
    <div className="ml-history-chart">

      <div className="ml-history-chart-head">

        <div>

          <strong>
            Histórico observado
            {forecast
              ? " + pronóstico complementario"
              : ""}
          </strong>

          <span>

            {history
              ? `${history.count} observaciones · ${history.coverage_hours.toFixed(1)} h de cobertura`
              : "Sin histórico persistido"}

          </span>

        </div>


        <div className="ml-history-legend">

          <span className="observed">
            Observado
          </span>

          {forecast && (
            <>
              <span className="forecast">
                RF +24 h
              </span>

              <span className="uncertainty">
                P10–P90
              </span>
            </>
          )}

        </div>

      </div>


      <div className="ml-history-svg-wrap">

        <svg
          viewBox={
            `0 0 ${chart.width} ${chart.height}`
          }
          role="img"
          aria-label="Serie temporal de humedad del suelo observada y pronóstico complementario"
        >

          {yTicks.map(
            (
              tick,
              index
            ) => (

              <g
                key={
                  `y-${index}`
                }
              >

                <line
                  x1={
                    chart.padding.left
                  }
                  x2={
                    chart.width
                    -
                    chart.padding.right
                  }
                  y1={
                    chart.y(
                      tick
                    )
                  }
                  y2={
                    chart.y(
                      tick
                    )
                  }
                  className="ml-chart-grid-line"
                />

                <text
                  x={
                    chart.padding.left
                    -
                    8
                  }
                  y={
                    chart.y(
                      tick
                    )
                    +
                    4
                  }
                  textAnchor="end"
                  className="ml-chart-axis-label"
                >
                  {formatValue(
                    tick
                  )}
                </text>

              </g>

            )
          )}


          {xTicks.map(
            (
              tick,
              index
            ) => (

              <text
                key={
                  `x-${index}`
                }
                x={
                  chart.x(
                    tick
                  )
                }
                y={
                  chart.height
                  -
                  8
                }
                textAnchor={
                  index === 0
                    ? "start"
                    : index ===
                        xTicks.length - 1
                      ? "end"
                      : "middle"
                }
                className="ml-chart-axis-label"
              >
                {formatTime(
                  tick
                )}
              </text>

            )
          )}


          {observed.length >= 2 && (

            <polyline
              points={
                chart.observedPolyline
              }
              className="ml-chart-observed-line"
            />

          )}


          {observed.map(
            (
              point,
              index
            ) => (

              <circle
                key={
                  `point-${index}`
                }
                cx={
                  chart.x(
                    point.timestamp
                  )
                }
                cy={
                  chart.y(
                    point.value
                  )
                }
                r={
                  observed.length > 60
                    ? 1.7
                    : 2.4
                }
                className="ml-chart-observed-point"
              />

            )
          )}


          {forecast
            &&
            chart.forecastReference !==
              null
            &&
            chart.futureTimestamp !==
              null
            &&
            Number.isFinite(
              chart.forecastReference
            )
            && (

            <>

              <line
                x1={
                  chart.x(
                    chart.forecastReference
                  )
                }
                x2={
                  chart.x(
                    chart.forecastReference
                  )
                }
                y1={
                  chart.padding.top
                }
                y2={
                  chart.height
                  -
                  chart.padding.bottom
                }
                className="ml-chart-now-line"
              />


              <line
                x1={
                  chart.x(
                    chart.forecastReference
                  )
                }
                y1={
                  chart.y(
                    forecast
                      .current_soil_moisture
                  )
                }
                x2={
                  chart.x(
                    chart.futureTimestamp
                  )
                }
                y2={
                  chart.y(
                    forecast
                      .predicted_soil_moisture_24h
                  )
                }
                className="ml-chart-forecast-line"
              />


              <line
                x1={
                  chart.x(
                    chart.futureTimestamp
                  )
                }
                x2={
                  chart.x(
                    chart.futureTimestamp
                  )
                }
                y1={
                  chart.y(
                    forecast
                      .uncertainty
                      .p10
                  )
                }
                y2={
                  chart.y(
                    forecast
                      .uncertainty
                      .p90
                  )
                }
                className="ml-chart-uncertainty-line"
              />


              <line
                x1={
                  chart.x(
                    chart.futureTimestamp
                  )
                  -
                  7
                }
                x2={
                  chart.x(
                    chart.futureTimestamp
                  )
                  +
                  7
                }
                y1={
                  chart.y(
                    forecast
                      .uncertainty
                      .p10
                  )
                }
                y2={
                  chart.y(
                    forecast
                      .uncertainty
                      .p10
                  )
                }
                className="ml-chart-uncertainty-cap"
              />


              <line
                x1={
                  chart.x(
                    chart.futureTimestamp
                  )
                  -
                  7
                }
                x2={
                  chart.x(
                    chart.futureTimestamp
                  )
                  +
                  7
                }
                y1={
                  chart.y(
                    forecast
                      .uncertainty
                      .p90
                  )
                }
                y2={
                  chart.y(
                    forecast
                      .uncertainty
                      .p90
                  )
                }
                className="ml-chart-uncertainty-cap"
              />


              <circle
                cx={
                  chart.x(
                    chart.forecastReference
                  )
                }
                cy={
                  chart.y(
                    forecast
                      .current_soil_moisture
                  )
                }
                r="4"
                className="ml-chart-current-point"
              />


              <circle
                cx={
                  chart.x(
                    chart.futureTimestamp
                  )
                }
                cy={
                  chart.y(
                    forecast
                      .predicted_soil_moisture_24h
                  )
                }
                r="4.5"
                className="ml-chart-forecast-point"
              />

            </>

          )}

        </svg>

      </div>


      <div className="ml-history-chart-note">

        {forecast
          ? (
            <>
              La línea discontinua muestra únicamente el pronóstico del
              módulo Random Forest complementario. No es la trayectoria
              del motor de inferencia ni una recomendación de riego.
            </>
          )
          : (
            <>
              El histórico permanece disponible aunque no exista un
              pronóstico ML válido para esta parcela.
            </>
          )}

      </div>

    </div>
  );
}
