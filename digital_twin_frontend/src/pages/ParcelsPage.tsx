import {
  useEffect,
  useMemo,
  useState,
} from "react";

import {
  ArrowRight,
  BrainCircuit,
  Droplets,
  Leaf,
  MapPinned,
  Search,
  Satellite,
  ShieldCheck,
  TriangleAlert,
  Plus,
  Pencil,
} from "lucide-react";

import {
  Link,
} from "react-router-dom";

import {
  createParcel,
  getParcelMap,
  getParcels,
  updateParcel,
  updateParcelGeometry,
  type Parcel,
  type ParcelCreateInput,
  type ParcelUpdateInput,
  type ParcelMapFeatureCollection,
} from "../api/parcels";

import {
  getParcelState,
  type ParcelState,
} from "../api/twin";

import {
  ParcelMap,
} from "../components/ParcelMap";

import {
  ParcelForm,
} from "../components/parcels/ParcelForm";

import {
  useLanguage,
} from "../i18n/LanguageContext";

import {
  getCropLabel,
  getCropSupportLabel,
  getCropCatalogItem,
} from "../config/cropCatalog";


interface ParcelOverview {

  parcel: Parcel;

  state: ParcelState | null;

  error: boolean;
}


/* ===================================================== */
/* TRUSTED STATE HELPERS                                 */
/* ===================================================== */

