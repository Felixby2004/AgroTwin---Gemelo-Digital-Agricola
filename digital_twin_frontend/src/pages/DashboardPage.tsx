import {
  useEffect,
  useMemo,
  useState,
} from "react";

import {
  ArrowRight,
  BrainCircuit,
  CircleAlert,
  Droplets,
  Leaf,
  MapPinned,
  ShieldCheck,
  Sprout,
  Activity,
  Satellite,
} from "lucide-react";

import {
  Link,
} from "react-router-dom";

import {
  getParcels,
  type Parcel,
} from "../api/parcels";

import {
  getParcelState,
  type ParcelState,
} from "../api/twin";

import {
  useLanguage,
} from "../i18n/LanguageContext";

import {
  getCropLabel,
} from "../config/cropCatalog";


interface ParcelOverview {
  parcel: Parcel;
  state: ParcelState | null;
  error: boolean;
}


function getTrustedNumber(
  state: ParcelState | null,
  variable: string
): number | null {

  const item =
    state
      ?.trusted_state
      ?.find(
        (entry) =>
          entry.variable === variable
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

    const numericValue =
      Object.values(
        item.value
      ).find(
        (value) =>
          typeof value ===
          "number"
      );


    if (
      typeof numericValue ===
      "number"
    ) {
      return numericValue;
    }

  }


  return null;
}


