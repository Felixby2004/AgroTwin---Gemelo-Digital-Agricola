import {
  useEffect,
  useMemo,
  useRef,
} from "react";

import {
  Color,
  InstancedMesh,
  Object3D,
} from "three";

import type {
  ParcelProjection,
  CropRenderPoint,
} from "../../utils/parcelGeometry3d";

import {
  buildRepresentativeCropPoints,
} from "../../utils/parcelGeometry3d";

import {
  estimateCropPopulation,
  estimateRenderedInstanceCount,
  getCropVisualProfile,
  resolveVisualizationAreaHa,
  type CropModelKind,
} from "../../utils/cropVisualProfiles";


type PrimitiveKind =
  | "cylinder"
  | "box"
  | "sphere"
  | "cone";


interface InstancedPartProps {
  points: CropRenderPoint[];

  primitive: PrimitiveKind;

  color:
    | string
    | Color;

  offset?: [
    number,
    number,
    number
  ];

  scale: [
    number,
    number,
    number
  ];

  rotation?: [
    number,
    number,
    number
  ];

  alternateZ?: boolean;

  castShadow?: boolean;
}


function InstancedPart({
  points,
  primitive,
  color,
  offset = [
    0,
    0,
    0,
  ],
  scale,
  rotation = [
    0,
    0,
    0,
  ],
  alternateZ = false,
  castShadow = true,
}: InstancedPartProps) {

  const ref =
    useRef<InstancedMesh>(
      null
    );


  useEffect(
    () => {

      const mesh =
        ref.current;


      if (!mesh) {
        return;
      }


      const dummy =
        new Object3D();


      points.forEach(
        (
          point,
          index
        ) => {

          dummy.position.set(
            point.x
            +
            offset[0],

            offset[1],

            point.z
            +
            offset[2]
          );


          dummy.rotation.set(
            rotation[0],

            point.yaw
            +
            rotation[1],

            alternateZ
              &&
              index % 2 === 1
              ? -rotation[2]
              : rotation[2]
          );


          dummy.scale.set(
            scale[0]
            *
            point.scale,

            scale[1]
            *
            point.scale,

            scale[2]
            *
            point.scale
          );


          dummy.updateMatrix();


          mesh.setMatrixAt(
            index,
            dummy.matrix
          );
        }
      );


      mesh.instanceMatrix
        .needsUpdate =
        true;
    },
    [
      points,
      offset,
      scale,
      rotation,
      alternateZ,
    ]
  );


  const shadows =
    castShadow
    &&
    points.length <=
      1800;


  return (
    <instancedMesh
      ref={
        ref
      }
      args={[
        undefined,
        undefined,
        points.length,
      ]}
      castShadow={
        shadows
      }
      receiveShadow={false}
    >

      {primitive ===
        "cylinder" && (

        <cylinderGeometry
          args={[
            1,
            1,
            1,
            6,
          ]}
        />

      )}


      {primitive ===
        "box" && (

        <boxGeometry
          args={[
            1,
            1,
            1,
          ]}
        />

      )}


      {primitive ===
        "sphere" && (

        <icosahedronGeometry
          args={[
            1,
            1,
          ]}
        />

      )}


      {primitive ===
        "cone" && (

        <coneGeometry
          args={[
            1,
            1,
            7,
          ]}
        />

      )}


      <meshStandardMaterial
        color={
          color
        }
        roughness={0.80}
        metalness={0}
      />

    </instancedMesh>
  );
}


function foliageColor(
  healthy: string,
  stressed: string,
  health: number
): Color {

  const safeHealth =
    Math.max(
      0,
      Math.min(
        1,
        health
      )
    );


  return new Color(
    stressed
  )
  .lerp(
    new Color(
      healthy
    ),
    safeHealth
  );
}


interface CropModelProps {
  points: CropRenderPoint[];

  model: CropModelKind;

  health: number;

  healthyColor: string;

  stressedColor: string;

  baseScale: number;
}


