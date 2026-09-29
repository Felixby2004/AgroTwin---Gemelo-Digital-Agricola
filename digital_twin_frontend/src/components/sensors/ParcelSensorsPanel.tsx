import {
  Activity,
  Clock3,
  Cpu,
  ExternalLink,
  Gauge,
  MapPin,
  ShieldCheck,
  Thermometer,
  TriangleAlert,
  Wifi,
  WifiOff,
  Droplets,
} from "lucide-react";

import {
  Link,
} from "react-router-dom";

import {
  useMemo,
  useState,
} from "react";

import type {
  Sensor,
} from "../../api/sensors";

import {
  formatSensorValue,
  getEffectiveSensorStatus,
  sensorStatusClass,
} from "../../utils/sensorPresentation";

import {
  useLanguage,
} from "../../i18n/LanguageContext";

import {
  SensorDetails,
} from "./SensorDetails";


interface ParcelSensorsPanelProps {
  sensors: Sensor[];
  parcelName: string;
  unavailable?: boolean;
}


type Translate = (
  es: string,
  en: string
) => string;


/* ===================================================== */
/* ICONS                                                 */
/* ===================================================== */

function getVariableIcon(
  variable:
    | string
    | null
    | undefined
) {

  switch (
    variable
  ) {

    case "soil_moisture":
    case "soil_water_state":

      return (
        <Droplets
          size={18}
        />
      );


    case "air_temperature":
    case "soil_temperature":

      return (
        <Thermometer
          size={18}
        />
      );


    case "flow_rate":

      return (
        <Gauge
          size={18}
        />
      );


    default:

      return (
        <Activity
          size={18}
        />
      );
  }
}


/* ===================================================== */
/* STATUS                                                */
/* ===================================================== */

function formatSensorStatus(
  status:
    ReturnType<
      typeof getEffectiveSensorStatus
    >,
  tr: Translate
): string {

  switch (
    status
  ) {

    case "ACTIVE":

      return tr(
        "Activo",
        "Active"
      );


    case "STALE":

      return tr(
        "Desactualizado",
        "Outdated"
      );


    case "NO_DATA":

      return tr(
        "Sin datos",
        "No data"
      );


    case "ERROR":

      return tr(
        "Error",
        "Error"
      );


    case "INACTIVE":

      return tr(
        "Inactivo",
        "Inactive"
      );


    default:

      return tr(
        "Sin evaluar",
        "Not evaluated"
      );
  }
}


/* ===================================================== */
/* VARIABLE                                              */
/* ===================================================== */

function formatSensorVariable(
  variable:
    | string
    | null
    | undefined,
  tr: Translate
): string {

  switch (
    variable
  ) {

    case "soil_moisture":
    case "soil_water_state":

      return tr(
        "Humedad del suelo",
        "Soil moisture"
      );


    case "air_temperature":

      return tr(
        "Temperatura del aire",
        "Air temperature"
      );


    case "soil_temperature":

      return tr(
        "Temperatura del suelo",
        "Soil temperature"
      );


    case "relative_humidity":

      return tr(
        "Humedad relativa",
        "Relative humidity"
      );


    case "rainfall":

      return tr(
        "Lluvia",
        "Rainfall"
      );


    case "flow_rate":

      return tr(
        "Caudal",
        "Flow rate"
      );


    default:

      return (
        variable
          ?.replaceAll(
            "_",
            " "
          )
        ||
        tr(
          "Variable",
          "Variable"
        )
      );
  }
}


/* ===================================================== */
/* DATE                                                  */
/* ===================================================== */

function formatSensorDateTime(
  value:
    | string
    | null
    | undefined,
  language:
    | "es"
    | "en",
  tr: Translate
): string {

  if (
    !value
  ) {

    return tr(
      "Sin comunicación",
      "No communication"
    );
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

    return tr(
      "Fecha no disponible",
      "Date unavailable"
    );
  }


  return new Intl
    .DateTimeFormat(
      language ===
        "es"
        ? "es-PE"
        : "en-US",
      {
        dateStyle:
          "short",

        timeStyle:
          "short",
      }
    )
    .format(
      date
    );
}


