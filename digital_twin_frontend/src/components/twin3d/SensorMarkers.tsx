import {
  Html,
} from "@react-three/drei";

import {
  useMemo,
} from "react";

import type {
  Sensor,
} from "../../api/sensors";

import type {
  ParcelGeometryResponse,
} from "../../api/parcels";

import {
  buildParcelProjection,
  pointInParcelPolygon,
  projectGeoPointToLocal,
  type ParcelProjection,
} from "../../utils/parcelGeometry3d";

import {
  formatSensorValue,
  getEffectiveSensorStatus,
  sensorStatusColor,
  sensorStatusLabel,
} from "../../utils/sensorPresentation";


interface SensorMarkersProps {
  sensors: Sensor[];

  showLabels?: boolean;

  geometry?:
    | ParcelGeometryResponse["geometry"]
    | null;
}


interface SensorPosition {
  sensor: Sensor;

  x: number;

  z: number;
}


function hashText(
  text: string
): number {

  let hash =
    2166136261;


  for (
    let index = 0;
    index < text.length;
    index += 1
  ) {

    hash ^=
      text.charCodeAt(
        index
      );

    hash =
      Math.imul(
        hash,
        16777619
      );
  }


  return hash >>> 0;
}


function fallbackPosition(
  sensor: Sensor,
  index: number,
  projection:
    | ParcelProjection
    | null
): {
  x: number;
  z: number;
} {

  const hash =
    hashText(
      sensor.sensor_id
    );


  if (projection) {

    const {
      bounds,
      points,
    } =
      projection;


    const fractions = [
      0.25,
      0.50,
      0.75,
      0.35,
      0.65,
    ];


    for (
      let attempt = 0;
      attempt < fractions.length;
      attempt += 1
    ) {

      const xFraction =
        fractions[
          (
            hash
            + attempt
          )
          % fractions.length
        ];

      const zFraction =
        fractions[
          (
            hash
            + index
            + attempt
            + 2
          )
          % fractions.length
        ];


      const point = {
        x:
          bounds.minX
          +
          bounds.width
          * xFraction,

        z:
          bounds.minZ
          +
          bounds.depth
          * zFraction,
      };


      if (
        pointInParcelPolygon(
          point,
          points
        )
      ) {
        return point;
      }
    }


    return {
      x: 0,
      z: 0,
    };
  }


  const angle =
    (
      (hash % 360)
      * Math.PI
    )
    / 180;


  const ring =
    1.6
    +
    (
      index % 3
    )
    * 0.85;


  return {
    x:
      Math.cos(
        angle
      )
      * ring,

    z:
      Math.sin(
        angle
      )
      * ring,
  };
}


function buildPositions(
  sensors: Sensor[],
  geometry:
    | ParcelGeometryResponse["geometry"]
    | null
): SensorPosition[] {

  const projection =
    buildParcelProjection(
      geometry
    );


  return sensors.map(
    (
      sensor,
      index
    ) => {

      if (
        projection
        &&
        typeof sensor.latitude ===
          "number"
        &&
        typeof sensor.longitude ===
          "number"
      ) {

        const local =
          projectGeoPointToLocal(
            projection,
            sensor.longitude,
            sensor.latitude
          );


        return {
          sensor,
          x:
            local.x,
          z:
            local.z,
        };
      }


      return {
        sensor,
        ...fallbackPosition(
          sensor,
          index,
          projection
        ),
      };
    }
  );
}


export function SensorMarkers({
  sensors,
  showLabels = false,
  geometry = null,
}: SensorMarkersProps) {

  const positions =
    useMemo(
      () =>
        buildPositions(
          sensors,
          geometry
        ),
      [
        sensors,
        geometry,
      ]
    );


  return (
    <>

      {positions.map(
        ({
          sensor,
          x,
          z,
        }) => {

          const status =
            getEffectiveSensorStatus(
              sensor
            );


          const color =
            sensorStatusColor(
              status
            );


          return (
            <group
              key={
                sensor.sensor_id
              }
              position={[
                x,
                0.18,
                z,
              ]}
            >

              <mesh
                position={[
                  0,
                  0.42,
                  0,
                ]}
                castShadow
              >

                <cylinderGeometry
                  args={[
                    0.045,
                    0.055,
                    0.82,
                    10,
                  ]}
                />

                <meshStandardMaterial
                  color="#475569"
                  roughness={0.62}
                  metalness={0.28}
                />

              </mesh>


              <mesh
                position={[
                  0,
                  0.88,
                  0,
                ]}
                castShadow
              >

                <boxGeometry
                  args={[
                    0.28,
                    0.24,
                    0.18,
                  ]}
                />

                <meshStandardMaterial
                  color={color}
                  roughness={0.48}
                  metalness={0.12}
                />

              </mesh>


              <mesh
                position={[
                  0,
                  1.07,
                  0,
                ]}
              >

                <sphereGeometry
                  args={[
                    0.055,
                    12,
                    12,
                  ]}
                />

                <meshStandardMaterial
                  color={color}
                  emissive={color}
                  emissiveIntensity={
                    status ===
                      "ACTIVE"
                      ? 0.75
                      : 0.22
                  }
                />

              </mesh>


              {showLabels && (

                <Html
                  center
                  position={[
                    0,
                    1.42,
                    0,
                  ]}
                  distanceFactor={9}
                  style={{
                    pointerEvents:
                      "none",
                  }}
                >

                  <div className="twin-sensor-label">

                    <strong>
                      {sensor.name}
                    </strong>

                    <span>

                      {sensorStatusLabel(
                        status
                      )}

                      {" · "}

                      {formatSensorValue(
                        sensor.latest_value,
                        sensor.latest_unit
                      )}

                    </span>

                  </div>

                </Html>

              )}

            </group>
          );
        }
      )}

    </>
  );
}
