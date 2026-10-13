import {
  useEffect,
  useMemo,
  useState,
} from "react";

import {
  isAxiosError,
} from "axios";

import {
  useSearchParams,
} from "react-router-dom";

import {
  Activity,
  Clock3,
  Cpu,
  Droplets,
  Gauge,
  MapPin,
  Plus,
  RefreshCw,
  Search,
  ShieldCheck,
  Thermometer,
  TriangleAlert,
  Wifi,
  WifiOff,
} from "lucide-react";

import {
  createSensor,
  getSensors,
  type Sensor,
  type SensorCreateInput,
  type SensorOperationalStatus,
} from "../api/sensors";

import {
  getParcels,
  type Parcel,
} from "../api/parcels";

import {
  SensorDetails,
} from "../components/sensors/SensorDetails";

import {
  SensorForm,
} from "../components/sensors/SensorForm";

import {
  useLanguage,
} from "../i18n/LanguageContext";


type EffectiveStatus =
  SensorOperationalStatus;


const FRESHNESS_HOURS:
Record<string, number> = {
  soil_moisture: 6,
  soil_water_state: 6,
  air_temperature: 3,
  relative_humidity: 3,
  rainfall: 24,
  flow_rate: 6,
};


function getEffectiveStatus(
  sensor: Sensor
): EffectiveStatus {

  if (
    !sensor.is_active
    ||
    sensor.operational_status ===
      "INACTIVE"
  ) {
    return "INACTIVE";
  }


  if (
    sensor.operational_status ===
    "ERROR"
  ) {
    return "ERROR";
  }


  if (
    !sensor.latest_observed_at
  ) {
    return "NO_DATA";
  }


  const observedAt =
    new Date(
      sensor.latest_observed_at
    )
    .getTime();


  if (
    Number.isNaN(
      observedAt
    )
  ) {
    return sensor
      .operational_status as
      EffectiveStatus;
  }


  const variable =
    sensor.latest_variable
    ?? sensor.variables[0]
    ?? "";


  const thresholdHours =
    FRESHNESS_HOURS[
      variable
    ]
    ?? 6;


  const ageHours =
    (
      Date.now()
      - observedAt
    )
    / 3_600_000;


  if (
    ageHours >
    thresholdHours
  ) {
    return "STALE";
  }


  return "ACTIVE";
}


function statusLabel(
  status:
    EffectiveStatus
): string {

  switch (
    status
  ) {

    case "ACTIVE":
      return "Activo";

    case "STALE":
      return "Desactualizado";

    case "NO_DATA":
      return "Sin datos";

    case "ERROR":
      return "Error";

    case "INACTIVE":
      return "Inactivo";

    default:
      return "Sin evaluar";
  }
}


