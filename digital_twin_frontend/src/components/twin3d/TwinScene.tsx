import {
  Canvas,
} from "@react-three/fiber";

import {
  Environment,
  Grid,
  OrbitControls,
} from "@react-three/drei";

import {
  Suspense,
  useMemo,
  useState,
} from "react";

import {
  ParcelField,
} from "./ParcelField";

import {
  SensorMarkers,
} from "./SensorMarkers";

import type {
  ParcelState,
} from "../../api/twin";

import type {
  Sensor,
} from "../../api/sensors";

import type {
  ParcelGeometryResponse,
} from "../../api/parcels";

import {
  buildParcelProjection,
} from "../../utils/parcelGeometry3d";

import {
  estimateCropPopulation,
  estimateRenderedInstanceCount,
  getCropVisualProfile,
  resolveVisualizationAreaHa,
} from "../../utils/cropVisualProfiles";

import {
  formatLayerValue,
  layerLabel,
  type TwinAgronomicLayer,
} from "../../utils/agronomicLayers";


export type TwinSceneMode =
  | "summary"
  | "detailed";


interface TwinSceneProps {
  state: ParcelState | null;

  sensors?: Sensor[];

  mode?: TwinSceneMode;

  soilMoistureOverride?:
    | number
    | null;

  geometry?:
    | ParcelGeometryResponse["geometry"]
    | null;

  cropType?:
    | string
    | null;

  areaHa?:
    | number
    | null;
}


function getNumericStateValue(
  state: ParcelState | null,
  variable: string
): number | null {

  const item =
    state
      ?.trusted_state
      ?.find(
        (entry) =>
          entry.variable ===
          variable
      );


  if (!item) {
    return null;
  }


  if (
    typeof item.value ===
    "number"
  ) {
    return item.value;
  }


  if (
    item.value
    &&
    typeof item.value ===
      "object"
  ) {

    const numeric =
      Object.values(
        item.value
      ).find(
        (entry) =>
          typeof entry ===
          "number"
      );


    if (
      typeof numeric ===
      "number"
    ) {
      return numeric;
    }
  }


  return null;
}


