import {
  useEffect,
  useMemo,
  useState,
} from "react";

import {
  Clock3,
  Database,
  MapPin,
  ShieldCheck,
  X,
} from "lucide-react";

import {
  getSensorReadings,
  type Sensor,
  type SensorReadingHistoryItem,
} from "../../api/sensors";

import {
  useLanguage,
} from "../../i18n/LanguageContext";


interface SensorDetailsProps {
  sensor: Sensor;
  parcelName: string;
  onClose: () => void;
}


function formatDateTime(
  value:
    | string
    | null
    | undefined
): string {

  if (!value) {
    return "Sin registro";
  }

  const date =
    new Date(
      value
    );

  if (
    Number.isNaN(
      date.getTime()
    )
  ) {
    return "Fecha no disponible";
  }

  return new Intl
    .DateTimeFormat(
      "es-PE",
      {
        dateStyle:
          "medium",
        timeStyle:
          "short",
      }
    )
    .format(
      date
    );
}


function formatVariable(
  variable:
    | string
    | null
    | undefined
): string {

  switch (
    variable
  ) {

    case "soil_moisture":
    case "soil_water_state":
      return "Humedad del suelo";

    case "air_temperature":
      return "Temperatura del aire";

    case "relative_humidity":
      return "Humedad relativa";

    case "rainfall":
      return "Lluvia";

    case "flow_rate":
      return "Caudal";

    default:
      return (
        variable
          ?.replaceAll(
            "_",
            " "
          )
        || "Variable"
      );
  }
}


function formatValue(
  value: unknown,
  unit:
    | string
    | null
): string {

  if (
    value === null
    ||
    value === undefined
  ) {
    return "—";
  }

  if (
    typeof value ===
    "number"
  ) {

    const digits =
      Math.abs(
        value
      ) < 1
        ? 3
        : 2;

    return `${
      value.toFixed(
        digits
      )
    }${
      unit
        ? ` ${unit}`
        : ""
    }`;
  }

  if (
    typeof value ===
    "string"
  ) {
    return `${
      value
    }${
      unit
        ? ` ${unit}`
        : ""
    }`;
  }

  return JSON.stringify(
    value
  );
}


function qualityLabel(
  value:
    | number
    | null
): string {

  if (
    value === null
    ||
    value === undefined
  ) {
    return "Sin evaluar";
  }

  if (value >= 0.9) {
    return "Muy alta";
  }

  if (value >= 0.75) {
    return "Alta";
  }

  if (value >= 0.5) {
    return "Media";
  }

  return "Baja";
}


