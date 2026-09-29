import type {
  Shape,
} from "three";

import {
  soilMoistureColor,
} from "../../utils/agronomicLayers";


interface SoilLayersProps {
  moisture: number | null;

  shape?:
    | Shape
    | null;

  profileMode?: boolean;
}


export function SoilLayers({
  moisture,
  shape = null,
  profileMode = false,
}: SoilLayersProps) {

  const wet =
    typeof moisture === "number"
      ? Math.max(
          0,
          Math.min(
            1,
            moisture / 0.4
          )
        )
      : 0.4;


  const moistureTone =
    soilMoistureColor(
      moisture
    );


  const upperColor =
    profileMode
      ? moistureTone
      : wet > 0.65
        ? "#4f4035"
        : wet > 0.4
          ? "#6f523b"
          : "#8a6545";


  const middleColor =
    profileMode
      ? wet > 0.60
        ? "#53665f"
        : "#684d3b"
      : "#68472f";


  const deepColor =
    profileMode
      ? wet > 0.60
        ? "#404f4c"
        : "#4c372c"
      : "#4f3627";


  const firstY =
    profileMode
      ? -0.02
      : -0.03;

  const secondY =
    profileMode
      ? -0.39
      : -0.33;

  const thirdY =
    profileMode
      ? -0.81
      : -0.67;


  const firstDepth =
    profileMode
      ? 0.28
      : 0.30;

  const secondDepth =
    profileMode
      ? 0.31
      : 0.34;

  const thirdDepth =
    profileMode
      ? 0.36
      : 0.38;


  if (shape) {

    return (
      <group>

        <mesh
          rotation={[
            Math.PI / 2,
            0,
            0,
          ]}
          position={[
            0,
            firstY,
            0,
          ]}
          receiveShadow
        >

          <extrudeGeometry
            args={[
              shape,
              {
                depth:
                  firstDepth,
                bevelEnabled:
                  false,
                steps: 1,
              },
            ]}
          />

          <meshStandardMaterial
            color={
              upperColor
            }
            roughness={0.98}
          />

        </mesh>


        <mesh
          rotation={[
            Math.PI / 2,
            0,
            0,
          ]}
          position={[
            0,
            secondY,
            0,
          ]}
          receiveShadow
        >

          <extrudeGeometry
            args={[
              shape,
              {
                depth:
                  secondDepth,
                bevelEnabled:
                  false,
                steps: 1,
              },
            ]}
          />

          <meshStandardMaterial
            color={
              middleColor
            }
            roughness={1}
          />

        </mesh>


        <mesh
          rotation={[
            Math.PI / 2,
            0,
            0,
          ]}
          position={[
            0,
            thirdY,
            0,
          ]}
          receiveShadow
        >

          <extrudeGeometry
            args={[
              shape,
              {
                depth:
                  thirdDepth,
                bevelEnabled:
                  false,
                steps: 1,
              },
            ]}
          />

          <meshStandardMaterial
            color={
              deepColor
            }
            roughness={1}
          />

        </mesh>

      </group>
    );
  }


  return (
    <group>

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
            0.35,
            11,
          ]}
        />

        <meshStandardMaterial
          color={
            upperColor
          }
          roughness={1}
        />

      </mesh>


      <mesh
        position={[
          0,
          -0.63,
          0,
        ]}
        receiveShadow
      >

        <boxGeometry
          args={[
            18,
            0.38,
            11,
          ]}
        />

        <meshStandardMaterial
          color={
            middleColor
          }
          roughness={1}
        />

      </mesh>


      <mesh
        position={[
          0,
          -1.02,
          0,
        ]}
        receiveShadow
      >

        <boxGeometry
          args={[
            18,
            0.4,
            11,
          ]}
        />

        <meshStandardMaterial
          color={
            deepColor
          }
          roughness={1}
        />

      </mesh>

    </group>
  );
}
