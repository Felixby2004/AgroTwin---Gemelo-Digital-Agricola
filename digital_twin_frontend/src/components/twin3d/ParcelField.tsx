import {
  useMemo,
} from "react";

import type {
  ParcelState,
} from "../../api/twin";

import type {
  ParcelGeometryResponse,
} from "../../api/parcels";

import type {
  TwinSceneMode,
} from "./TwinScene";

import type {
  TwinAgronomicLayer,
} from "../../utils/agronomicLayers";

import {
  CropInstances,
} from "./CropInstances";

import {
  SoilLayers,
} from "./SoilLayers";

import {
  buildParcelProjection,
  createParcelShape,
} from "../../utils/parcelGeometry3d";

import {
  ndmiColor,
  soilMoistureColor,
} from "../../utils/agronomicLayers";


interface ParcelFieldProps {
  state: ParcelState | null;

  mode: TwinSceneMode;

  visualLayer?: TwinAgronomicLayer;

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


function getVariable(
  state: ParcelState | null,
  variable: string
) {

  return state
    ?.trusted_state
    ?.find(
      (entry) =>
        entry.variable ===
        variable
    );
}


function getNumericValue(
  state: ParcelState | null,
  variable: string
): number | null {

  const item =
    getVariable(
      state,
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
        (value) =>
          typeof value ===
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


export function ParcelField({
  state,
  mode,
  visualLayer = "crop",
  soilMoistureOverride = null,
  geometry = null,
  cropType = null,
  areaHa = null,
}: ParcelFieldProps) {

  const detailed =
    mode === "detailed";


  const projection =
    useMemo(
      () =>
        buildParcelProjection(
          geometry
        ),
      [
        geometry,
      ]
    );


  const shape =
    useMemo(
      () =>
        createParcelShape(
          projection
        ),
      [
        projection,
      ]
    );


  const soilMoisture =
    getNumericValue(
      state,
      "soil_water_state"
    );


  const visualSoilMoisture =
    typeof soilMoistureOverride ===
      "number"
      ? soilMoistureOverride
      : soilMoisture;


  const ndvi =
    getNumericValue(
      state,
      "ndvi"
    );


  const ndmi =
    getNumericValue(
      state,
      "ndmi"
    );


  const irrigation =
    state
      ?.recommendation
      ?.irrigation_mm
    ??
    0;


  const plantHealth =
    useMemo(
      () => {

        if (
          typeof ndvi !==
            "number"
        ) {
          return 0.62;
        }


        return Math.max(
          0.12,
          Math.min(
            1,
            ndvi
          )
        );
      },
      [
        ndvi,
      ]
    );


  const wetness =
    typeof visualSoilMoisture ===
      "number"
      ? Math.max(
          0,
          Math.min(
            1,
            visualSoilMoisture
            /
            0.40
          )
        )
      : 0.5;


  const defaultSurfaceColor =
    wetness > 0.66
      ? "#5f4a3b"
      : wetness > 0.42
        ? "#765943"
        : "#8d6b4d";


  const surfaceColor =
    visualLayer ===
      "ndmi"
      ? ndmiColor(
          ndmi
        )
      : visualLayer ===
          "soil-moisture"
        ? soilMoistureColor(
            visualSoilMoisture
          )
        : visualLayer ===
            "ndvi"
          ? "#625347"
          : defaultSurfaceColor;


  const profileMode =
    visualLayer ===
      "soil-profile";


  const showCrops =
    !profileMode;


  return (
    <group>

      {detailed ? (

        <SoilLayers
          moisture={
            visualSoilMoisture
          }
          shape={
            shape
          }
          profileMode={
            profileMode
          }
        />

      ) : shape ? (

        <mesh
          rotation={[
            Math.PI / 2,
            0,
            0,
          ]}
          position={[
            0,
            -0.02,
            0,
          ]}
          receiveShadow
        >

          <extrudeGeometry
            args={[
              shape,
              {
                depth: 0.42,
                bevelEnabled: false,
                steps: 1,
              },
            ]}
          />

          <meshStandardMaterial
            color={
              surfaceColor
            }
            roughness={0.95}
          />

        </mesh>

      ) : (

        <mesh
          position={[
            0,
            -0.25,
            0,
          ]}
          receiveShadow
        >

          <boxGeometry
            args={[
              18,
              0.45,
              11,
            ]}
          />

          <meshStandardMaterial
            color={
              surfaceColor
            }
            roughness={0.95}
          />

        </mesh>

      )}


      {!profileMode && (

        shape ? (

          <mesh
            rotation={[
              Math.PI / 2,
              0,
              0,
            ]}
            position={[
              0,
              0.015,
              0,
            ]}
            receiveShadow
          >

            <shapeGeometry
              args={[
                shape,
              ]}
            />

            <meshStandardMaterial
              color={
                surfaceColor
              }
              roughness={0.92}
            />

          </mesh>

        ) : (

          <mesh
            position={[
              0,
              0,
              0,
            ]}
            receiveShadow
          >

            <boxGeometry
              args={[
                18,
                0.08,
                11,
              ]}
            />

            <meshStandardMaterial
              color={
                surfaceColor
              }
              roughness={0.92}
            />

          </mesh>

        )

      )}


      {showCrops && (

        <CropInstances
          projection={
            projection
          }
          areaHa={
            areaHa
          }
          cropType={
            cropType
          }
          health={
            plantHealth
          }
        />

      )}


      {irrigation > 0
        &&
        visualLayer ===
          "crop"
        && (

        <group>

          <mesh
            position={[
              0,
              1.2,
              0,
            ]}
          >

            <cylinderGeometry
              args={[
                0.10,
                0.10,
                2.1,
                18,
              ]}
            />

            <meshStandardMaterial
              color="#38bdf8"
              transparent
              opacity={0.38}
            />

          </mesh>


          <mesh
            position={[
              0,
              2.28,
              0,
            ]}
          >

            <sphereGeometry
              args={[
                0.17,
                14,
                14,
              ]}
            />

            <meshStandardMaterial
              color="#0ea5e9"
              emissive="#0ea5e9"
              emissiveIntensity={0.12}
            />

          </mesh>

        </group>

      )}

    </group>
  );
}
