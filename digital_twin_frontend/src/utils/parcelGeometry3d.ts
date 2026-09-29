import {
  Shape,
  Vector2,
} from "three";

import type {
  ParcelGeometryResponse,
} from "../api/parcels";


export interface LocalParcelPoint {
  x: number;
  z: number;
}


export interface ParcelLocalBounds {
  minX: number;
  maxX: number;
  minZ: number;
  maxZ: number;
  width: number;
  depth: number;
}


export interface ParcelProjection {
  points: LocalParcelPoint[];

  bounds: ParcelLocalBounds;

  centerLongitude: number;

  centerLatitude: number;

  metersPerDegreeLongitude: number;

  metersPerDegreeLatitude: number;

  scale: number;

  realAreaHa: number;

  localArea: number;
}


const MAX_WIDTH = 18;
const MAX_DEPTH = 11;


function removeClosingPoint(
  coordinates: number[][]
): number[][] {

  if (
    coordinates.length < 2
  ) {
    return coordinates;
  }


  const first =
    coordinates[0];

  const last =
    coordinates[
      coordinates.length - 1
    ];


  if (
    first.length >= 2
    &&
    last.length >= 2
    &&
    first[0] === last[0]
    &&
    first[1] === last[1]
  ) {
    return coordinates.slice(
      0,
      -1
    );
  }


  return coordinates;
}


function polygonArea(
  points: LocalParcelPoint[]
): number {

  if (points.length < 3) {
    return 0;
  }

  let sum = 0;

  for (
    let index = 0;
    index < points.length;
    index += 1
  ) {

    const current =
      points[index];

    const next =
      points[
        (index + 1)
        % points.length
      ];

    sum +=
      current.x * next.z
      -
      next.x * current.z;
  }

  return Math.abs(sum) / 2;
}


function deterministicNoise(
  index: number,
  salt: number
): number {

  const value =
    Math.sin(
      (index + 1)
      *
      (12.9898 + salt)
    )
    *
    43758.5453;

  return (
    value
    -
    Math.floor(value)
  );
}


export function buildParcelProjection(
  geometry:
    | ParcelGeometryResponse["geometry"]
    | null
    | undefined
): ParcelProjection | null {

  const rawRing =
    geometry
      ?.coordinates
      ?.[0];


  if (
    !Array.isArray(
      rawRing
    )
    ||
    rawRing.length < 3
  ) {
    return null;
  }


  const ring =
    removeClosingPoint(
      rawRing
    )
    .filter(
      (coordinate) =>
        Array.isArray(
          coordinate
        )
        &&
        coordinate.length >= 2
        &&
        typeof coordinate[0] ===
          "number"
        &&
        typeof coordinate[1] ===
          "number"
    );


  if (
    ring.length < 3
  ) {
    return null;
  }


  const longitudeValues =
    ring.map(
      (coordinate) =>
        coordinate[0]
    );

  const latitudeValues =
    ring.map(
      (coordinate) =>
        coordinate[1]
    );


  const centerLongitude =
    (
      Math.min(
        ...longitudeValues
      )
      +
      Math.max(
        ...longitudeValues
      )
    )
    / 2;


  const centerLatitude =
    (
      Math.min(
        ...latitudeValues
      )
      +
      Math.max(
        ...latitudeValues
      )
    )
    / 2;


  const latitudeRadians =
    (
      centerLatitude
      * Math.PI
    )
    / 180;


  const metersPerDegreeLongitude =
    Math.max(
      1,
      111_320
      * Math.cos(
        latitudeRadians
      )
    );


  const metersPerDegreeLatitude =
    110_540;


  const meterPoints =
    ring.map(
      (coordinate) => ({

        x:
          (
            coordinate[0]
            - centerLongitude
          )
          * metersPerDegreeLongitude,

        /*
         * North is negative Z so the parcel reads
         * naturally from the default camera.
         */
        z:
          -(
            coordinate[1]
            - centerLatitude
          )
          * metersPerDegreeLatitude,
      })
    );


  const meterXs =
    meterPoints.map(
      (point) =>
        point.x
    );

  const meterZs =
    meterPoints.map(
      (point) =>
        point.z
    );


  const meterWidth =
    Math.max(
      Math.max(
        ...meterXs
      )
      -
      Math.min(
        ...meterXs
      ),
      0.001
    );


  const meterDepth =
    Math.max(
      Math.max(
        ...meterZs
      )
      -
      Math.min(
        ...meterZs
      ),
      0.001
    );


  const scale =
    Math.min(
      MAX_WIDTH
      / meterWidth,

      MAX_DEPTH
      / meterDepth
    );


  const points =
    meterPoints.map(
      (point) => ({
        x:
          point.x
          * scale,

        z:
          point.z
          * scale,
      })
    );


  const xs =
    points.map(
      (point) =>
        point.x
    );

  const zs =
    points.map(
      (point) =>
        point.z
    );


  const minX =
    Math.min(
      ...xs
    );

  const maxX =
    Math.max(
      ...xs
    );

  const minZ =
    Math.min(
      ...zs
    );

  const maxZ =
    Math.max(
      ...zs
    );


  const realAreaHa =
    polygonArea(
      meterPoints
    )
    /
    10_000;


  const localArea =
    polygonArea(
      points
    );


  return {
    points,

    bounds: {
      minX,
      maxX,
      minZ,
      maxZ,
      width:
        maxX - minX,
      depth:
        maxZ - minZ,
    },

    centerLongitude,

    centerLatitude,

    metersPerDegreeLongitude,

    metersPerDegreeLatitude,

    scale,

    realAreaHa,

    localArea,
  };
}