function getRiskClass(
  level?: string
) {

  switch (
    level?.toUpperCase()
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


function getRiskLabelKey(
  level?: string
) {

  switch (
    level?.toUpperCase()
  ) {

    case "LOW":
      return "parcels.riskStable";

    case "MEDIUM":
      return "parcels.riskAttention";

    case "HIGH":
      return "parcels.riskHigh";

    case "BLOCKED":
      return "parcels.riskBlocked";

    default:
      return "parcels.riskUnknown";
  }
}


export function DashboardPage() {

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
    loading,
    setLoading,
  ] = useState(true);


  const [
    error,
    setError,
  ] = useState("");


  useEffect(() => {

    const loadDashboard =
      async () => {

        try {

          setLoading(true);
          setError("");


          const parcelList =
            await getParcels();


          const stateResults =
            await Promise.allSettled(
              parcelList.map(
                (parcel) =>
                  getParcelState(
                    parcel.id
                  )
              )
            );


          const overview:
            ParcelOverview[] =
            parcelList.map(
              (
                parcel,
                index
              ) => {

                const result =
                  stateResults[
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
                    error: false,
                  };

                }


                return {
                  parcel,
                  state: null,
                  error: true,
                };

              }
            );


          setParcels(
            overview
          );

        } catch {

          setError(
            t("dashboard.loadError")
          );

        } finally {

          setLoading(false);

        }

      };


    void loadDashboard();

  }, []);


  const statistics =
    useMemo(
      () => {

        let stable = 0;
        let attention = 0;
        let highRisk = 0;
        let blocked = 0;
        let recommendations = 0;


        parcels.forEach(
          ({ state }) => {

            const risk =
              state
                ?.risk
                ?.level
                ?.toUpperCase();


            if (
              risk === "LOW"
            ) {
              stable += 1;
            }


            if (
              risk === "MEDIUM"
            ) {
              attention += 1;
            }


            if (
              risk === "HIGH"
            ) {
              highRisk += 1;
            }


            if (
              risk === "BLOCKED"
            ) {
              blocked += 1;
            }


            if (
              state
                ?.recommendation
                ?.allowed &&
              typeof state
                .recommendation
                .irrigation_mm ===
                "number"
            ) {
              recommendations += 1;
            }

          }
        );


        return {
          total:
            parcels.length,

          stable,

          attention,

          highRisk,

          blocked,

          recommendations,
        };

      },
      [parcels]
    );


  const recentRecommendations =
    useMemo(
      () =>
        parcels.filter(
          ({ state }) =>
            state
              ?.recommendation
              ?.allowed &&
            typeof state
              .recommendation
              .irrigation_mm ===
              "number"
        ),
      [parcels]
    );


  if (loading) {

    return (
      <div className="dashboard-loading">
        {t("dashboard.loading")}
      </div>
    );

  }


  return (
    <div>

      {/* ============================================= */}
      {/* PAGE HEADER                                   */}
      {/* ============================================= */}

      <section className="page-header">

        <div>

          <h1>
            {t("dashboard.title")}
          </h1>

          <p>
            {t("dashboard.subtitle")}
          </p>

        </div>


        <Link
          to="/parcels"
          className="dashboard-map-button"
        >

          <MapPinned size={17} />

          {t("dashboard.viewMap")}

        </Link>

      </section>


      {error && (

        <div className="error">
          {error}
        </div>

      )}


      {/* ============================================= */}
      {/* GLOBAL METRICS                                */}
      {/* ============================================= */}

      <section className="dashboard-global-metrics">

        <article className="dashboard-global-card">

          <div className="dashboard-global-icon green">
            <MapPinned size={21} />
          </div>

          <div>

            <span>
              {t("dashboard.parcels")}
            </span>

            <strong>
              {statistics.total}
            </strong>

            <small>
              {t("dashboard.registered")}
            </small>

          </div>

        </article>


        <article className="dashboard-global-card">

          <div className="dashboard-global-icon emerald">
            <ShieldCheck size={21} />
          </div>

          <div>

            <span>
              {t("dashboard.stableState")}
            </span>

            <strong>
              {statistics.stable}
            </strong>

            <small>
              {t("dashboard.lowRisk")}
            </small>

          </div>

        </article>


        <article className="dashboard-global-card">

          <div className="dashboard-global-icon orange">
            <CircleAlert size={21} />
          </div>

          <div>

            <span>
              {t("dashboard.needAttention")}
            </span>

            <strong>
              {statistics.attention +
                statistics.highRisk +
                statistics.blocked}
            </strong>

            <small>
              {t("dashboard.attentionRiskBlock")}
            </small>

          </div>

        </article>


        <article className="dashboard-global-card">

          <div className="dashboard-global-icon purple">
            <BrainCircuit size={21} />
          </div>

          <div>

            <span>
              {t("dashboard.aiRecommendations")}
            </span>

            <strong>
              {statistics.recommendations}
            </strong>

            <small>
              {t("dashboard.availableNow")}
            </small>

          </div>

        </article>

      </section>


      {/* ============================================= */}
      {/* PARCELS OVERVIEW                              */}
      {/* ============================================= */}

      <section className="panel dashboard-parcels-panel">

        <div className="panel-header">

          <div className="panel-header-title">

            <div className="panel-icon">
              <Sprout size={20} />
            </div>

            <div>

              <h2>
                {t("dashboard.parcelStatus")}
              </h2>

              <p>
                {t("dashboard.summaryTwins")}
              </p>

            </div>

          </div>


          <Link
            to="/parcels"
            className="panel-link"
          >

            {t("dashboard.viewAll")}

            <ArrowRight size={15} />

          </Link>

        </div>


        <div className="parcel-overview-grid">

          {parcels
            .slice(0, 4)
            .map(
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


              const risk =
                state
                  ?.risk
                  ?.level;


              const recommendation =
                state
                  ?.recommendation;


              return (

                <Link
                  key={parcel.id}
                  to={`/parcels/${parcel.id}`}
                  className="parcel-overview-card"
                >

                  <div className="parcel-overview-top">

                    <div className="parcel-overview-icon">
                      <Leaf size={21} />
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
                        ? t("dashboard.noAccess")
                        : t(
                            getRiskLabelKey(
                              risk
                            )
                          )}
                    </span>

                  </div>


                  <div className="parcel-overview-name">

                    <h3>
                      {parcel.name}
                    </h3>

                    <span>
                      {getCropLabel(
                        parcel.crop_type,
                        language
                      )}
                    </span>

                  </div>


                  <div className="parcel-overview-data">

                    <div>

                      <Satellite
                        size={15}
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
                        size={15}
                      />

                      <span>
                        {t("dashboard.moisture")}
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
                        size={15}
                      />

                      <span>
                        {t("dashboard.irrigation")}
                      </span>

                      <strong>
                        {recommendation
                          ?.allowed
                          ? `${recommendation
                              .irrigation_mm} mm`
                          : "—"}
                      </strong>

                    </div>

                  </div>


                  <div className="parcel-overview-footer">

                    <span>
                      {state
                        ?.quality_gate_status ||
                        t("dashboard.noStatus")}
                    </span>

                    <span className="parcel-detail-link">

                      {t("dashboard.viewDetail")}

                      <ArrowRight
                        size={14}
                      />

                    </span>

                  </div>

                </Link>

              );

            }
          )}

        </div>

      </section>


      {/* ============================================= */}
      {/* LOWER DASHBOARD                               */}
      {/* ============================================= */}

      <section className="dashboard-lower-grid">

        {/* =========================================== */}
        {/* RECOMMENDATIONS                            */}
        {/* =========================================== */}

        <article className="panel">

          <div className="panel-header">

            <div className="panel-header-title">

              <div className="panel-icon purple-icon">
                <BrainCircuit size={20} />
              </div>

              <div>

                <h2>
                  {t("dashboard.recentRecommendations")}
                </h2>

                <p>
                  {t("dashboard.decisionsByParcel")}
                </p>

              </div>

            </div>

          </div>


          <div className="dashboard-recommendation-list">

            {recentRecommendations.length ===
              0 && (

              <div className="dashboard-empty">

                {t("dashboard.noRecommendations")}

              </div>

            )}


            {recentRecommendations.map(
              ({
                parcel,
                state,
              }) => (

                <Link
                  key={parcel.id}
                  to={`/parcels/${parcel.id}`}
                  className="dashboard-recommendation-row"
                >

                  <div className="recommendation-row-icon">
                    <Droplets size={17} />
                  </div>


                  <div className="recommendation-row-content">

                    <strong>
                      {parcel.name}
                    </strong>

                    <span>
                      {t("dashboard.irrigationRecommendation")}
                    </span>

                  </div>


                  <div className="recommendation-row-value">

                    <strong>
                      {state
                        ?.recommendation
                        ?.irrigation_mm ??
                        "—"} mm
                    </strong>

                    <span>
                      {t("dashboard.score")}{" "}
                      {state
                        ?.recommendation
                        ?.score
                        ?.toFixed(
                          3
                        ) ||
                        "—"}
                    </span>

                  </div>


                  <ArrowRight
                    size={15}
                  />

                </Link>

              )
            )}

          </div>

        </article>


        {/* =========================================== */}
        {/* SYSTEM STATUS                              */}
        {/* =========================================== */}

        <article className="panel">

          <div className="panel-header">

            <div className="panel-header-title">

              <div className="panel-icon blue-icon">
                <Activity size={20} />
              </div>

              <div>

                <h2>
                  {t("dashboard.operationalStatus")}
                </h2>

                <p>
                  {t("dashboard.globalMonitoring")}
                </p>

              </div>

            </div>

          </div>


          <div className="dashboard-operational-list">

            <div className="operational-row">

              <span className="operational-dot stable" />

              <div>

                <strong>
                  {t("dashboard.stableParcels")}
                </strong>

                <span>
                  {t("dashboard.noRelevantRisk")}
                </span>

              </div>

              <strong>
                {statistics.stable}
              </strong>

            </div>


            <div className="operational-row">

              <span className="operational-dot attention" />

              <div>

                <strong>
                  Requieren atención
                </strong>

                <span>
                  {t("dashboard.mediumRisk")}
                </span>

              </div>

              <strong>
                {statistics.attention}
              </strong>

            </div>


            <div className="operational-row">

              <span className="operational-dot high" />

              <div>

                <strong>
                  {t("dashboard.highRisk")}
                </strong>

                <span>
                  {t("dashboard.priorityReview")}
                </span>

              </div>

              <strong>
                {statistics.highRisk}
              </strong>

            </div>


            <div className="operational-row">

              <span className="operational-dot blocked" />

              <div>

                <strong>
                  {t("dashboard.blocked")}
                </strong>

                <span>
                  {t("dashboard.noAutonomousRecommendation")}
                </span>

              </div>

              <strong>
                {statistics.blocked}
              </strong>

            </div>

          </div>

        </article>

      </section>

    </div>
  );
}