/* ===================================================== */
/* COMPONENT                                             */
/* ===================================================== */

export function ParcelSensorsPanel({
  sensors,
  parcelName,
  unavailable = false,
}: ParcelSensorsPanelProps) {

  const {
    language,
    tr,
  } = useLanguage();


  const [
    selectedSensor,
    setSelectedSensor,
  ] = useState<
    Sensor | null
  >(
    null
  );


  const summary =
    useMemo(
      () => {

        const statuses =
          sensors.map(
            (
              sensor
            ) =>
              getEffectiveSensorStatus(
                sensor
              )
          );


        return {

          total:
            sensors.length,

          active:
            statuses.filter(
              (
                status
              ) =>
                status ===
                "ACTIVE"
            ).length,

          stale:
            statuses.filter(
              (
                status
              ) =>
                status ===
                "STALE"
            ).length,

          attention:
            statuses.filter(
              (
                status
              ) =>
                [
                  "ERROR",
                  "NO_DATA",
                  "INACTIVE",
                ].includes(
                  status
                )
            ).length,
        };
      },

      [
        sensors,
      ]
    );


  return (

    <section className="panel parcel-sensors-panel">

      {/* ================================================= */}
      {/* HEADER                                            */}
      {/* ================================================= */}

      <div className="panel-header parcel-sensors-header">

        <div className="panel-header-title">

          <div className="panel-icon">

            <Cpu
              size={20}
            />

          </div>


          <div>

            <h2>

              {tr(
                "Sensores de la parcela",
                "Parcel sensors"
              )}

            </h2>


            <p>

              {tr(
                "IoT integrado al estado del gemelo digital",
                "IoT integrated into the digital twin state"
              )}

            </p>

          </div>

        </div>


        <Link
          className="button-secondary parcel-sensors-link"
          to="/sensors"
        >

          <ExternalLink
            size={15}
          />

          {tr(
            "Ver sensores",
            "View sensors"
          )}

        </Link>

      </div>


      {/* ================================================= */}
      {/* UNAVAILABLE                                       */}
      {/* ================================================= */}

      {unavailable ? (

        <div className="parcel-sensors-unavailable">

          <TriangleAlert
            size={20}
          />


          <div>

            <strong>

              {tr(
                "Sensores temporalmente no disponibles",
                "Sensors temporarily unavailable"
              )}

            </strong>


            <span>

              {tr(
                "El resto del gemelo digital puede seguir funcionando.",
                "The rest of the digital twin can continue operating."
              )}

            </span>

          </div>

        </div>

      ) : (

        <>

          {/* ============================================= */}
          {/* SUMMARY                                       */}
          {/* ============================================= */}

          <div className="parcel-sensor-summary">

            <div>

              <Cpu
                size={17}
              />

              <span>

                {tr(
                  "Registrados",
                  "Registered"
                )}

              </span>

              <strong>
                {summary.total}
              </strong>

            </div>


            <div>

              <Wifi
                size={17}
              />

              <span>

                {tr(
                  "Activos",
                  "Active"
                )}

              </span>

              <strong>
                {summary.active}
              </strong>

            </div>


            <div>

              <Clock3
                size={17}
              />

              <span>

                {tr(
                  "Desactualizados",
                  "Outdated"
                )}

              </span>

              <strong>
                {summary.stale}
              </strong>

            </div>


            <div>

              <TriangleAlert
                size={17}
              />

              <span>

                {tr(
                  "Atención",
                  "Attention"
                )}

              </span>

              <strong>
                {summary.attention}
              </strong>

            </div>

          </div>


          {/* ============================================= */}
          {/* EMPTY                                         */}
          {/* ============================================= */}

          {sensors.length ===
            0 ? (

            <div className="parcel-sensors-empty">

              <WifiOff
                size={28}
              />


              <div>

                <strong>

                  {tr(
                    "No hay sensores registrados en esta parcela",
                    "No sensors are registered for this parcel"
                  )}

                </strong>


                <span>

                  {tr(
                    "Los dispositivos que se vinculen aparecerán aquí y en el gemelo 3D.",
                    "Connected devices will appear here and in the 3D digital twin."
                  )}

                </span>

              </div>

            </div>

          ) : (

            /* =========================================== */
            /* SENSOR CARDS                                */
            /* =========================================== */

            <div className="parcel-sensor-cards">

              {sensors.map(
                (
                  sensor
                ) => {

                  const status =
                    getEffectiveSensorStatus(
                      sensor
                    );


                  const variable =
                    sensor
                      .latest_variable
                    ??
                    sensor
                      .variables[0];


                  return (

                    <button
                      key={
                        sensor.sensor_id
                      }
                      type="button"
                      className="parcel-sensor-card"
                      onClick={() =>
                        setSelectedSensor(
                          sensor
                        )
                      }
                    >

                      <div className="parcel-sensor-card-top">

                        <div className="parcel-sensor-variable-icon">

                          {getVariableIcon(
                            variable
                          )}

                        </div>


                        <span
                          className={
                            `parcel-sensor-status ${
                              sensorStatusClass(
                                status
                              )
                            }`
                          }
                        >

                          {formatSensorStatus(
                            status,
                            tr
                          )}

                        </span>

                      </div>


                      <div className="parcel-sensor-card-name">

                        <strong>
                          {sensor.name}
                        </strong>

                        <span>
                          {sensor.sensor_id}
                        </span>

                      </div>


                      <div className="parcel-sensor-reading">

                        <span>

                          {formatSensorVariable(
                            variable,
                            tr
                          )}

                        </span>


                        <strong>

                          {formatSensorValue(
                            sensor.latest_value,
                            sensor.latest_unit
                          )}

                        </strong>

                      </div>


                      <div className="parcel-sensor-card-meta">

                        <span>

                          <ShieldCheck
                            size={13}
                          />

                          {tr(
                            "Calidad",
                            "Quality"
                          )}{" "}

                          {sensor
                            .latest_quality_score !==
                            null

                            ? `${
                                Math.round(
                                  sensor
                                    .latest_quality_score
                                  *
                                  100
                                )
                              }%`

                            : "—"}

                        </span>


                        <span>

                          <Clock3
                            size={13}
                          />

                          {formatSensorDateTime(
                            sensor
                              .latest_observed_at,
                            language,
                            tr
                          )}

                        </span>


                        {typeof sensor
                          .latitude ===
                            "number"
                          &&
                          typeof sensor
                            .longitude ===
                            "number"
                          && (

                          <span>

                            <MapPin
                              size={13}
                            />

                            {tr(
                              "Georreferenciado",
                              "Georeferenced"
                            )}

                          </span>
                        )}

                      </div>

                    </button>
                  );
                }
              )}

            </div>
          )}

        </>
      )}


      {/* ================================================= */}
      {/* SENSOR DETAILS MODAL                              */}
      {/* ================================================= */}

      {selectedSensor && (

        <div
          className="sensor-modal-backdrop"
          role="presentation"
          onMouseDown={
            (
              event
            ) => {

              if (
                event.target ===
                event.currentTarget
              ) {

                setSelectedSensor(
                  null
                );
              }
            }
          }
        >

          <div
            className="sensor-modal-shell"
            role="dialog"
            aria-modal="true"
            aria-label={tr(
              "Detalle del dispositivo",
              "Device details"
            )}
          >

            <SensorDetails
              sensor={
                selectedSensor
              }
              parcelName={
                parcelName
              }
              onClose={() =>
                setSelectedSensor(
                  null
                )
              }
            />

          </div>

        </div>
      )}

    </section>
  );
}