export function createParcelShape(
  projection:
    | ParcelProjection
    | null
): Shape | null {

  if (
    !projection
    ||
    projection.points.length < 3
  ) {
    return null;
  }


  const vectors =
    projection.points.map(
      (point) =>
        new Vector2(
          point.x,
          point.z
        )
    );


  return new Shape(
    vectors
  );
}


export function projectGeoPointToLocal(
  projection: ParcelProjection,
  longitude: number,
  latitude: number
): LocalParcelPoint {

  return {
    x:
      (
        longitude
        - projection
          .centerLongitude
      )
      * projection
        .metersPerDegreeLongitude
      * projection.scale,

    z:
      -(
        latitude
        - projection
          .centerLatitude
      )
      * projection
        .metersPerDegreeLatitude
      * projection.scale,
  };
}


export function pointInParcelPolygon(
  point: LocalParcelPoint,
  polygon: LocalParcelPoint[]
): boolean {

  let inside =
    false;


  for (
    let index = 0,
      previous =
        polygon.length - 1;

    index < polygon.length;

    previous = index++
  ) {

    const currentPoint =
      polygon[
        index
      ];

    const previousPoint =
      polygon[
        previous
      ];


    const intersects =
      (
        currentPoint.z >
        point.z
      )
      !==
      (
        previousPoint.z >
        point.z
      )
      &&
      point.x
      <
      (
        (
          previousPoint.x
          - currentPoint.x
        )
        *
        (
          point.z
          - currentPoint.z
        )
        /
        (
          previousPoint.z
          - currentPoint.z
          || Number.EPSILON
        )
        +
        currentPoint.x
      );


    if (
      intersects
    ) {
      inside =
        !inside;
    }
  }


  return inside;
}


export interface ParcelPlantRow {
  z: number;
  xPositions: number[];
}


export function buildPlantRows(
  projection:
    | ParcelProjection
    | null
): ParcelPlantRow[] {

  if (!projection) {

    return [
      {
        z: -2,
        xPositions:
          [
            -4, -3, -2, -1,
             0,  1,  2,  3, 4,
          ],
      },
      {
        z: -1,
        xPositions:
          [
            -4, -3, -2, -1,
             0,  1,  2,  3, 4,
          ],
      },
      {
        z: 0,
        xPositions:
          [
            -4, -3, -2, -1,
             0,  1,  2,  3, 4,
          ],
      },
      {
        z: 1,
        xPositions:
          [
            -4, -3, -2, -1,
             0,  1,  2,  3, 4,
          ],
      },
      {
        z: 2,
        xPositions:
          [
            -4, -3, -2, -1,
             0,  1,  2,  3, 4,
          ],
      },
    ];
  }


  const {
    bounds,
    points,
  } =
    projection;


  const margin =
    0.30;

  const rowSpacing =
    Math.max(
      0.55,
      Math.min(
        0.85,
        bounds.depth
        / 7
      )
    );

  const plantSpacing =
    Math.max(
      0.55,
      Math.min(
        0.85,
        bounds.width
        / 11
      )
    );


  const rows:
    ParcelPlantRow[] =
    [];


  for (
    let z =
      bounds.minZ
      + margin;

    z <=
      bounds.maxZ
      - margin;

    z += rowSpacing
  ) {

    const xPositions:
      number[] =
      [];


    for (
      let x =
        bounds.minX
        + margin;

      x <=
        bounds.maxX
        - margin;

      x += plantSpacing
    ) {

      if (
        pointInParcelPolygon(
          {
            x,
            z,
          },
          points
        )
      ) {

        xPositions.push(
          x
        );
      }
    }


    if (
      xPositions.length > 0
    ) {

      rows.push({
        z,
        xPositions,
      });
    }
  }


  return rows;
}