export function SensorDetails({
  sensor,
  parcelName,
  onClose,
}: SensorDetailsProps) {

  const {
    t,
  } = useLanguage();


  const [
    readings,
    setReadings,
  ] = useState<
    SensorReadingHistoryItem[]
  >([]);


  const [
    loading,
    setLoading,
  ] = useState(
    true
  );


  const [
    error,
    setError,
  ] = useState("");


  useEffect(
    () => {

      const load =
        async () => {

          try {

            setLoading(
              true
            );

            setError("");


            const data =
              await getSensorReadings(
                sensor.sensor_id,
                30
              );


            setReadings(
              data
            );

          } catch {

            setError(
              "No se pudo cargar el historial del sensor."
            );

          } finally {

            setLoading(
              false
            );
          }
        };


      void load();

    },
    [
      sensor.sensor_id,
    ]
  );


  const coordinates =
    useMemo(
      () => {

        if (
          sensor.latitude === null
          ||
          sensor.longitude === null
        ) {
          return null;
        }

        return `${sensor.latitude.toFixed(
          6
        )}, ${sensor.longitude.toFixed(
          6
        )}`;
      },
      [
        sensor.latitude,
        sensor.longitude,
      ]
    );


  return (

    <section className="sensor-details">

      <div className="sensor-details-header">

        <div>

          <span className="sensor-details-kicker">
            {t("sensorDetail.kicker")}
          </span>

          <h2>
            {sensor.name}
          </h2>

          <p>
            {parcelName}
            {" · "}
            {sensor.sensor_id}
          </p>

        </div>


        <button
          type="button"
          className="sensor-close-button"
          onClick={
            onClose
          }
          aria-label="Cerrar detalle del sensor"
          title="Cerrar"
        >
          <X size={18} />
        </button>

      </div>


      <div className="sensor-details-meta">

        <div>

          <Database size={17} />

          <span>
            {t("sensorDetail.type")}
          </span>

          <strong>
            {sensor.sensor_type}
          </strong>

        </div>


        <div>

          <ShieldCheck size={17} />

          <span>
            {t("sensorDetail.latestQuality")}
          </span>

          <strong>
            {sensor.latest_quality_score !== null
              ? `${
                  Math.round(
                    sensor.latest_quality_score
                    * 100
                  )
                }% · ${
                  qualityLabel(
                    sensor.latest_quality_score
                  )
                }`
              : "Sin evaluar"}
          </strong>

        </div>


        <div>

          <Clock3 size={17} />

          <span>
            {t("sensors.lastCommunication")}
          </span>

          <strong>
            {formatDateTime(
              sensor.latest_observed_at
            )}
          </strong>

        </div>


        <div>

          <MapPin size={17} />

          <span>
            {t("sensorDetail.location")}
          </span>

          <strong>
            {coordinates
              ?? t("sensorDetail.notRegistered")}
          </strong>

        </div>

      </div>


      <div className="sensor-variable-block">

        <span>
          {t("sensorDetail.variables")}
        </span>

        <div className="sensor-variable-tags">

          {sensor.variables.map(
            (
              variable
            ) => (

              <span
                key={
                  variable
                }
              >
                {formatVariable(
                  variable
                )}
              </span>

            )
          )}

        </div>

      </div>


      <div className="sensor-history-header">

        <div>

          <h3>
            {t("sensorDetail.history")}
          </h3>

          <p>
            {t("sensorDetail.historyHelp")}
          </p>

        </div>

      </div>


      {loading ? (

        <div className="sensor-history-empty">
          {t("sensorDetail.loadingHistory")}
        </div>

      ) : error ? (

        <div className="error">
          {error}
        </div>

      ) : readings.length === 0 ? (

        <div className="sensor-history-empty">
          {t("sensorDetail.noHistory")}
        </div>

      ) : (

        <div className="sensor-history-table-wrap">

          <table className="sensor-history-table">

            <thead>

              <tr>

                <th>
                  {t("sensorDetail.date")}
                </th>

                <th>
                  {t("sensorDetail.variable")}
                </th>

                <th>
                  {t("sensorDetail.reading")}
                </th>

                <th>
                  {t("sensors.quality")}
                </th>

                <th>
                  {t("sensorDetail.status")}
                </th>

              </tr>

            </thead>


            <tbody>

              {readings.map(
                (
                  reading
                ) => (

                  <tr
                    key={
                      reading.evidence_id
                    }
                  >

                    <td>
                      {formatDateTime(
                        reading.observed_at
                      )}
                    </td>

                    <td>
                      {formatVariable(
                        reading.variable
                      )}
                    </td>

                    <td>
                      <strong>
                        {formatValue(
                          reading.value,
                          reading.unit
                        )}
                      </strong>
                    </td>

                    <td>
                      {reading.quality_score !== null
                        ? `${
                            Math.round(
                              reading.quality_score
                              * 100
                            )
                          }%`
                        : "—"}
                    </td>

                    <td>

                      <span
                        className={
                          reading.status === "ACTIVE"
                            ? "reading-status active"
                            : "reading-status stale"
                        }
                      >
                        {reading.status === "ACTIVE"
                          ? t("sensorDetail.current")
                          : reading.status === "STALE"
                            ? t("sensorDetail.outdated")
                            : reading.status}
                      </span>

                    </td>

                  </tr>

                )
              )}

            </tbody>

          </table>

        </div>

      )}

    </section>
  );
}
