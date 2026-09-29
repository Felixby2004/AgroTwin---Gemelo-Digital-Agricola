import type {
  Sensor,
  SensorOperationalStatus,
} from "../api/sensors";


export type EffectiveSensorStatus =
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


export function getEffectiveSensorStatus(
  sensor: Sensor
): EffectiveSensorStatus {

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

    switch (
      sensor.operational_status
    ) {

      case "ACTIVE":
      case "STALE":
      case "NO_DATA":
      case "ERROR":
      case "INACTIVE":
        return sensor.operational_status;

      default:
        return "NO_DATA";
    }
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


export function sensorStatusLabel(
  status: EffectiveSensorStatus
): string {

  switch (status) {

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


export function sensorStatusClass(
  status: EffectiveSensorStatus
): string {

  return status
    .toLowerCase()
    .replaceAll(
      "_",
      "-"
    );
}


export function sensorStatusColor(
  status: EffectiveSensorStatus
): string {

  switch (status) {

    case "ACTIVE":
      return "#16a34a";

    case "STALE":
      return "#d97706";

    case "ERROR":
      return "#dc2626";

    case "INACTIVE":
      return "#64748b";

    case "NO_DATA":
    default:
      return "#2563eb";
  }
}


export function formatSensorVariable(
  variable:
    | string
    | null
    | undefined
): string {

  switch (variable) {

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


export function formatSensorValue(
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
    typeof value === "number"
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
    typeof value === "string"
  ) {

    return `${
      value
    }${
      unit
        ? ` ${unit}`
        : ""
    }`;
  }


  try {

    return JSON.stringify(
      value
    );

  } catch {

    return "—";
  }
}


export function formatSensorDateTime(
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
        dateStyle: "short",
        timeStyle: "short",
      }
    )
    .format(
      date
    );
}
