import {
  Html,
} from "@react-three/drei";


interface SensorMarkerProps {
  position: [
    number,
    number,
    number
  ];

  label: string;

  value: string;

  type:
    | "soil"
    | "temperature"
    | "satellite";
}


export function SensorMarker({
  position,
  label,
  value,
  type,
}: SensorMarkerProps) {

  const color =
    type === "soil"
      ? "#0ea5e9"
      : type === "temperature"
        ? "#f59e0b"
        : "#7c3aed";


  return (
    <group
      position={position}
    >

      <mesh
        position={[
          0,
          0.55,
          0,
        ]}
        castShadow
      >

        <cylinderGeometry
          args={[
            0.06,
            0.08,
            1.1,
            10,
          ]}
        />

        <meshStandardMaterial
          color="#475569"
        />

      </mesh>


      <mesh
        position={[
          0,
          1.15,
          0,
        ]}
        castShadow
      >

        <sphereGeometry
          args={[
            0.17,
            20,
            20,
          ]}
        />

        <meshStandardMaterial
          color={color}
          emissive={color}
          emissiveIntensity={0.15}
        />

      </mesh>


      <Html
        position={[
          0,
          1.55,
          0,
        ]}
        center
        distanceFactor={9}
      >

        <div className="sensor-3d-label">

          <strong>
            {label}
          </strong>

          <span>
            {value}
          </span>

        </div>

      </Html>

    </group>
  );
}