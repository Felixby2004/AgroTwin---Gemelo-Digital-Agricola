import {
  Cpu,
  Droplets,
  Leaf,
  Satellite,
  ShieldCheck,
  Wifi,
} from "lucide-react";

import type {
  ParcelState,
} from "../../api/twin";

import type {
  Sensor,
} from "../../api/sensors";

import {
  getEffectiveSensorStatus,
} from "../../utils/sensorPresentation";


interface TwinLegendProps {
  state: ParcelState | null;

  sensors?: Sensor[];
}


function getValue(
  state: ParcelState | null,
  variable: string
) {

  const item =
    state
      ?.trusted_state
      ?.find(
        (entry) =>
          entry.variable ===
          variable
      );


  if (!item) {
    return "—";
  }


  if (
    typeof item.value ===
    "number"
  ) {

    return item.value.toFixed(
      3
    );

  }


  if (
    item.value &&
    typeof item.value ===
    "object"
  ) {

    const numeric =
      Object.values(
        item.value
      ).find(
        (value) =>
          typeof value ===
          "number"
      );


    if (
      typeof numeric ===
      "number"
    ) {

      return numeric.toFixed(
        3
      );

    }

  }


  return "—";
}


export function TwinLegend({
  state,
  sensors = [],
}: TwinLegendProps) {

  const activeSensors =
    sensors.filter(
      (sensor) =>
        getEffectiveSensorStatus(
          sensor
        ) === "ACTIVE"
    ).length;


  return (
    <div className="twin-legend">

      <div>

        <Droplets size={16} />

        <span>
          Humedad
        </span>

        <strong>
          {getValue(
            state,
            "soil_water_state"
          )}
        </strong>

      </div>


      <div>

        <Satellite size={16} />

        <span>
          NDVI
        </span>

        <strong>
          {getValue(
            state,
            "ndvi"
          )}
        </strong>

      </div>


      <div>

        <Leaf size={16} />

        <span>
          Riego
        </span>

        <strong>
          {state
            ?.recommendation
            ?.irrigation_mm ??
            "—"} mm
        </strong>

      </div>


      <div>

        <ShieldCheck size={16} />

        <span>
          Riesgo
        </span>

        <strong>
          {state
            ?.risk
            ?.level ||
            "—"}
        </strong>

      </div>


      <div>

        {activeSensors > 0 ? (
          <Wifi size={16} />
        ) : (
          <Cpu size={16} />
        )}

        <span>
          Sensores
        </span>

        <strong>
          {activeSensors}/{sensors.length}
        </strong>

      </div>

    </div>
  );
}