export interface CropRenderPoint {
  x: number;
  z: number;
  yaw: number;
  scale: number;
}


export function buildRepresentativeCropPoints(
  projection:
    | ParcelProjection
    | null,
  count: number,
  rowToPlantSpacingRatio = 1
): CropRenderPoint[] {

  const safeCount =
    Math.max(
      1,
      Math.floor(count)
    );


  const bounds =
    projection
      ?.bounds
    ??
    {
      minX: -5,
      maxX: 5,
      minZ: -3,
      maxZ: 3,
      width: 10,
      depth: 6,
    };


  const polygon =
    projection
      ?.points
    ??
    [
      { x: -5, z: -3 },
      { x: 5, z: -3 },
      { x: 5, z: 3 },
      { x: -5, z: 3 },
    ];


  const boundsArea =
    Math.max(
      0.001,
      bounds.width
      *
      bounds.depth
    );


  const polygonAreaFraction =
    projection
      ? Math.max(
          0.08,
          Math.min(
            1,
            projection.localArea
            /
            boundsArea
          )
        )
      : 1;


  const candidateCount =
    Math.ceil(
      safeCount
      /
      polygonAreaFraction
      *
      1.12
    );


  const parcelAspect =
    Math.max(
      0.25,
      Math.min(
        4,
        bounds.width
        /
        Math.max(
          0.001,
          bounds.depth
        )
      )
    );


  /*
   * If real row spacing is much wider than plant spacing
   * (e.g. maize), we should visually preserve that pattern:
   * many plants along each row, fewer rows across the field.
   */
  const cropSpacingRatio =
    Math.max(
      0.85,
      Math.min(
        10,
        rowToPlantSpacingRatio
        * 1.55
      )
    );


  const layoutRatio =
    parcelAspect
    *
    cropSpacingRatio;


  const columns =
    Math.max(
      1,
      Math.ceil(
        Math.sqrt(
          candidateCount
          *
          layoutRatio
        )
      )
    );


  const rows =
    Math.max(
      1,
      Math.ceil(
        candidateCount
        /
        columns
      )
    );


  const cellWidth =
    bounds.width
    /
    columns;


  const cellDepth =
    bounds.depth
    /
    rows;


  const points:
    CropRenderPoint[] =
    [];


  let index = 0;


  for (
    let row = 0;
    row < rows
    &&
    points.length < safeCount;
    row += 1
  ) {

    for (
      let column = 0;
      column < columns
      &&
      points.length < safeCount;
      column += 1
    ) {

      const rowOffset =
        row % 2 === 0
          ? 0
          : 0.12;


      const jitterX =
        (
          deterministicNoise(
            index,
            0.31
          )
          - 0.5
        )
        *
        cellWidth
        *
        0.045;


      const jitterZ =
        (
          deterministicNoise(
            index,
            0.73
          )
          - 0.5
        )
        *
        cellDepth
        *
        0.025;


      const x =
        bounds.minX
        +
        (
          column
          + 0.5
          + rowOffset
        )
        *
        cellWidth
        +
        jitterX;


      const z =
        bounds.minZ
        +
        (
          row
          + 0.5
        )
        *
        cellDepth
        +
        jitterZ;


      index += 1;


      if (
        !pointInParcelPolygon(
          { x, z },
          polygon
        )
      ) {
        continue;
      }


      points.push({
        x,
        z,

        yaw:
          (
            deterministicNoise(
              index,
              1.17
            )
            - 0.5
          )
          *
          0.28,

        scale:
          0.88
          +
          deterministicNoise(
            index,
            1.91
          )
          *
          0.24,
      });
    }
  }


  let attempt = 1;


  while (
    points.length < safeCount
    &&
    attempt < safeCount * 40
  ) {

    const x =
      bounds.minX
      +
      deterministicNoise(
        attempt,
        2.41
      )
      *
      bounds.width;


    const z =
      bounds.minZ
      +
      deterministicNoise(
        attempt,
        4.07
      )
      *
      bounds.depth;


    attempt += 1;


    if (
      !pointInParcelPolygon(
        { x, z },
        polygon
      )
    ) {
      continue;
    }


    points.push({
      x,
      z,

      yaw:
        (
          deterministicNoise(
            attempt,
            5.71
          )
          - 0.5
        )
        *
        0.36,

      scale:
        0.88
        +
        deterministicNoise(
          attempt,
          7.13
        )
        *
        0.24,
    });
  }


  return points;
}