function CropModel({
  points,
  model,
  health,
  healthyColor,
  stressedColor,
  baseScale,
}: CropModelProps) {

  const green =
    useMemo(
      () =>
        foliageColor(
          healthyColor,
          stressedColor,
          health
        ),
      [
        healthyColor,
        stressedColor,
        health,
      ]
    );


  switch (model) {

    case "maize":

      return (
        <>

          <InstancedPart
            points={points}
            primitive="cylinder"
            color="#5f913c"
            offset={[
              0,
              0.66 * baseScale,
              0,
            ]}
            scale={[
              0.024 * baseScale,
              1.24 * baseScale,
              0.024 * baseScale,
            ]}
          />

          <InstancedPart
            points={points}
            primitive="box"
            color={green}
            offset={[
              0,
              0.64 * baseScale,
              0,
            ]}
            scale={[
              0.032 * baseScale,
              0.31 * baseScale,
              0.070 * baseScale,
            ]}
            rotation={[
              0,
              0,
              0.72,
            ]}
            alternateZ
          />

          <InstancedPart
            points={points}
            primitive="box"
            color={green}
            offset={[
              0,
              0.92 * baseScale,
              0,
            ]}
            scale={[
              0.029 * baseScale,
              0.27 * baseScale,
              0.064 * baseScale,
            ]}
            rotation={[
              0,
              Math.PI / 2,
              0.68,
            ]}
            alternateZ
          />

          <InstancedPart
            points={points}
            primitive="cylinder"
            color="#d5a838"
            offset={[
              0.045 * baseScale,
              0.72 * baseScale,
              0,
            ]}
            scale={[
              0.032 * baseScale,
              0.15 * baseScale,
              0.032 * baseScale,
            ]}
            rotation={[
              0,
              0,
              0.18,
            ]}
            castShadow={false}
          />


          <InstancedPart
            points={points}
            primitive="cone"
            color="#c7a54a"
            offset={[
              0,
              1.31 * baseScale,
              0,
            ]}
            scale={[
              0.038 * baseScale,
              0.13 * baseScale,
              0.038 * baseScale,
            ]}
            castShadow={false}
          />

        </>
      );


    case "potato":

      return (
        <>

          <InstancedPart
            points={points}
            primitive="cylinder"
            color="#4f7d38"
            offset={[
              0,
              0.22 * baseScale,
              0,
            ]}
            scale={[
              0.020 * baseScale,
              0.38 * baseScale,
              0.020 * baseScale,
            ]}
          />

          <InstancedPart
            points={points}
            primitive="sphere"
            color={green}
            offset={[
              -0.10 * baseScale,
              0.34 * baseScale,
              0,
            ]}
            scale={[
              0.18 * baseScale,
              0.11 * baseScale,
              0.16 * baseScale,
            ]}
          />

          <InstancedPart
            points={points}
            primitive="sphere"
            color={green}
            offset={[
              0.11 * baseScale,
              0.39 * baseScale,
              0.02 * baseScale,
            ]}
            scale={[
              0.17 * baseScale,
              0.10 * baseScale,
              0.15 * baseScale,
            ]}
          />

          <InstancedPart
            points={points}
            primitive="sphere"
            color={green}
            offset={[
              0,
              0.47 * baseScale,
              -0.07 * baseScale,
            ]}
            scale={[
              0.16 * baseScale,
              0.09 * baseScale,
              0.14 * baseScale,
            ]}
            castShadow={false}
          />

        </>
      );


    case "rice":

      return (
        <>

          {[
            -0.07,
            -0.025,
            0.025,
            0.07,
          ].map(
            (
              offset,
              index
            ) => (

              <InstancedPart
                key={index}
                points={points}
                primitive="cylinder"
                color={green}
                offset={[
                  offset
                  * baseScale,
                  0.42 * baseScale,
                  0,
                ]}
                scale={[
                  0.010 * baseScale,
                  0.78 * baseScale,
                  0.010 * baseScale,
                ]}
                rotation={[
                  0,
                  0,
                  offset * 1.6,
                ]}
                castShadow={false}
              />

            )
          )}

        </>
      );


    case "wheat":

      return (
        <>

          <InstancedPart
            points={points}
            primitive="cylinder"
            color="#779b48"
            offset={[
              0,
              0.46 * baseScale,
              0,
            ]}
            scale={[
              0.010 * baseScale,
              0.86 * baseScale,
              0.010 * baseScale,
            ]}
            castShadow={false}
          />

          <InstancedPart
            points={points}
            primitive="cone"
            color="#c4a95b"
            offset={[
              0,
              0.94 * baseScale,
              0,
            ]}
            scale={[
              0.050 * baseScale,
              0.24 * baseScale,
              0.050 * baseScale,
            ]}
            castShadow={false}
          />

        </>
      );


    case "onion":

      return (
        <>

          {[
            -0.04,
            0,
            0.04,
          ].map(
            (
              offset,
              index
            ) => (

              <InstancedPart
                key={index}
                points={points}
                primitive="cylinder"
                color={green}
                offset={[
                  offset
                  * baseScale,
                  0.28 * baseScale,
                  0,
                ]}
                scale={[
                  0.014 * baseScale,
                  0.50 * baseScale,
                  0.014 * baseScale,
                ]}
                rotation={[
                  0,
                  0,
                  offset * 2.2,
                ]}
                castShadow={false}
              />

            )
          )}

        </>
      );


    case "tomato":

      return (
        <>

          <InstancedPart
            points={points}
            primitive="cylinder"
            color="#507a38"
            offset={[
              0,
              0.38 * baseScale,
              0,
            ]}
            scale={[
              0.022 * baseScale,
              0.68 * baseScale,
              0.022 * baseScale,
            ]}
          />

          <InstancedPart
            points={points}
            primitive="sphere"
            color={green}
            offset={[
              -0.08 * baseScale,
              0.52 * baseScale,
              0,
            ]}
            scale={[
              0.22 * baseScale,
              0.17 * baseScale,
              0.20 * baseScale,
            ]}
          />

          <InstancedPart
            points={points}
            primitive="sphere"
            color={green}
            offset={[
              0.10 * baseScale,
              0.61 * baseScale,
              -0.03 * baseScale,
            ]}
            scale={[
              0.20 * baseScale,
              0.15 * baseScale,
              0.18 * baseScale,
            ]}
          />

          <InstancedPart
            points={points}
            primitive="sphere"
            color="#d74336"
            offset={[
              0.08 * baseScale,
              0.39 * baseScale,
              0.05 * baseScale,
            ]}
            scale={[
              0.045 * baseScale,
              0.045 * baseScale,
              0.045 * baseScale,
            ]}
            castShadow={false}
          />

        </>
      );


    case "avocado":

      return (
        <>

          <InstancedPart
            points={points}
            primitive="cylinder"
            color="#6c4f36"
            offset={[
              0,
              0.62 * baseScale,
              0,
            ]}
            scale={[
              0.055 * baseScale,
              1.05 * baseScale,
              0.055 * baseScale,
            ]}
          />

          <InstancedPart
            points={points}
            primitive="sphere"
            color={green}
            offset={[
              0,
              1.25 * baseScale,
              0,
            ]}
            scale={[
              0.52 * baseScale,
              0.42 * baseScale,
              0.52 * baseScale,
            ]}
          />

          <InstancedPart
            points={points}
            primitive="sphere"
            color={green}
            offset={[
              0.20 * baseScale,
              1.40 * baseScale,
              0.02 * baseScale,
            ]}
            scale={[
              0.34 * baseScale,
              0.28 * baseScale,
              0.34 * baseScale,
            ]}
          />

        </>
      );


    case "coffee":

      return (
        <>

          <InstancedPart
            points={points}
            primitive="cylinder"
            color="#65503b"
            offset={[
              0,
              0.42 * baseScale,
              0,
            ]}
            scale={[
              0.030 * baseScale,
              0.72 * baseScale,
              0.030 * baseScale,
            ]}
          />

          <InstancedPart
            points={points}
            primitive="sphere"
            color={green}
            offset={[
              0,
              0.70 * baseScale,
              0,
            ]}
            scale={[
              0.30 * baseScale,
              0.23 * baseScale,
              0.28 * baseScale,
            ]}
          />

          <InstancedPart
            points={points}
            primitive="sphere"
            color="#c73e3e"
            offset={[
              0.13 * baseScale,
              0.58 * baseScale,
              0.04 * baseScale,
            ]}
            scale={[
              0.032 * baseScale,
              0.032 * baseScale,
              0.032 * baseScale,
            ]}
            castShadow={false}
          />

        </>
      );


    case "sugarcane":

      return (
        <>

          <InstancedPart
            points={points}
            primitive="cylinder"
            color="#6e9b48"
            offset={[
              0,
              0.78 * baseScale,
              0,
            ]}
            scale={[
              0.033 * baseScale,
              1.48 * baseScale,
              0.033 * baseScale,
            ]}
          />

          <InstancedPart
            points={points}
            primitive="box"
            color={green}
            offset={[
              0,
              1.18 * baseScale,
              0,
            ]}
            scale={[
              0.045 * baseScale,
              0.47 * baseScale,
              0.10 * baseScale,
            ]}
            rotation={[
              0,
              0,
              0.77,
            ]}
            alternateZ
          />

          <InstancedPart
            points={points}
            primitive="box"
            color={green}
            offset={[
              0,
              1.30 * baseScale,
              0,
            ]}
            scale={[
              0.040 * baseScale,
              0.43 * baseScale,
              0.09 * baseScale,
            ]}
            rotation={[
              0,
              Math.PI / 2,
              0.72,
            ]}
            alternateZ
            castShadow={false}
          />

        </>
      );


    case "quinoa":

      return (
        <>

          <InstancedPart
            points={points}
            primitive="cylinder"
            color="#6d8741"
            offset={[
              0,
              0.50 * baseScale,
              0,
            ]}
            scale={[
              0.018 * baseScale,
              0.92 * baseScale,
              0.018 * baseScale,
            ]}
            castShadow={false}
          />

          <InstancedPart
            points={points}
            primitive="cone"
            color="#b4775b"
            offset={[
              0,
              1.02 * baseScale,
              0,
            ]}
            scale={[
              0.10 * baseScale,
              0.34 * baseScale,
              0.10 * baseScale,
            ]}
            castShadow={false}
          />

        </>
      );


    case "generic":
    default:

      return (
        <>

          <InstancedPart
            points={points}
            primitive="cylinder"
            color="#587c3b"
            offset={[
              0,
              0.43 * baseScale,
              0,
            ]}
            scale={[
              0.025 * baseScale,
              0.75 * baseScale,
              0.025 * baseScale,
            ]}
          />

          <InstancedPart
            points={points}
            primitive="sphere"
            color={green}
            offset={[
              0,
              0.70 * baseScale,
              0,
            ]}
            scale={[
              0.22 * baseScale,
              0.16 * baseScale,
              0.20 * baseScale,
            ]}
          />

        </>
      );
  }
}


