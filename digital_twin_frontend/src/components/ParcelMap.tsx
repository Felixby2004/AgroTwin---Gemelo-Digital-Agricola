import {
  useEffect,
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
  RotateCcw,
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

      {editing && (

        <div className="parcel-map-editor">

          <div>

            <strong>
              Editando ubicación
            </strong>

            <span>
              {editingParcel.name}
            </span>

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
          attribution={
            "&copy; OpenStreetMap contributors"
          }
          url={
            "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
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


            const crop =
              properties.crop_type ??
              "Cultivo no definido";


            const area =
              typeof properties
                .area_ha ===
              "number"
                ? `${properties.area_ha} ha`
                : "Área no definida";


            layer.bindTooltip(
              `
                <div class="parcel-map-popup">

                  <strong>
                    ${name}
                  </strong>

                  <span>
                    ${crop}
                  </span>

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