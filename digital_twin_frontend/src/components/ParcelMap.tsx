import {
  useEffect,
  useMemo,
  useState,
} from "react";

import {
  CircleMarker,
  GeoJSON,
  MapContainer,
  Polygon,
  TileLayer,
  useMap,
  useMapEvents,
} from "react-leaflet";

import {
  useNavigate,
} from "react-router-dom";

import {
  Check,
  Map as MapIcon,
  Mountain,
  RotateCcw,
  Satellite,
  Trash2,
  Undo2,
} from "lucide-react";

import L, {
  type LatLngTuple,
} from "leaflet";

import type {
  FeatureCollection,
} from "geojson";

import type {
  Parcel,
  ParcelMapFeatureCollection,
} from "../api/parcels";

import "leaflet/dist/leaflet.css";


interface ParcelMapProps {

  data:
    ParcelMapFeatureCollection;

  editingParcel?:
    Parcel | null;

  onSaveGeometry?: (
    coordinates:
      number[][][]
  ) => Promise<void>;

  onCancelEdit?: () => void;
}


/* ===================================================== */
/* BASE MAP VIEWS                                        */
/* ===================================================== */

type ParcelMapView =
  | "MAP"
  | "TERRAIN"
  | "SATELLITE";


interface ParcelBaseLayer {
  label: string;
  url: string;
  attribution: string;
  maxZoom: number;
}


const PARCEL_BASE_LAYERS:
Record<
  ParcelMapView,
  ParcelBaseLayer
> = {

  MAP: {
    label:
      "Mapa",

    url:
      "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",

    attribution:
      "&copy; OpenStreetMap contributors",

    maxZoom:
      19,
  },


  TERRAIN: {
    label:
      "Terreno",

    url:
      "https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png",

    attribution:
      "Map data &copy; OpenStreetMap contributors · Map style &copy; OpenTopoMap",

    maxZoom:
      17,
  },


  SATELLITE: {
    label:
      "Satélite",

    url:
      "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",

    attribution:
      "Tiles &copy; Esri",
      
    maxZoom:
      19,
  },
};

/* ===================================================== */
/* AUTOMATIC BOUNDS                                      */
/* ===================================================== */

function MapBounds({
  data,
  editing,
}: {
  data:
    ParcelMapFeatureCollection;

  editing: boolean;
}) {

  const map =
    useMap();


  useEffect(
    () => {

      if (
        editing ||
        data.features.length === 0
      ) {
        return;
      }


      const geoJsonData =
        data as FeatureCollection;


      const layer =
        L.geoJSON(
          geoJsonData
        );


      const bounds =
        layer.getBounds();


      if (
        bounds.isValid()
      ) {

        map.fitBounds(
          bounds,
          {
            padding: [
              35,
              35,
            ],

            maxZoom: 18,
          }
        );
      }

    },
    [
      data,
      editing,
      map,
    ]
  );


  return null;
}


/* ===================================================== */
/* CLICK DRAWING                                         */
/* ===================================================== */

function MapDrawingController({
  enabled,
  onPoint,
}: {
  enabled: boolean;

  onPoint:
    (
      point:
        LatLngTuple
    ) => void;
}) {

  useMapEvents({

    click(
      event
    ) {

      if (!enabled) {
        return;
      }


      onPoint([
        event.latlng.lat,
        event.latlng.lng,
      ]);
    },
  });


  return null;
}


/* ===================================================== */
/* LIVE POLYGON AREA                                     */
/* ===================================================== */

const EARTH_RADIUS_METERS =
  6_378_137;


/**
 * Geodesic approximation for a polygon expressed
 * as Leaflet [latitude, longitude] coordinates.
 *
 * This value is only a live preview.
 *
 * The authoritative area is recalculated by
 * PostGIS when the geometry is persisted.
 */
function calculatePolygonAreaM2(
  points: LatLngTuple[]
): number {

  if (
    points.length <
    3
  ) {
    return 0;
  }


  let total = 0;


  for (
    let index = 0;
    index < points.length;
    index += 1
  ) {

    const current =
      points[index];


    const next =
      points[
        (
          index + 1
        )
        %
        points.length
      ];


    const latitude1 =
      current[0]
      *
      Math.PI
      /
      180;


    const latitude2 =
      next[0]
      *
      Math.PI
      /
      180;


    const longitude1 =
      current[1]
      *
      Math.PI
      /
      180;


    const longitude2 =
      next[1]
      *
      Math.PI
      /
      180;


    let longitudeDelta =
      longitude2
      -
      longitude1;


    if (
      longitudeDelta >
      Math.PI
    ) {

      longitudeDelta -=
        2
        *
        Math.PI;
    }


    if (
      longitudeDelta <
      -Math.PI
    ) {

      longitudeDelta +=
        2
        *
        Math.PI;
    }


    total +=
      longitudeDelta
      *
      (
        2
        +
        Math.sin(
          latitude1
        )
        +
        Math.sin(
          latitude2
        )
      );
  }


  return Math.abs(
    total
    *
    EARTH_RADIUS_METERS
    *
    EARTH_RADIUS_METERS
    /
    2
  );
}