export function TwinScene({
  state,
  sensors = [],
  mode = "summary",
  soilMoistureOverride = null,
  geometry = null,
  cropType = null,
  areaHa = null,
}: TwinSceneProps) {

  const detailed =
    mode === "detailed";


  const [
    visualLayer,
    setVisualLayer,
  ] = useState<
    TwinAgronomicLayer
  >("crop");


  const ndvi =
    getNumericStateValue(
      state,
      "ndvi"
    );


  const ndmi =
    getNumericStateValue(
      state,
      "ndmi"
    );


  const trustedSoilMoisture =
    getNumericStateValue(
      state,
      "soil_water_state"
    );


  const shownSoilMoisture =
    typeof soilMoistureOverride ===
      "number"
      ? soilMoistureOverride
      : trustedSoilMoisture;


  const cropStats =
    useMemo(
      () => {

        const projection =
          buildParcelProjection(
            geometry
          );

        const profile =
          getCropVisualProfile(
            cropType
          );

        const effectiveAreaHa =
          resolveVisualizationAreaHa(
            areaHa,
            projection
              ?.realAreaHa
          );

        const actualPopulation =
          estimateCropPopulation(
            effectiveAreaHa,
            profile
          );

        const renderedInstances =
          estimateRenderedInstanceCount(
            actualPopulation,
            profile
          );

        const metersPerLocalUnit =
          projection
            ? 1
              /
              Math.max(
                projection.scale,
                0.000001
              )
            : null;


        return {
          projection,
          profile,
          effectiveAreaHa,
          actualPopulation,
          renderedInstances,
          metersPerLocalUnit,
        };
      },
      [
        geometry,
        cropType,
        areaHa,
      ]
    );


  return (
    <div className="twin-3d-canvas">

      <Canvas
        camera={{
          position: detailed
            ? [10, 8.5, 12]
            : [9, 7.5, 10.5],

          fov: detailed
            ? 40
            : 44,
        }}
        shadows
      >

        <ambientLight
          intensity={1.05}
        />


        <directionalLight
          position={[
            6,
            10,
            6,
          ]}
          intensity={1.6}
          castShadow
        />


        <Suspense fallback={null}>

          <ParcelField
            state={state}
            mode={mode}
            visualLayer={
              visualLayer
            }
            soilMoistureOverride={
              soilMoistureOverride
            }
            geometry={
              geometry
            }
            cropType={
              cropType
            }
            areaHa={
              areaHa
            }
          />


          <SensorMarkers
            sensors={
              sensors
            }
            showLabels={
              detailed
            }
            geometry={
              geometry
            }
          />


          <Grid
            args={[
              30,
              30,
            ]}
            cellSize={1}
            cellThickness={
              detailed
                ? 0.45
                : 0.3
            }
            sectionSize={5}
            sectionThickness={1}
            fadeDistance={30}
            fadeStrength={1}
            infiniteGrid
          />


          <Environment
            preset="sunset"
          />

        </Suspense>


        <OrbitControls
          makeDefault
          enableDamping
          dampingFactor={0.08}
          minDistance={
            detailed
              ? 5
              : 6
          }
          maxDistance={
            detailed
              ? 36
              : 26
          }
          maxPolarAngle={
            Math.PI / 2.05
          }
        />

      </Canvas>


      {detailed && (

        <div className="twin-layer-control">

          <div className="twin-layer-buttons">

            <button
              type="button"
              className={
                visualLayer ===
                  "crop"
                  ? "active"
                  : ""
              }
              onClick={() =>
                setVisualLayer(
                  "crop"
                )
              }
            >
              Cultivo
            </button>


            <button
              type="button"
              className={
                visualLayer ===
                  "ndvi"
                  ? "active"
                  : ""
              }
              disabled={
                ndvi === null
              }
              onClick={() =>
                setVisualLayer(
                  "ndvi"
                )
              }
            >
              NDVI
            </button>


            <button
              type="button"
              className={
                visualLayer ===
                  "ndmi"
                  ? "active"
                  : ""
              }
              disabled={
                ndmi === null
              }
              onClick={() =>
                setVisualLayer(
                  "ndmi"
                )
              }
            >
              NDMI
            </button>


            <button
              type="button"
              className={
                visualLayer ===
                  "soil-moisture"
                  ? "active"
                  : ""
              }
              disabled={
                shownSoilMoisture ===
                  null
              }
              onClick={() =>
                setVisualLayer(
                  "soil-moisture"
                )
              }
            >
              Humedad
            </button>


            <button
              type="button"
              className={
                visualLayer ===
                  "soil-profile"
                  ? "active"
                  : ""
              }
              onClick={() =>
                setVisualLayer(
                  "soil-profile"
                )
              }
            >
              Suelo
            </button>

          </div>


          <div className="twin-layer-caption">

            <strong>
              {layerLabel(
                visualLayer
              )}
            </strong>


            {visualLayer ===
              "ndvi"
              && (

              <span>
                {formatLayerValue(
                  ndvi
                )}
                {" · "}
                valor parcelario
              </span>

            )}


            {visualLayer ===
              "ndmi"
              && (

              <span>
                {formatLayerValue(
                  ndmi
                )}
                {" · "}
                valor parcelario
              </span>

            )}


            {visualLayer ===
              "soil-moisture"
              && (

              <span>
                {formatLayerValue(
                  shownSoilMoisture
                )}
                {" · "}
                humedad del TwinState
              </span>

            )}


            {visualLayer ===
              "soil-profile"
              && (

              <span>
                Perfil visual de 3 capas
              </span>

            )}


            {visualLayer ===
              "crop"
              && (

              <span>
                Vista operativa del cultivo
              </span>

            )}

          </div>


          {(visualLayer ===
              "ndvi"
            ||
            visualLayer ===
              "ndmi")
            && (

            <small>
              Capa uniforme: aún no se dispone de un raster espacial por píxel.
            </small>

          )}


          {visualLayer ===
            "soil-profile"
            && (

            <small>
              Las capas representan profundidad visual; no son tres sensores independientes.
            </small>

          )}

        </div>

      )}


      {detailed && (

        <div className="twin-crop-scale">

          <div>

            <strong>
              {cropStats
                .profile
                .label}
            </strong>

            <span>
              {cropStats
                .effectiveAreaHa
                .toFixed(2)} ha
            </span>

          </div>


          <small>

            Representación espacial simplificada
            {" · "}

            {cropStats
              .metersPerLocalUnit !==
              null
              ? `1 unidad 3D ≈ ${
                  cropStats
                    .metersPerLocalUnit
                    .toFixed(1)
                } m`
              : "escala visual normalizada"}

          </small>


          <em>

            El número de plantas es representativo; se priorizan
            proporción, filas y legibilidad del cultivo.

          </em>

        </div>

      )}

    </div>
  );
}
