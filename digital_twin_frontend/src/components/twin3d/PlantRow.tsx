interface PlantRowProps {
  z: number;

  health: number;

  xPositions?: number[];

  cropType?:
    | string
    | null;
}


function normalizedCrop(
  cropType:
    | string
    | null
    | undefined
): string {

  return (
    cropType
      ?.trim()
      .toLowerCase()
    || ""
  );
}


export function PlantRow({
  z,
  health,
  xPositions,
  cropType = null,
}: PlantRowProps) {

  const positions =
    xPositions
    ??
    [
      -4, -3, -2, -1,
       0,  1,  2,  3, 4,
    ];


  const crop =
    normalizedCrop(
      cropType
    );


  const isPotato =
    crop === "potato"
    ||
    crop === "papa";


  const isRice =
    crop === "rice"
    ||
    crop === "arroz";


  const height =
    isPotato
      ? (
          0.30
          +
          health * 0.32
        )
      : isRice
        ? (
            0.55
            +
            health * 0.55
          )
        : (
            0.65
            +
            health * 0.85
          );


  const color =
    health >= 0.65
      ? "#1f9d55"
      : health >= 0.4
        ? "#78b447"
        : "#b6a440";


  return (
    <group>

      {positions.map(
        (
          x,
          index
        ) => {

          if (isPotato) {

            return (
              <group
                key={
                  `${z}-${index}`
                }
                position={[
                  x,
                  0.08,
                  z,
                ]}
              >

                <mesh
                  position={[
                    0,
                    height * 0.55,
                    0,
                  ]}
                  castShadow
                >

                  <cylinderGeometry
                    args={[
                      0.025,
                      0.035,
                      height,
                      7,
                    ]}
                  />

                  <meshStandardMaterial
                    color={color}
                  />

                </mesh>


                {[
                  [-0.12, 0.32, 0.02],
                  [0.13, 0.42, -0.02],
                  [0.00, 0.52, 0.08],
                ].map(
                  (
                    offset,
                    leafIndex
                  ) => (

                    <mesh
                      key={
                        leafIndex
                      }
                      position={[
                        offset[0],
                        height
                        * offset[1]
                        * 1.8,
                        offset[2],
                      ]}
                      scale={[
                        1.0,
                        0.55,
                        1.25,
                      ]}
                      castShadow
                    >

                      <sphereGeometry
                        args={[
                          0.13,
                          10,
                          8,
                        ]}
                      />

                      <meshStandardMaterial
                        color={color}
                      />

                    </mesh>
                  )
                )}

              </group>
            );
          }


          if (isRice) {

            return (
              <group
                key={
                  `${z}-${index}`
                }
                position={[
                  x,
                  0.05,
                  z,
                ]}
              >

                {[
                  -0.07,
                  0,
                  0.07,
                ].map(
                  (
                    offset,
                    stalkIndex
                  ) => (

                    <mesh
                      key={
                        stalkIndex
                      }
                      position={[
                        offset,
                        height / 2,
                        0,
                      ]}
                      rotation={[
                        0,
                        0,
                        offset * 1.4,
                      ]}
                      castShadow
                    >

                      <cylinderGeometry
                        args={[
                          0.014,
                          0.018,
                          height,
                          6,
                        ]}
                      />

                      <meshStandardMaterial
                        color={color}
                      />

                    </mesh>
                  )
                )}

              </group>
            );
          }


          return (
            <group
              key={
                `${z}-${index}`
              }
              position={[
                x,
                0.15,
                z,
              ]}
            >

              <mesh
                position={[
                  0,
                  height / 2,
                  0,
                ]}
                castShadow
              >

                <cylinderGeometry
                  args={[
                    0.04,
                    0.06,
                    height,
                    8,
                  ]}
                />

                <meshStandardMaterial
                  color={color}
                />

              </mesh>


              <mesh
                position={[
                  -0.14,
                  height * 0.65,
                  0,
                ]}
                rotation={[
                  0,
                  0,
                  0.75,
                ]}
                castShadow
              >

                <boxGeometry
                  args={[
                    0.28,
                    0.06,
                    0.12,
                  ]}
                />

                <meshStandardMaterial
                  color={color}
                />

              </mesh>


              <mesh
                position={[
                  0.14,
                  height * 0.78,
                  0,
                ]}
                rotation={[
                  0,
                  0,
                  -0.75,
                ]}
                castShadow
              >

                <boxGeometry
                  args={[
                    0.28,
                    0.06,
                    0.12,
                  ]}
                />

                <meshStandardMaterial
                  color={color}
                />

              </mesh>

            </group>
          );
        }
      )}

    </group>
  );
}
