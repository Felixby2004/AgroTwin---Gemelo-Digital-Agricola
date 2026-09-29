import {
  Clock3,
  Pause,
  Play,
} from "lucide-react";

import {
  useEffect,
  useMemo,
  useState,
} from "react";

import type {
  SoilMoistureForecast,
} from "../../api/ml";


interface TemporalTwinControlsProps {
  currentMoisture:
    | number
    | null;

  forecast:
    | SoilMoistureForecast
    | null;

  selectedHour: number;

  onSelectedHourChange:
    (hour: number) => void;
}


const HOURS = [
  0,
  6,
  12,
  18,
  24,
];


function interpolateMoisture(
  current: number,
  future: number,
  hour: number
): number {

  const ratio =
    Math.max(
      0,
      Math.min(
        1,
        hour / 24
      )
    );


  return (
    current
    +
    (
      future
      - current
    )
    * ratio
  );
}


function formatMoisture(
  value:
    | number
    | null
    | undefined
): string {

  if (
    typeof value !==
    "number"
  ) {
    return "—";
  }


  return value.toFixed(
    3
  );
}


export function TemporalTwinControls({
  currentMoisture,
  forecast,
  selectedHour,
  onSelectedHourChange,
}: TemporalTwinControlsProps) {

  const [
    playing,
    setPlaying,
  ] = useState(
    false
  );


  const forecastAvailable =
    typeof currentMoisture ===
      "number"
    &&
    typeof forecast
      ?.predicted_soil_moisture_24h ===
      "number";


  const displayedMoisture =
    useMemo(
      () => {

        if (
          !forecastAvailable
          ||
          typeof currentMoisture !==
            "number"
          ||
          !forecast
        ) {
          return currentMoisture;
        }


        return interpolateMoisture(
          currentMoisture,
          forecast
            .predicted_soil_moisture_24h,
          selectedHour
        );
      },
      [
        currentMoisture,
        forecast,
        forecastAvailable,
        selectedHour,
      ]
    );


  useEffect(
    () => {

      if (
        !playing
        ||
        !forecastAvailable
      ) {
        return;
      }


      const timer =
        window.setInterval(
          () => {

            const currentIndex =
              HOURS.indexOf(
                selectedHour
              );


            if (
              currentIndex ===
              HOURS.length - 1
            ) {

              onSelectedHourChange(
                0
              );

              return;
            }


            const nextHour =
              HOURS[
                Math.max(
                  0,
                  currentIndex + 1
                )
              ];


            onSelectedHourChange(
              nextHour
            );
          },
          1100
        );


      return () => {
        window.clearInterval(
          timer
        );
      };
    },
    [
      playing,
      forecastAvailable,
      selectedHour,
      onSelectedHourChange,
    ]
  );


  useEffect(
    () => {

      if (
        !forecastAvailable
      ) {
        setPlaying(
          false
        );
      }

    },
    [
      forecastAvailable,
    ]
  );


  const stateLabel =
    selectedHour === 0
      ? "TwinState actual"
      : selectedHour === 24
        ? "Pronóstico complementario RF · +24 h"
        : `Interpolación visual (no predicción) · +${selectedHour} h`;


  return (
    <div className="twin-temporal-controls">

      <div className="twin-temporal-head">

        <div>

          <div className="twin-temporal-title">

            <Clock3
              size={16}
            />

            <strong>
              Vista temporal complementaria
            </strong>

          </div>

          <span>
            {stateLabel}
          </span>

        </div>


        <div className="twin-temporal-value">

          <span>
            Humedad visualizada
          </span>

          <strong>
            {formatMoisture(
              displayedMoisture
            )}
          </strong>

        </div>

      </div>


      <div className="twin-temporal-actions">

        <button
          type="button"
          className={
            playing
              ? "twin-play-button active"
              : "twin-play-button"
          }
          disabled={
            !forecastAvailable
          }
          onClick={() =>
            setPlaying(
              (value) =>
                !value
            )
          }
        >

          {playing ? (
            <Pause
              size={15}
            />
          ) : (
            <Play
              size={15}
            />
          )}

          {playing
            ? "Pausar"
            : "Reproducir"}

        </button>


        <div className="twin-time-steps">

          {HOURS.map(
            (hour) => (

              <button
                key={hour}
                type="button"
                className={
                  selectedHour ===
                    hour
                    ? "active"
                    : ""
                }
                disabled={
                  hour > 0
                  &&
                  !forecastAvailable
                }
                onClick={() =>
                  onSelectedHourChange(
                    hour
                  )
                }
              >

                {hour === 0
                  ? "Ahora"
                  : `+${hour} h`}

              </button>

            )
          )}

        </div>

      </div>


      {forecastAvailable && forecast ? (

        <div className="twin-temporal-meta">

          <span>
            Actual{" "}
            <strong>
              {formatMoisture(
                currentMoisture
              )}
            </strong>
          </span>

          <span>
            Pronóstico 24 h{" "}
            <strong>
              {formatMoisture(
                forecast
                  .predicted_soil_moisture_24h
              )}
            </strong>
          </span>

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

      ) : (

        <div className="twin-temporal-note">

          No hay un pronóstico complementario disponible. El TwinState actual y el motor de decisión continúan funcionando de forma independiente.

        </div>

      )}


      {forecastAvailable && selectedHour > 0 && selectedHour < 24 && (

        <div className="twin-temporal-note">

          +6 h, +12 h y +18 h son solo una interpolación gráfica entre el TwinState actual y el pronóstico complementario de +24 h. No son predicciones independientes y no pertenecen al motor de inferencia.

        </div>

      )}


      {forecastAvailable && selectedHour === 24 && (

        <div className="twin-temporal-note forecast">

          La vista +24 h proviene exclusivamente del Random Forest complementario. No modifica el TrustedState, no participa en escenarios o ranking y no cambia la recomendación del motor de decisión.

        </div>

      )}

    </div>
  );
}