function statusClass(
  status:
    EffectiveStatus
): string {

  return status
    .toLowerCase()
    .replaceAll(
      "_",
      "-"
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


function sensorTypeLabel(
  value: string
): string {

  switch (
    value
  ) {

    case "SOIL_MOISTURE":
      return "Humedad del suelo";

    case "AIR_TEMPERATURE":
      return "Temperatura";

    case "RELATIVE_HUMIDITY":
      return "Humedad relativa";

    case "RAINFALL":
      return "Pluviómetro";

    case "FLOW_RATE":
      return "Caudalímetro";

    case "GENERIC_IOT":
      return "Sensor IoT";

    default:
      return value
        .replaceAll(
          "_",
          " "
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


function formatDateTime(
  value:
    | string
    | null
): string {

  if (!value) {
    return "Sin comunicación";
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
          "short",
        timeStyle:
          "short",
      }
    )
    .format(
      date
    );
}


function getVariableIcon(
  variable:
    | string
    | null
) {

  switch (
    variable
  ) {

    case "soil_moisture":
    case "soil_water_state":
      return (
        <Droplets
          size={20}
        />
      );

    case "air_temperature":
      return (
        <Thermometer
          size={20}
        />
      );

    case "flow_rate":
      return (
        <Gauge
          size={20}
        />
      );

    default:
      return (
        <Activity
          size={20}
        />
      );
  }
}


export function SensorsPage() {

  const {
    t,
    tr,
  } = useLanguage();


  const [
    searchParams,
    setSearchParams,
  ] = useSearchParams();


  const [
    sensors,
    setSensors,
  ] = useState<
    Sensor[]
  >([]);


  const [
    parcels,
    setParcels,
  ] = useState<
    Parcel[]
  >([]);


  const [
    loading,
    setLoading,
  ] = useState(
    true
  );


  const [
    refreshing,
    setRefreshing,
  ] = useState(
    false
  );


  const [
    error,
    setError,
  ] = useState("");


  const [
    search,
    setSearch,
  ] = useState("");


  const [
    parcelFilter,
    setParcelFilter,
  ] = useState("ALL");


  const [
    statusFilter,
    setStatusFilter,
  ] = useState("ALL");


  const [
    typeFilter,
    setTypeFilter,
  ] = useState("ALL");


  const [
    selectedSensor,
    setSelectedSensor,
  ] = useState<
    Sensor | null
  >(null);


  const [
    showCreateSensor,
    setShowCreateSensor,
  ] = useState(
    searchParams.get(
      "create"
    ) === "1"
  );


  const [
    creatingSensor,
    setCreatingSensor,
  ] = useState(false);


  const [
    createError,
    setCreateError,
  ] = useState("");


  const [
    createMessage,
    setCreateMessage,
  ] = useState("");


  const requestedParcelId =
    searchParams.get(
      "parcel_id"
    ) ?? "";


  const requestedCreate =
    searchParams.get(
      "create"
    ) === "1";


  const loadData =
    async (
      showPageLoader = false
    ) => {

      try {

        if (
          showPageLoader
        ) {
          setLoading(
            true
          );
        } else {
          setRefreshing(
            true
          );
        }


        setError("");


        const [
          sensorData,
          parcelData,
        ] =
          await Promise.all([
            getSensors(),
            getParcels(),
          ]);


        setSensors(
          sensorData
        );

        setParcels(
          parcelData
        );


        setSelectedSensor(
          (
            current
          ) => {

            if (!current) {
              return null;
            }

            return (
              sensorData.find(
                (
                  sensor
                ) =>
                  sensor.sensor_id ===
                  current.sensor_id
              )
              ?? null
            );
          }
        );

      } catch {

        setError(
          "No se pudieron cargar los sensores."
        );

      } finally {

        setLoading(
          false
        );

        setRefreshing(
          false
        );
      }
    };


  useEffect(
    () => {

      void loadData(
        true
      );

    },
    []
  );


  useEffect(
    () => {

      if (
        requestedCreate
      ) {
        setSelectedSensor(
          null
        );

        setCreateError("");
        setCreateMessage("");

        setShowCreateSensor(
          true
        );
      }

    },
    [
      requestedCreate,
    ]
  );


  useEffect(
    () => {

      if (
        requestedParcelId
      ) {
        setParcelFilter(
          requestedParcelId
        );
      }

    },
    [
      requestedParcelId,
    ]
  );


  const openCreateSensor =
    () => {

      setSelectedSensor(
        null
      );

      setCreateError("");
      setCreateMessage("");

      setShowCreateSensor(
        true
      );
    };


  const closeCreateSensor =
    () => {

      setShowCreateSensor(
        false
      );

      setCreateError("");

      const next =
        new URLSearchParams(
          searchParams
        );

      next.delete(
        "create"
      );

      next.delete(
        "parcel_id"
      );

      setSearchParams(
        next,
        {
          replace: true,
        }
      );
    };


  const registerSensor =
    async (
      payload: SensorCreateInput
    ) => {

      try {
        setCreatingSensor(
          true
        );

        setCreateError("");
        setCreateMessage("");

        const created =
          await createSensor(
            payload
          );

        setSensors(
          (current) => [
            created,
            ...current.filter(
              (sensor) =>
                sensor.sensor_id !==
                created.sensor_id
            ),
          ]
        );

        setParcelFilter(
          created.parcel_id
        );

        setCreateMessage(
          tr(
            `Sensor "${created.name}" registrado correctamente. Permanecerá sin datos hasta recibir su primera lectura real.`,
            `Sensor "${created.name}" registered successfully. It will remain without data until its first real reading arrives.`
          )
        );

        closeCreateSensor();

      } catch (
        requestError
      ) {

        if (
          isAxiosError(
            requestError
          )
        ) {

          const detail =
            requestError
              .response
              ?.data
              ?.detail;

          if (
            typeof detail ===
            "string"
          ) {
            setCreateError(
              detail
            );
          } else {
            setCreateError(
              tr(
                "No se pudo registrar el sensor. Verifica tus permisos y los datos ingresados.",
                "The sensor could not be registered. Check your permissions and the entered data."
              )
            );
          }

        } else {
          setCreateError(
            tr(
              "No se pudo registrar el sensor.",
              "The sensor could not be registered."
            )
          );
        }

      } finally {
        setCreatingSensor(
          false
        );
      }
    };


  const parcelMap =
    useMemo(
      () => {

        return new Map(
          parcels.map(
            (
              parcel
            ) => [
              parcel.id,
              parcel.name,
            ]
          )
        );

      },
      [
        parcels,
      ]
    );


  const sensorTypes =
    useMemo(
      () => {

        return Array.from(
          new Set(
            sensors.map(
              (
                sensor
              ) =>
                sensor.sensor_type
            )
          )
        )
        .sort();

      },
      [
        sensors,
      ]
    );


  const filteredSensors =
    useMemo(
      () => {

        const query =
          search
            .trim()
            .toLowerCase();


        return sensors.filter(
          (
            sensor
          ) => {

            const status =
              getEffectiveStatus(
                sensor
              );


            const parcelName =
              parcelMap.get(
                sensor.parcel_id
              )
              ?? "";


            const matchesSearch =
              query === ""
              ||
              sensor.name
                .toLowerCase()
                .includes(
                  query
                )
              ||
              sensor.sensor_id
                .toLowerCase()
                .includes(
                  query
                )
              ||
              parcelName
                .toLowerCase()
                .includes(
                  query
                )
              ||
              sensor.variables
                .some(
                  (
                    variable
                  ) =>
                    formatVariable(
                      variable
                    )
                      .toLowerCase()
                      .includes(
                        query
                      )
                );


            const matchesParcel =
              parcelFilter ===
                "ALL"
              ||
              sensor.parcel_id ===
                parcelFilter;


            const matchesStatus =
              statusFilter ===
                "ALL"
              ||
              status ===
                statusFilter;


            const matchesType =
              typeFilter ===
                "ALL"
              ||
              sensor.sensor_type ===
                typeFilter;


            return (
              matchesSearch
              &&
              matchesParcel
              &&
              matchesStatus
              &&
              matchesType
            );
          }
        );

      },
      [
        sensors,
        search,
        parcelFilter,
        statusFilter,
        typeFilter,
        parcelMap,
      ]
    );


  const summary =
    useMemo(
      () => {

        const statuses =
          sensors.map(
            (
              sensor
            ) =>
              getEffectiveStatus(
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


  if (
    loading
  ) {

    return (
      <div className="dashboard-loading">
        Cargando sensores...
      </div>
    );
  }


  return (

    <div className="sensors-page">

      <section className="page-header sensors-page-header">

        <div>

          <h1>
            Sensores IoT
          </h1>

          <p>
            {t("sensors.subtitle")}
          </p>

        </div>


        <div className="sensors-header-actions">

          <button
            type="button"
            className="button-primary sensors-new-button"
            onClick={
              openCreateSensor
            }
            disabled={
              parcels.length === 0
            }
            title={
              parcels.length === 0
                ? tr(
                    "Necesitas al menos una parcela disponible.",
                    "You need at least one available parcel."
                  )
                : undefined
            }
          >
            <Plus size={16} />

            {tr(
              "Nuevo sensor",
              "New sensor"
            )}
          </button>


          <button
            type="button"
            className="button-secondary sensors-refresh-button"
            onClick={() =>
              void loadData(
                false
              )
            }
            disabled={
              refreshing
            }
          >
            <RefreshCw
              size={16}
              className={
                refreshing
                  ? "sensor-spin"
                  : ""
              }
            />

            {refreshing
              ? t("sensors.refreshing")
              : t("sensors.refresh")}
          </button>

        </div>

      </section>


      {error && (

        <div className="error">
          {error}
        </div>

      )}


      {createMessage && (

        <div className="sensor-create-success">
          {createMessage}
        </div>

      )}


      <section className="sensor-summary-grid">

        <article className="sensor-summary-card">

          <div className="sensor-summary-icon neutral">
            <Cpu size={21} />
          </div>

          <div>

            <span>
              {t("sensors.registered")}
            </span>

            <strong>
              {summary.total}
            </strong>

          </div>

        </article>


        <article className="sensor-summary-card">

          <div className="sensor-summary-icon active">
            <Wifi size={21} />
          </div>

          <div>

            <span>
              {t("sensors.active")}
            </span>

            <strong>
              {summary.active}
            </strong>

          </div>

        </article>


        <article className="sensor-summary-card">

          <div className="sensor-summary-icon stale">
            <Clock3 size={21} />
          </div>

          <div>

            <span>
              {t("sensors.stale")}
            </span>

            <strong>
              {summary.stale}
            </strong>

          </div>

        </article>


        <article className="sensor-summary-card">

          <div className="sensor-summary-icon attention">
            <TriangleAlert size={21} />
          </div>

          <div>

            <span>
              {t("sensors.attention")}
            </span>

            <strong>
              {summary.attention}
            </strong>

          </div>

        </article>

      </section>


      <section className="panel sensors-toolbar">

        <div className="sensor-search">

          <Search
            size={18}
          />

          <input
            type="text"
            value={
              search
            }
            placeholder={t("sensors.searchPlaceholder")}
            onChange={
              (
                event
              ) =>
                setSearch(
                  event
                    .target
                    .value
                )
            }
          />

        </div>


        <select
          value={
            parcelFilter
          }
          onChange={
            (
              event
            ) =>
              setParcelFilter(
                event
                  .target
                  .value
              )
          }
        >

          <option value="ALL">
            {t("sensors.allParcels")}
          </option>


          {parcels.map(
            (
              parcel
            ) => (

              <option
                key={
                  parcel.id
                }
                value={
                  parcel.id
                }
              >
                {parcel.name}
              </option>

            )
          )}

        </select>


        <select
          value={
            statusFilter
          }
          onChange={
            (
              event
            ) =>
              setStatusFilter(
                event
                  .target
                  .value
              )
          }
        >

          <option value="ALL">
            {t("sensors.allStatuses")}
          </option>

          <option value="ACTIVE">
            Activos
          </option>

          <option value="STALE">
            Desactualizados
          </option>

          <option value="NO_DATA">
            {t("sensors.noData")}
          </option>

          <option value="ERROR">
            {t("sensors.error")}
          </option>

          <option value="INACTIVE">
            {t("sensors.inactive")}
          </option>

        </select>


        <select
          value={
            typeFilter
          }
          onChange={
            (
              event
            ) =>
              setTypeFilter(
                event
                  .target
                  .value
              )
          }
        >

          <option value="ALL">
            {t("sensors.allTypes")}
          </option>


          {sensorTypes.map(
            (
              sensorType
            ) => (

              <option
                key={
                  sensorType
                }
                value={
                  sensorType
                }
              >
                {sensorTypeLabel(
                  sensorType
                )}
              </option>

            )
          )}

        </select>

      </section>


      <div className="sensor-results-bar">

        <div>

          <strong>
            {t("sensors.devices")}
          </strong>

          <span>
            {filteredSensors.length}
            {" "}
            {filteredSensors.length === 1
              ? t("sensors.result")
              : t("sensors.results")}
          </span>

        </div>

      </div>


      {filteredSensors.length === 0 ? (

        <section className="panel sensor-empty-state">

          <WifiOff size={34} />

          <h2>
            {t("sensors.noFiltered")}
          </h2>

          <p>
            {t("sensors.adjustFilters")}
          </p>

        </section>

      ) : (

        <section className="sensor-grid">

          {filteredSensors.map(
            (
              sensor
            ) => {

              const status =
                getEffectiveStatus(
                  sensor
                );


              const parcelName =
                parcelMap.get(
                  sensor.parcel_id
                )
                ?? "Parcela";


              return (

                <article
                  key={
                    sensor.sensor_id
                  }
                  className={
                    selectedSensor
                      ?.sensor_id ===
                      sensor.sensor_id
                        ? "sensor-card selected"
                        : "sensor-card"
                  }
                >

                  <div className="sensor-card-top">

                    <div className="sensor-device-icon">

                      {getVariableIcon(
                        sensor.latest_variable
                        ?? sensor.variables[0]
                        ?? null
                      )}

                    </div>


                    <span
                      className={
                        `sensor-status-badge ${
                          statusClass(
                            status
                          )
                        }`
                      }
                    >
                      {statusLabel(
                        status
                      )}
                    </span>

                  </div>


                  <div className="sensor-card-title">

                    <span>
                      {sensorTypeLabel(
                        sensor.sensor_type
                      )}
                    </span>

                    <h3>
                      {sensor.name}
                    </h3>

                    <p>
                      {sensor.sensor_id}
                    </p>

                  </div>


                  <div className="sensor-reading-highlight">

                    <span>
                      {t("sensors.lastReading")}
                    </span>

                    <strong>
                      {formatValue(
                        sensor.latest_value,
                        sensor.latest_unit
                      )}
                    </strong>

                    <small>
                      {formatVariable(
                        sensor.latest_variable
                      )}
                    </small>

                  </div>


                  <div className="sensor-card-info">

                    <div>

                      <MapPin size={15} />

                      <span>
                        {t("sensors.parcel")}
                      </span>

                      <strong>
                        {parcelName}
                      </strong>

                    </div>


                    <div>

                      <ShieldCheck size={15} />

                      <span>
                        {t("sensors.quality")}
                      </span>

                      <strong>
                        {sensor.latest_quality_score !== null
                          ? `${
                              Math.round(
                                sensor.latest_quality_score
                                * 100
                              )
                            }%`
                          : "—"}
                      </strong>

                    </div>


                    <div>

                      <Clock3 size={15} />

                      <span>
                        {t("sensors.lastCommunication")}
                      </span>

                      <strong>
                        {formatDateTime(
                          sensor.latest_observed_at
                        )}
                      </strong>

                    </div>

                  </div>


                  <button
                    type="button"
                    className="sensor-detail-button"
                    onClick={() =>
                      setSelectedSensor(
                        sensor
                      )
                    }
                  >
                    {t("sensors.viewDetail")}
                  </button>

                </article>

              );
            }
          )}

        </section>

      )}


      {showCreateSensor && (

        <div
          className="sensor-modal-backdrop"
          role="presentation"
          onMouseDown={(
            event
          ) => {

            if (
              event.target ===
              event.currentTarget &&
              !creatingSensor
            ) {
              closeCreateSensor();
            }
          }}
        >

          <div
            className="sensor-create-modal-shell"
            role="dialog"
            aria-modal="true"
            aria-label={tr(
              "Registrar sensor",
              "Register sensor"
            )}
          >

            <SensorForm
              parcels={
                parcels
              }
              initialParcelId={
                requestedParcelId
              }
              submitting={
                creatingSensor
              }
              errorMessage={
                createError
              }
              onCancel={
                closeCreateSensor
              }
              onSubmit={
                registerSensor
              }
            />

          </div>

        </div>
      )}


      {selectedSensor && (

        <div
          className="sensor-modal-backdrop"
          role="presentation"
          onMouseDown={(
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
          }}
        >

          <div
            className="sensor-modal-shell"
            role="dialog"
            aria-modal="true"
            aria-label="Detalle del dispositivo"
          >

            <SensorDetails
              sensor={
                selectedSensor
              }
              parcelName={
                parcelMap.get(
                  selectedSensor.parcel_id
                )
                ?? "Parcela"
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

    </div>
  );
}