function getTrustedNumber(
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
    item.value &&
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


/* ===================================================== */
/* RISK HELPERS                                          */
/* ===================================================== */

function getRiskClass(
  risk?: string
) {

  switch (
    risk?.toUpperCase()
  ) {

    case "LOW":
      return "low";

    case "MEDIUM":
      return "medium";

    case "HIGH":
      return "high";

    case "BLOCKED":
      return "blocked";

    default:
      return "unknown";
  }
}


/* ===================================================== */
/* PAGE                                                  */
/* ===================================================== */

export function ParcelsPage() {

  const {
    t,
    language,
  } = useLanguage();


  const [
    parcels,
    setParcels,
  ] = useState<
    ParcelOverview[]
  >([]);


  const [
    mapData,
    setMapData,
  ] = useState<
    ParcelMapFeatureCollection
  >({
    type:
      "FeatureCollection",

    features: [],
  });


  const [
    search,
    setSearch,
  ] = useState("");


  const [
    riskFilter,
    setRiskFilter,
  ] = useState(
    "ALL"
  );


  const [
    loading,
    setLoading,
  ] = useState(
    true
  );


  const [
    error,
    setError,
  ] = useState("");


  /*
   * IMPORTANT:
   * Hooks must stay inside ParcelsPage().
   */

  const [
    editingParcelId,
    setEditingParcelId,
  ] = useState("");


  const [
    mapMessage,
    setMapMessage,
  ] = useState("");


  const [
    formOpen,
    setFormOpen,
  ] = useState(
    false
  );


  const [
    formParcel,
    setFormParcel,
  ] = useState<
    Parcel | null
  >(null);


  const [
    formSubmitting,
    setFormSubmitting,
  ] = useState(
    false
  );


  const [
    formMessage,
    setFormMessage,
  ] = useState("");


  /* =================================================== */
  /* LOAD DATA                                           */
  /* =================================================== */

  useEffect(
    () => {

      const loadParcels =
        async () => {

          try {

            setLoading(
              true
            );

            setError("");


            const [
              parcelData,
              parcelMapData,
            ] =
              await Promise.all([
                getParcels(),
                getParcelMap(),
              ]);


            setMapData(
              parcelMapData
            );


            const states =
              await Promise
                .allSettled(
                  parcelData.map(
                    (parcel) =>
                      getParcelState(
                        parcel.id
                      )
                  )
                );


            const overview =
              parcelData.map(
                (
                  parcel,
                  index
                ):
                  ParcelOverview => {

                  const result =
                    states[
                      index
                    ];


                  if (
                    result.status ===
                    "fulfilled"
                  ) {

                    return {
                      parcel,
                      state:
                        result.value,
                      error:
                        false,
                    };
                  }


                  return {
                    parcel,
                    state:
                      null,
                    error:
                      true,
                  };
                }
              );


            setParcels(
              overview
            );

          } catch {

            setError(
              "No se pudieron cargar las parcelas."
            );

          } finally {

            setLoading(
              false
            );
          }
        };


      void loadParcels();

    },
    []
  );


  /* =================================================== */
  /* FILTERS                                             */
  /* =================================================== */

  const filteredParcels =
    useMemo(
      () => {

        const normalizedSearch =
          search
            .trim()
            .toLowerCase();


        return parcels.filter(
          ({
            parcel,
            state,
          }) => {

            const matchesText =
              normalizedSearch ===
                "" ||
              parcel.name
                .toLowerCase()
                .includes(
                  normalizedSearch
                ) ||
              (
                parcel.crop_type ||
                ""
              )
                .toLowerCase()
                .includes(
                  normalizedSearch
                ) ||
              getCropLabel(
                parcel.crop_type
              )
                .toLowerCase()
                .includes(
                  normalizedSearch
                );


            const risk =
              state
                ?.risk
                ?.level
                ?.toUpperCase() ||
              "UNKNOWN";


            const matchesRisk =
              riskFilter ===
                "ALL" ||
              risk ===
                riskFilter;


            return (
              matchesText &&
              matchesRisk
            );
          }
        );
      },
      [
        parcels,
        search,
        riskFilter,
      ]
    );


  /* =================================================== */
  /* SUMMARY                                             */
  /* =================================================== */

  const summary =
    useMemo(
      () => {

        return {

          total:
            parcels.length,


          stable:
            parcels.filter(
              ({ state }) =>
                state
                  ?.risk
                  ?.level ===
                "LOW"
            ).length,


          attention:
            parcels.filter(
              ({ state }) =>
                [
                  "MEDIUM",
                  "HIGH",
                  "BLOCKED",
                ].includes(
                  state
                    ?.risk
                    ?.level ||
                    ""
                )
            ).length,
        };
      },
      [
        parcels,
      ]
    );


  /* =================================================== */
  /* CURRENT PARCEL BEING EDITED                         */
  /* =================================================== */

  const editingParcel =
    useMemo(
      () => {

        return (
          parcels.find(
            ({
              parcel,
            }) =>
              parcel.id ===
              editingParcelId
          )
          ?.parcel ??
          null
        );
      },
      [
        parcels,
        editingParcelId,
      ]
    );


  /* =================================================== */
  /* MAP HELPERS                                         */
  /* =================================================== */

  const refreshMap =
    async () => {

      const updatedMap =
        await getParcelMap();


      setMapData(
        updatedMap
      );
    };


  const saveGeometry =
    async (
      coordinates:
        number[][][]
    ) => {

      if (!editingParcel) {
        return;
      }


      const result =
        await updateParcelGeometry(
          editingParcel.id,
          {
            type:
              "Polygon",

            coordinates,
          }
        );


      /*
      * Refresh both sources:
      *
      * 1. Parcel list:
      *    updates the official area_ha.
      *
      * 2. GeoJSON map:
      *    updates geometry + tooltip area.
      */

      await reloadParcels();

      await refreshMap();


      if (
        result.area_ha !== null
      ) {

        const squareMeters =
          result.area_ha
          *
          10_000;


        setMapMessage(
          `Parcela "${editingParcel.name}" delimitada correctamente. `
          +
          `Área oficial: ${result.area_ha.toFixed(4)} ha `
          +
          `(${squareMeters.toLocaleString(
            "es-PE",
            {
              maximumFractionDigits:
                2,
            }
          )} m²).`
        );

      } else {

        setMapMessage(
          `Geometría de "${editingParcel.name}" guardada correctamente.`
        );
      }


      setEditingParcelId(
        ""
      );
    };

  const reloadParcels =
    async () => {

      const parcelData =
        await getParcels();


      const states =
        await Promise
          .allSettled(
            parcelData.map(
              (parcel) =>
                getParcelState(
                  parcel.id
                )
            )
          );


      const overview =
        parcelData.map(
          (
            parcel,
            index
          ):
            ParcelOverview => {

            const result =
              states[
                index
              ];


            return result.status === "fulfilled"
              ? {
                  parcel,
                  state:
                    result.value,
                  error:
                    false,
                }
              : {
                  parcel,
                  state:
                    null,
                  error:
                    true,
                };
          }
        );


      setParcels(
        overview
      );
    };


  const openCreateForm =
    () => {

      setFormParcel(
        null
      );

      setFormMessage("");

      setFormOpen(
        true
      );
    };


  const openEditForm =
    (
      parcel:
        Parcel
    ) => {

      setFormParcel(
        parcel
      );

      setFormMessage("");

      setFormOpen(
        true
      );
    };


  const closeParcelForm =
    () => {

      setFormOpen(
        false
      );

      setFormParcel(
        null
      );
    };


  const saveParcel =
    async (
      payload:
        ParcelCreateInput
        | ParcelUpdateInput
    ) => {

      setFormSubmitting(
        true
      );

      setFormMessage("");


      try {

        if (
          formParcel
        ) {

          await updateParcel(
            formParcel.id,
            payload
          );


          setFormMessage(
            "Parcela actualizada correctamente."
          );

        } else {

          const createdParcel =
            await createParcel(
              payload
            );


          setEditingParcelId(
            createdParcel.id
          );


          setMapMessage(
            `Parcela "${createdParcel.name}" creada. `
            +
            "Ahora delimita su área haciendo clic sobre el mapa."
          );


          setFormMessage(
            "Parcela creada correctamente."
          );
        }


        await reloadParcels();

        await refreshMap();

        closeParcelForm();

      } catch {

        setFormMessage(
          "No se pudo guardar la parcela."
        );

      } finally {

        setFormSubmitting(
          false
        );
      }
    };


  /* =================================================== */
  /* LOADING                                             */
  /* =================================================== */

  if (
    loading
  ) {

    return (
      <div className="dashboard-loading">

        Cargando parcelas...

      </div>
    );
  }


  /* =================================================== */
  /* RENDER                                              */
  /* =================================================== */

  return (

    <div>

      {/* ============================================= */}
      {/* HEADER                                        */}
      {/* ============================================= */}

      <section className="page-header">

        <div>

          <h1>
            {t("parcels.titlePrefix")} {t("parcels.titleHighlight")}
          </h1>


          <p>

            {t("parcels.subtitle")}

          </p>

        </div>


        <div className="parcels-header-actions">

          <button
            type="button"
            className="button-primary"
            onClick={
              openCreateForm
            }
          >
            <Plus size={16} />
            {t("parcels.new")}
          </button>


          <div className="parcels-header-summary">

          <div>

            <MapPinned
              size={16}
            />

            <span>
              {t("parcels.total")}
            </span>

            <strong>
              {summary.total}
            </strong>

          </div>


          <div>

            <ShieldCheck
              size={16}
            />

            <span>
              {t("parcels.stable")}
            </span>

            <strong>
              {summary.stable}
            </strong>

          </div>


          <div>

            <TriangleAlert
              size={16}
            />

            <span>
              {t("parcels.attention")}
            </span>

            <strong>
              {summary.attention}
            </strong>

          </div>

        </div>

        </div>

      </section>


      {formOpen && (

        <section className="panel parcel-form-panel">

          <ParcelForm
            parcel={
              formParcel
            }
            submitting={
              formSubmitting
            }
            onCancel={
              closeParcelForm
            }
            onSubmit={
              saveParcel
            }
          />

        </section>

      )}


      {formMessage && (

        <div className="parcel-map-success">
          {formMessage}
        </div>

      )}


      {error && (

        <div className="error">

          {error}

        </div>

      )}


      {/* ============================================= */}
      {/* MAP                                           */}
      {/* ============================================= */}

      <section className="parcels-territorial-panel panel">

        {/* ------------------------------------------- */}
        {/* PANEL HEADER                                */}
        {/* ------------------------------------------- */}

        <div className="panel-header">

          <div className="panel-header-title">

            <div className="panel-icon">

              <MapPinned
                size={20}
              />

            </div>


            <div>

              <h2>
                {t("parcels.territorialView")}
              </h2>

              <p>
                {t("parcels.geometryRegistered")}
              </p>

            </div>

          </div>


          <span className="parcels-result-count">

            {
              mapData
                .features
                .length
            }

            {" "}

            geometría

            {
              mapData
                .features
                .length ===
              1
                ? ""
                : "s"
            }

          </span>

        </div>


        {/* ------------------------------------------- */}
        {/* MAP MANAGEMENT                              */}
        {/* ------------------------------------------- */}

        <div className="parcel-map-management">

          <div>

            <strong>
              {t("parcels.locationTitle")}
            </strong>


            <span>

              {t("parcels.locationHelp")}

            </span>

          </div>


          <select
            className="page-select"
            value={
              editingParcelId
            }
            onChange={(
              event
            ) => {

              setEditingParcelId(
                event
                  .target
                  .value
              );


              setMapMessage(
                ""
              );
            }}
          >

            <option value="">
              {t("parcels.select")}
            </option>


            {parcels.map(
              ({
                parcel,
              }) => (

                <option
                  key={
                    parcel.id
                  }
                  value={
                    parcel.id
                  }
                >

                  {parcel.name}

                </option>

              )
            )}

          </select>

        </div>


        {mapMessage && (

          <div className="parcel-map-success">

            {mapMessage}

          </div>

        )}


        {/* ------------------------------------------- */}
        {/* MAP                                         */}
        {/* ------------------------------------------- */}

        <ParcelMap
          data={
            mapData
          }
          editingParcel={
            editingParcel
          }
          onSaveGeometry={
            saveGeometry
          }
          onCancelEdit={() => {

            setEditingParcelId(
              ""
            );

            setMapMessage(
              ""
            );
          }}
        />

      </section>


      {/* ============================================= */}
      {/* ALL PARCELS                                   */}
      {/* ============================================= */}

      <section className="all-parcels-section">

        <div className="all-parcels-title">

          <div>

            <h2>
              {t("parcels.all")}
            </h2>


            <p>

              {t("parcels.openHelp")}

            </p>

          </div>

        </div>

        {/* ============================================= */}
        {/* FILTERS                                       */}
        {/* ============================================= */}

        <section className="parcels-toolbar panel">

          <div className="parcel-search">

            <Search
              size={17}
            />


            <input
              type="text"
              value={
                search
              }
              placeholder={
                t("parcels.searchPlaceholder")
              }
              onChange={(
                event
              ) =>
                setSearch(
                  event
                    .target
                    .value
                )
              }
            />

          </div>


          <select
            className="page-select parcels-filter-select"
            value={
              riskFilter
            }
            onChange={(
              event
            ) =>
              setRiskFilter(
                event
                  .target
                  .value
              )
            }
          >

            <option value="ALL">
              {t("parcels.allStatuses")}
            </option>

            <option value="LOW">
              Estables
            </option>

            <option value="MEDIUM">
              Atención
            </option>

            <option value="HIGH">
              {t("parcels.highRisk")}
            </option>

            <option value="BLOCKED">
              {t("parcels.blocked")}
            </option>

          </select>

        </section>


        {filteredParcels
          .length ===
        0 ? (

          <div className="panel dashboard-empty">

            {t("parcels.noResults")}

          </div>

        ) : (

          <div className="all-parcels-grid">

            {filteredParcels.map(
              ({
                parcel,
                state,
                error:
                  parcelError,
              }) => {

                const ndvi =
                  getTrustedNumber(
                    state,
                    "ndvi"
                  );


                const moisture =
                  getTrustedNumber(
                    state,
                    "soil_water_state"
                  );


                const temperature =
                  getTrustedNumber(
                    state,
                    "air_temperature"
                  );


                const risk =
                  state
                    ?.risk
                    ?.level;


                const recommendation =
                  state
                    ?.recommendation;


                return (

                  <article
                    key={
                      parcel.id
                    }
                    className="full-parcel-card"
                  >

                    <div className="full-parcel-card-header">

                      <div className="full-parcel-icon">

                        <Leaf
                          size={22}
                        />

                      </div>


                      <span
                        className={
                          `parcel-risk-badge ${
                            getRiskClass(
                              risk
                            )
                          }`
                        }
                      >

                        {parcelError
                          ? t("parcels.noAccess")
                          : risk?.toUpperCase() === "LOW"
                            ? t("parcels.riskStable")
                            : risk?.toUpperCase() === "MEDIUM"
                              ? t("parcels.riskAttention")
                              : risk?.toUpperCase() === "HIGH"
                                ? t("parcels.riskHigh")
                                : risk?.toUpperCase() === "BLOCKED"
                                  ? t("parcels.riskBlocked")
                                  : t("parcels.riskUnknown")}

                      </span>

                    </div>


                    <div className="full-parcel-title">

                      <h3>
                        {parcel.name}
                      </h3>


                      <span>

                        {getCropLabel(
                          parcel.crop_type,
                          language
                        )}

                        {parcel.area_ha !== null
                          ? ` · ${parcel.area_ha.toFixed(4)} ha`
                          : " · Área pendiente"}

                      </span>

                      <span
                        className={
                          getCropCatalogItem(
                            parcel.crop_type
                          )?.supportStatus === "SUPPORTED"
                            ? "crop-support-badge validated"
                            : "crop-support-badge experimental"
                        }
                      >
                        {getCropSupportLabel(
                          parcel.crop_type
                        )}
                      </span>

                    </div>


                    <div className="full-parcel-metrics">

                      <div>

                        <Satellite
                          size={16}
                        />

                        <span>
                          NDVI
                        </span>

                        <strong>

                          {ndvi !== null
                            ? ndvi.toFixed(
                                3
                              )
                            : "—"}

                        </strong>

                      </div>


                      <div>

                        <Droplets
                          size={16}
                        />

                        <span>
                          {t("parcels.soilMoisture")}
                        </span>

                        <strong>

                          {moisture !== null
                            ? moisture.toFixed(
                                3
                              )
                            : "—"}

                        </strong>

                      </div>


                      <div>

                        <BrainCircuit
                          size={16}
                        />

                        <span>
                          {t("parcels.irrigation")}
                        </span>

                        <strong>

                          {recommendation
                            ?.allowed
                            ? `${recommendation.irrigation_mm} mm`
                            : "—"}

                        </strong>

                      </div>


                      <div>

                        <Leaf
                          size={16}
                        />

                        <span>
                          {t("parcels.temperature")}
                        </span>

                        <strong>

                          {temperature !== null
                            ? `${temperature.toFixed(1)}°`
                            : "—"}

                        </strong>

                      </div>

                    </div>


                    <div className="full-parcel-status">

                      <div>

                        <span>
                          {t("parcels.validData")}
                        </span>

                        <strong>

                          {state
                            ?.quality_gate_status ||
                            "—"}

                        </strong>

                      </div>


                      <div>

                        <span>
                          {t("parcels.evidence")}
                        </span>

                        <strong>

                          {state
                            ?.evidence
                            ?.total ??
                            "—"}

                        </strong>

                      </div>


                      <div>

                        <span>
                          {t("parcels.conflicts")}
                        </span>

                        <strong>

                          {state
                            ?.conflicts_count ??
                            "—"}

                        </strong>

                      </div>

                    </div>


                    <div className="parcel-card-actions">

                      <button
                        type="button"
                        className="button-secondary parcel-edit-button"
                        onClick={() =>
                          openEditForm(
                            parcel
                          )
                        }
                      >
                        <Pencil size={14} />
                        {t("parcels.edit")}
                      </button>


                      <Link
                      to={
                        `/parcels/${parcel.id}`
                      }
                      className="open-twin-button"
                    >

                      {t("parcels.openTwin")}

                      <ArrowRight
                        size={15}
                      />

                      </Link>

                    </div>

                  </article>

                );
              }
            )}

          </div>

        )}

      </section>

    </div>
  );
}