function formatAreaM2(
  value: number
): string {

  return new Intl
    .NumberFormat(
      "es-PE",
      {
        maximumFractionDigits:
          value >= 1000
            ? 0
            : 2,
      }
    )
    .format(
      value
    );
}


/* ===================================================== */
/* MAP                                                   */
/* ===================================================== */

export function ParcelMap({
  data,
  editingParcel = null,
  onSaveGeometry,
  onCancelEdit,
}: ParcelMapProps) {

  const navigate =
    useNavigate();

  const [
    mapView,
    setMapView,
  ] = useState<ParcelMapView>(
    "MAP"
  );


  const activeBaseLayer =
    PARCEL_BASE_LAYERS[
      mapView
    ];

  const [
    draftPoints,
    setDraftPoints,
  ] = useState<
    LatLngTuple[]
  >([]);


  const [
    saving,
    setSaving,
  ] = useState(
    false
  );


  const [
    drawError,
    setDrawError,
  ] = useState("");


  const editing =
    editingParcel !== null;

  const draftAreaM2 =
    useMemo(
      () =>
        calculatePolygonAreaM2(
          draftPoints
        ),
      [
        draftPoints,
      ]
    );


  const draftAreaHa =
    draftAreaM2
    /
    10_000;

  const geoJsonData =
    data as FeatureCollection;


  useEffect(
    () => {

      setDraftPoints(
        []
      );

      setDrawError(
        ""
      );

    },
    [
      editingParcel?.id,
    ]
  );


  const addPoint = (
    point:
      LatLngTuple
  ) => {

    setDraftPoints(
      (
        current
      ) => [
        ...current,
        point,
      ]
    );

    setDrawError(
      ""
    );
  };


  const undoPoint = () => {

    setDraftPoints(
      (
        current
      ) =>
        current.slice(
          0,
          -1
        )
    );
  };


  const clearPoints = () => {

    setDraftPoints(
      []
    );

    setDrawError(
      ""
    );
  };


  const savePolygon =
    async () => {

      if (
        draftPoints.length <
        3
      ) {

        setDrawError(
          "Marca al menos tres vértices."
        );

        return;
      }


      if (
        !onSaveGeometry
      ) {
        return;
      }


      /*
       * Leaflet:
       * [latitude, longitude]
       *
       * GeoJSON:
       * [longitude, latitude]
       */

      const ring =
        draftPoints.map(
          (
            point
          ) => [
            point[1],
            point[0],
          ]
        );


      ring.push(
        [
          draftPoints[0][1],
          draftPoints[0][0],
        ]
      );


      try {

        setSaving(
          true
        );

        setDrawError(
          ""
        );


        await onSaveGeometry(
          [
            ring,
          ]
        );


        setDraftPoints(
          []
        );


      } catch {

        setDrawError(
          "No se pudo guardar la geometría."
        );


      } finally {

        setSaving(
          false
        );
      }
    };


  return (

    <div className="parcel-map-container">

      <div
        className={
          editing
            ? "parcel-map-view-switcher editing"
            : "parcel-map-view-switcher"
        }
        role="group"
        aria-label="Cambiar vista del mapa"
      >

        <button
          type="button"
          className={
            mapView === "MAP"
              ? "active"
              : ""
          }
          onClick={() =>
            setMapView(
              "MAP"
            )
          }
          title="Vista de mapa"
        >

          <MapIcon
            size={15}
          />

          <span>
            Mapa
          </span>

        </button>


        <button
          type="button"
          className={
            mapView === "TERRAIN"
              ? "active"
              : ""
          }
          onClick={() =>
            setMapView(
              "TERRAIN"
            )
          }
          title="Vista de terreno"
        >

          <Mountain
            size={15}
          />

          <span>
            Terreno
          </span>

        </button>


        <button
          type="button"
          className={
            mapView === "SATELLITE"
              ? "active"
              : ""
          }
          onClick={() =>
            setMapView(
              "SATELLITE"
            )
          }
          title="Vista satelital"
        >

          <Satellite
            size={15}
          />

          <span>
            Satélite
          </span>

        </button>

      </div>

      {editing && (

        <div className="parcel-map-editor">

          <div className="parcel-map-editor-info">

            <strong>
              Delimitando parcela
            </strong>

            <span>
              {editingParcel.name}
            </span>


            <div className="parcel-map-live-area">

              {draftPoints.length >= 3 ? (

                <>

                  <b>
                    {draftAreaHa.toFixed(4)} ha
                  </b>

                  <small>
                    {formatAreaM2(
                      draftAreaM2
                    )} m² · estimación en tiempo real
                  </small>

                </>

              ) : (

                <>

                  <b>
                    Área pendiente
                  </b>

                  <small>
                    Marca al menos tres vértices
                  </small>

                </>

              )}

            </div>

          </div>


          <div className="parcel-map-editor-actions">

            <button
              type="button"
              onClick={
                undoPoint
              }
              disabled={
                draftPoints.length ===
                0
              }
              title="Deshacer último punto"
            >

              <Undo2
                size={15}
              />

            </button>


            <button
              type="button"
              onClick={
                clearPoints
              }
              disabled={
                draftPoints.length ===
                0
              }
              title="Limpiar dibujo"
            >

              <Trash2
                size={15}
              />

            </button>


            <button
              type="button"
              onClick={() => {

                clearPoints();

                onCancelEdit?.();

              }}
              title="Cancelar"
            >

              <RotateCcw
                size={15}
              />

            </button>


            <button
              type="button"
              className="save"
              onClick={() =>
                void savePolygon()
              }
              disabled={
                saving ||
                draftPoints.length <
                  3
              }
            >

              <Check
                size={15}
              />

              {saving
                ? "Guardando..."
                : "Guardar"}

            </button>

          </div>


          {drawError && (

            <span className="parcel-map-draw-error">
              {drawError}
            </span>

          )}

        </div>

      )}


      <MapContainer
        center={[
          -8.11,
          -79.03,
        ]}
        zoom={13}
        className="parcel-real-map"
        scrollWheelZoom
      >

        <TileLayer
          key={
            mapView
          }
          attribution={
            activeBaseLayer
              .attribution
          }
          url={
            activeBaseLayer
              .url
          }
          maxZoom={
            activeBaseLayer
              .maxZoom
          }
        />

        <GeoJSON
          key={
            JSON.stringify(
              data.features.map(
                (feature) => ({
                  id:
                    feature
                      .properties
                      .parcel_id,

                  coordinates:
                    feature
                      .geometry
                      .coordinates,
                })
              )
            )
          }
          data={
            geoJsonData
          }
          style={() => ({
            weight: 2,
            opacity: 1,
            fillOpacity: 0.32,
          })}
          onEachFeature={(
            feature,
            layer
          ) => {

            const properties =
              feature.properties as
                | {
                    parcel_id?: string;
                    name?: string;
                    crop_type?: string | null;
                    area_ha?: number | null;
                  }
                | undefined;


            if (!properties) {
              return;
            }


            const name =
              properties.name ??
              "Parcela";


            const area =
              typeof properties.area_ha ===
              "number"
                ? `${properties.area_ha.toFixed(4)} ha`
                : "Área pendiente de delimitación";


            layer.bindTooltip(
              `
                <div class="parcel-map-popup">

                  <strong>
                    ${name}
                  </strong>

                  <span>
                    ${area}
                  </span>

                  <small>
                    ${
                      editing
                        ? "Modo edición activo"
                        : "Clic para abrir el gemelo digital"
                    }
                  </small>

                </div>
              `,
              {
                sticky: true,
              }
            );


            layer.on(
              "click",
              () => {

                if (
                  editing
                ) {
                  return;
                }


                if (
                  properties
                    .parcel_id
                ) {

                  navigate(
                    `/parcels/${properties.parcel_id}`
                  );
                }
              }
            );
          }}
        />


        {editing &&
          draftPoints.length >
            0 && (

          <>

            {draftPoints.map(
              (
                point,
                index
              ) => (

                <CircleMarker
                  key={
                    `${point[0]}-${point[1]}-${index}`
                  }
                  center={
                    point
                  }
                  radius={5}
                />

              )
            )}


            {draftPoints.length >=
              2 && (

              <Polygon
                positions={
                  draftPoints
                }
                pathOptions={{
                  weight: 2,
                  fillOpacity:
                    0.2,
                }}
              />

            )}

          </>

        )}


        <MapDrawingController
          enabled={
            editing
          }
          onPoint={
            addPoint
          }
        />


        <MapBounds
          data={
            data
          }
          editing={
            editing
          }
        />

      </MapContainer>

    </div>
  );
}