interface CropInstancesProps {
  projection:
    | ParcelProjection
    | null;

  areaHa:
    | number
    | null
    | undefined;

  cropType:
    | string
    | null
    | undefined;

  health: number;
}


export function CropInstances({
  projection,
  areaHa,
  cropType,
  health,
}: CropInstancesProps) {

  const profile =
    useMemo(
      () =>
        getCropVisualProfile(
          cropType
        ),
      [
        cropType,
      ]
    );


  const effectiveAreaHa =
    useMemo(
      () =>
        resolveVisualizationAreaHa(
          areaHa,
          projection
            ?.realAreaHa
        ),
      [
        areaHa,
        projection,
      ]
    );


  const actualPopulation =
    useMemo(
      () =>
        estimateCropPopulation(
          effectiveAreaHa,
          profile
        ),
      [
        effectiveAreaHa,
        profile,
      ]
    );


  const renderedCount =
    useMemo(
      () =>
        estimateRenderedInstanceCount(
          actualPopulation,
          profile
        ),
      [
        actualPopulation,
        profile,
      ]
    );


  const points =
    useMemo(
      () =>
        buildRepresentativeCropPoints(
          projection,
          renderedCount,
          profile.rowSpacingM
          /
          Math.max(
            0.01,
            profile.plantSpacingM
          )
        ),
      [
        projection,
        renderedCount,
        profile,
      ]
    );


  return (
    <CropModel
      points={
        points
      }
      model={
        profile.key
      }
      health={
        health
      }
      healthyColor={
        profile.healthyColor
      }
      stressedColor={
        profile.stressedColor
      }
      baseScale={
        profile.baseScale
      }
    />
  );
}
