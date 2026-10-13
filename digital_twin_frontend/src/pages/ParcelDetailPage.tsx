import {
  useEffect,
  useRef,
  useState,
} from "react";

import {
  Link,
  useParams,
} from "react-router-dom";

import {
  isAxiosError,
} from "axios";

import {
  Activity,
  ArrowLeft,
  BrainCircuit,
  Database,
  Droplets,
  GitBranch,
  Leaf,
  Maximize2,
  Minimize2,
  RefreshCw,
  Satellite,
  ShieldCheck,
  Thermometer,
  TriangleAlert,
} from "lucide-react";

import {
  getParcel,
  getParcelGeometry,
  type Parcel,
  type ParcelGeometryResponse,
} from "../api/parcels";

import {
  getParcelState,
  type ParcelState,
  type TrustedStateItem,
} from "../api/twin";

import {
  getParcelSoilMoistureForecast,
  getParcelSoilMoistureHistory,
  type SoilMoistureForecast,
  type SoilMoistureHistory,
} from "../api/ml";

import {
  getParcelSensors,
  type Sensor,
} from "../api/sensors";

import {
  getMyParcelPermissions,
  hasParcelPermission,
  type ParcelPermissions,
} from "../api/permissions";

import {
  useLanguage,
} from "../i18n/LanguageContext";

import {
  TwinScene,
} from "../components/twin3d/TwinScene";

import {
  SoilMoistureForecastCard,
} from "../components/ml/SoilMoistureForecastCard";

import {
  SoilMoistureHistoryChart,
} from "../components/ml/SoilMoistureHistoryChart";

import {
  DecisionArchitecturePanel,
} from "../components/decision/DecisionArchitecturePanel";

import {
  DecisionTracePanel,
} from "../components/decision/DecisionTracePanel";

import {
  TemporalTwinControls,
} from "../components/twin3d/TemporalTwinControls";

import {
  FarmerDecisionPanel,
} from "../components/decision/FarmerDecisionPanel";

import {
  FarmerKnowledgeForm,
} from "../components/knowledge/FarmerKnowledgeForm";

import {
  HelpTooltip,
} from "../components/help/HelpTooltip";

import {
  ParcelSensorsPanel,
} from "../components/sensors/ParcelSensorsPanel";

import {
  ParcelMembersPanel,
} from "../components/members/ParcelMembersPanel";

import "./ParcelDetailTabs.css";


type Translate = (
  es: string,
  en: string
) => string;


function findVariable(
  state: ParcelState | null,
  variableName: string
): TrustedStateItem | undefined {

  return state
    ?.trusted_state
    ?.find(
      (item) =>
        item.variable ===
        variableName
    );
}


function extractValue(
  item:
    | TrustedStateItem
    | undefined
) {

  if (!item) {
    return "—";
  }

  const value =
    item.value;

  if (
    typeof value ===
    "number"
  ) {

    return value.toFixed(
      3
    );
  }

  if (
    value &&
    typeof value ===
      "object"
  ) {

    const objectValue =
      value as Record<
        string,
        unknown
      >;

    if (
      typeof objectValue
        .soil_moisture ===
      "number"
    ) {

      return objectValue
        .soil_moisture
        .toFixed(3);
    }

    const numberValue =
      Object.values(
        objectValue
      ).find(
        (entry) =>
          typeof entry ===
          "number"
      );

    if (
      typeof numberValue ===
      "number"
    ) {

      return numberValue
        .toFixed(3);
    }
  }

  return "—";
}


function extractNumericValue(
  item:
    | TrustedStateItem
    | undefined
): number | null {

  if (!item) {
    return null;
  }

  const value =
    item.value;

  if (
    typeof value ===
    "number"
  ) {
    return value;
  }

  if (
    value &&
    typeof value ===
      "object"
  ) {

    const objectValue =
      value as Record<
        string,
        unknown
      >;

    if (
      typeof objectValue
        .soil_moisture ===
      "number"
    ) {

      return objectValue
        .soil_moisture;
    }

    const numberValue =
      Object.values(
        objectValue
      ).find(
        (entry) =>
          typeof entry ===
          "number"
      );

    if (
      typeof numberValue ===
      "number"
    ) {
      return numberValue;
    }
  }

  return null;
}


function interpolateTemporalMoisture(
  current:
    | number
    | null,
  forecast:
    | SoilMoistureForecast
    | null,
  hour: number
): number | null {

  if (
    typeof current !==
    "number"
  ) {
    return null;
  }

  if (
    !forecast ||
    hour <= 0
  ) {
    return current;
  }

  const ratio =
    Math.max(
      0,
      Math.min(
        1,
        hour / 24
      )
    );

  return (
    current +
    (
      forecast
        .predicted_soil_moisture_24h
      - current
    ) *
    ratio
  );
}


function formatConfidence(
  item:
    | TrustedStateItem
    | undefined
) {

  if (!item) {
    return "—";
  }

  return `${(
    item.confidence_score *
    100
  ).toFixed(1)}%`;
}


function formatCropName(
  cropType:
    | string
    | null
    | undefined,
  tr: Translate
) {

  if (!cropType) {
    return tr(
      "Cultivo",
      "Crop"
    );
  }

  const normalized =
    cropType
      .trim()
      .toLowerCase();

  const labels:
    Record<string, string> = {

      maize:
        tr(
          "Maíz",
          "Maize"
        ),

      corn:
        tr(
          "Maíz",
          "Maize"
        ),

      potato:
        tr(
          "Papa",
          "Potato"
        ),

      rice:
        tr(
          "Arroz",
          "Rice"
        ),

      wheat:
        tr(
          "Trigo",
          "Wheat"
        ),

      onion:
        tr(
          "Cebolla",
          "Onion"
        ),

      tomato:
        tr(
          "Tomate",
          "Tomato"
        ),

      avocado:
        tr(
          "Palta",
          "Avocado"
        ),

      coffee:
        tr(
          "Café",
          "Coffee"
        ),

      sugarcane:
        tr(
          "Caña de azúcar",
          "Sugarcane"
        ),

      quinoa:
        tr(
          "Quinua",
          "Quinoa"
        ),
  };

  return (
    labels[
      normalized
    ] ??
    cropType
  );
}


function formatRecommendationStatus(
  status:
    | string
    | null
    | undefined,
  tr: Translate
) {

  switch (status) {

    case "RECOMMENDED":

      return tr(
        "Recomendado",
        "Recommended"
      );

    case "PROVISIONAL":

      return tr(
        "Provisional",
        "Provisional"
      );

    case "BLOCKED":

      return tr(
        "Bloqueado",
        "Blocked"
      );

    default:

      return status || "—";
  }
}


function formatRiskLevel(
  level:
    | string
    | null
    | undefined,
  tr: Translate
) {

  switch (level) {

    case "LOW":

      return tr(
        "Bajo",
        "Low"
      );

    case "MEDIUM":

      return tr(
        "Medio",
        "Medium"
      );

    case "HIGH":

      return tr(
        "Alto",
        "High"
      );

    default:

      return level || "—";
  }
}


function formatParcelRole(
  permissions:
    ParcelPermissions
    | null,
  tr: Translate
) {

  if (!permissions) {
    return "—";
  }

  if (
    permissions.system_role ===
    "ADMIN"
  ) {

    return tr(
      "ADMIN · acceso global",
      "ADMIN · global access"
    );
  }

  switch (
    permissions.parcel_role
  ) {

    case "OWNER":

      return tr(
        "Propietario",
        "Owner"
      );

    case "FARMER":

      return tr(
        "Agricultor",
        "Farmer"
      );

    case "AGRONOMIST":

      return tr(
        "Agrónomo",
        "Agronomist"
      );

    case "VIEWER":

      return tr(
        "Observador",
        "Viewer"
      );

    default:

      return tr(
        "Sin rol en la parcela",
        "No parcel role"
      );
  }
}


function getMLUnavailableMessage(
  error: unknown,
  tr: Translate
): string {

  if (
    isAxiosError(
      error
    )
  ) {

    const detail =
      error
        .response
        ?.data
        ?.detail;

    if (
      detail &&
      typeof detail ===
        "object" &&
      "code" in detail &&
      detail.code ===
        "INSUFFICIENT_ML_HISTORY"
    ) {

      return tr(
        (
          "Historial insuficiente: " +
          "se requieren al menos 24 horas " +
          "de evidencia de humedad."
        ),
        (
          "Insufficient history: " +
          "at least 24 hours of soil-moisture " +
          "evidence are required."
        )
      );
    }

    if (
      typeof detail ===
      "string"
    ) {
      return detail;
    }
  }

  return tr(
    (
      "El módulo Random Forest complementario " +
      "no está disponible para esta parcela."
    ),
    (
      "The complementary Random Forest module " +
      "is not available for this parcel."
    )
  );
}


export function ParcelDetailPage() {

  const {
    tr,
  } = useLanguage();

  const {
    parcelId,
  } = useParams();


  const twinFullscreenRef =
    useRef<HTMLElement | null>(
      null
    );


  const [
    parcel,
    setParcel,
  ] = useState<
    Parcel | null
  >(null);


  const [
    state,
    setState,
  ] = useState<
    ParcelState | null
  >(null);


  const [
    mlForecast,
    setMlForecast,
  ] = useState<
    SoilMoistureForecast | null
  >(null);


  const [
    mlUnavailable,
    setMlUnavailable,
  ] = useState(
    false
  );


  const [
    mlUnavailableMessage,
    setMlUnavailableMessage,
  ] = useState(
    ""
  );


  const [
    mlHistory,
    setMlHistory,
  ] = useState<
    SoilMoistureHistory | null
  >(null);


  const [
    permissions,
    setPermissions,
  ] = useState<
    ParcelPermissions | null
  >(null);


  const [
    sensors,
    setSensors,
  ] = useState<
    Sensor[]
  >([]);


  const [
    parcelGeometry,
    setParcelGeometry,
  ] = useState<
    ParcelGeometryResponse | null
  >(null);


  const [
    sensorsUnavailable,
    setSensorsUnavailable,
  ] = useState(
    false
  );


  const [
    isTwinFullscreen,
    setIsTwinFullscreen,
  ] = useState(
    false
  );


  const [
    temporalHour,
    setTemporalHour,
  ] = useState(
    0
  );


  const [
    activeTab,
    setActiveTab,
  ] = useState<
    "details"
    | "trace"
    | "permissions"
  >(
    "details"
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
  ] = useState(
    ""
  );


  const loadData =
    async () => {

      if (!parcelId) {
        return;
      }

      setLoading(true);

      setError("");

      setMlUnavailable(
        false
      );

      setMlUnavailableMessage(
        ""
      );

      setMlHistory(
        null
      );

      setSensorsUnavailable(
        false
      );

      setParcelGeometry(
        null
      );

      setTemporalHour(
        0
      );


      try {

        const [
          parcelData,
          stateData,
          permissionsData,
        ] =
          await Promise.all([

            getParcel(
              parcelId
            ),

            getParcelState(
              parcelId
            ),

            getMyParcelPermissions(
              parcelId
            ),
          ]);


        setParcel(
          parcelData
        );

        setState(
          stateData
        );

        setPermissions(
          permissionsData
        );


        const optionalResults =
          await Promise
            .allSettled([

              getParcelSoilMoistureForecast(
                parcelId
              ),

              getParcelSoilMoistureHistory(
                parcelId,
                72
              ),

              getParcelSensors(
                parcelId
              ),

              getParcelGeometry(
                parcelId
              ),
            ]);


        const forecastResult =
          optionalResults[0];

        const historyResult =
          optionalResults[1];

        const sensorResult =
          optionalResults[2];

        const geometryResult =
          optionalResults[3];


        if (
          forecastResult.status ===
          "fulfilled"
        ) {

          setMlForecast(
            forecastResult.value
          );

          setMlUnavailable(
            false
          );

        } else {

          setMlForecast(
            null
          );

          setMlUnavailable(
            true
          );

          setMlUnavailableMessage(
            getMLUnavailableMessage(
              forecastResult.reason,
              tr
            )
          );
        }


        if (
          historyResult.status ===
          "fulfilled"
        ) {

          setMlHistory(
            historyResult.value
          );

        } else {

          setMlHistory(
            null
          );
        }


        if (
          sensorResult.status ===
          "fulfilled"
        ) {

          setSensors(
            sensorResult.value
          );

          setSensorsUnavailable(
            false
          );

        } else {

          setSensors([]);

          setSensorsUnavailable(
            true
          );
        }


        if (
          geometryResult.status ===
          "fulfilled"
        ) {

          setParcelGeometry(
            geometryResult.value
          );

        } else {

          setParcelGeometry(
            null
          );
        }

      } catch {

        setError(
          tr(
            "No se pudo cargar el estado del gemelo digital.",
            "Could not load the digital twin state."
          )
        );

      } finally {

        setLoading(
          false
        );
      }
    };


  useEffect(
    () => {

      void loadData();

    },
    [
      parcelId,
    ]
  );


  useEffect(
    () => {

      const handleFullscreenChange =
        () => {

          setIsTwinFullscreen(
            document
              .fullscreenElement ===
              twinFullscreenRef.current
          );
        };


      document.addEventListener(
        "fullscreenchange",
        handleFullscreenChange
      );


      return () => {

        document.removeEventListener(
          "fullscreenchange",
          handleFullscreenChange
        );
      };

    },
    []
  );


  const toggleTwinFullscreen =
    async () => {

      const element =
        twinFullscreenRef.current;

      if (!element) {
        return;
      }

      try {

        if (
          document.fullscreenElement ===
          element
        ) {

          await document
            .exitFullscreen();

          return;
        }

        if (
          document.fullscreenElement
        ) {

          await document
            .exitFullscreen();
        }

        await element
          .requestFullscreen();

      } catch {

        setIsTwinFullscreen(
          false
        );
      }
    };


  if (loading) {

    return (
      <div className="panel empty-state">

        {tr(
          "Cargando gemelo digital...",
          "Loading digital twin..."
        )}

      </div>
    );
  }


  if (
    error ||
    !parcel
  ) {

    return (
      <div className="error">

        {error ||
          tr(
            "Parcela no encontrada.",
            "Parcel not found."
          )}

      </div>
    );
  }


  const soilWater =
    findVariable(
      state,
      "soil_water_state"
    );


  const currentSoilMoisture =
    extractNumericValue(
      soilWater
    );


  const temporalSoilMoisture =
    interpolateTemporalMoisture(
      currentSoilMoisture,
      mlForecast,
      temporalHour
    );


  const temperature =
    findVariable(
      state,
      "air_temperature"
    );


  const ndvi =
    findVariable(
      state,
      "ndvi"
    );


  const ndmi =
    findVariable(
      state,
      "ndmi"
    );


  const rainfall =
    findVariable(
      state,
      "rainfall"
    );


  const recommendation =
    state?.recommendation;


  const risk =
    state?.risk;


  const canManageKnowledge =
    hasParcelPermission(
      permissions,
      "MANAGE_KNOWLEDGE"
    );


  const canManageSensors =
    hasParcelPermission(
      permissions,
      "EDIT"
    );


  const canRespondRecommendation =
    hasParcelPermission(
      permissions,
      "RESPOND_RECOMMENDATION"
    );


  const canManageMembers =
    hasParcelPermission(
      permissions,
      "MANAGE_MEMBERS"
    );


  return (

    <div>

      {/* HEADER */}

      <section className="page-header">

        <div>

          <Link
            to="/parcels"
            className="back-link"
          >

            <ArrowLeft
              size={16}
            />

            {tr(
              "Parcelas",
              "Parcels"
            )}

          </Link>


          <h1>
            {parcel.name}
          </h1>


          <p>

            {formatCropName(
              parcel.crop_type,
              tr
            )}

            {" · "}

            {parcel.area_ha ||
              "—"} ha

            {" · "}

            {tr(
              "Gemelo digital operativo",
              "Operational digital twin"
            )}

          </p>


          <div className="parcel-role-inline">

            <ShieldCheck
              size={15}
            />

            <span>
              {tr(
                "Acceso:",
                "Access:"
              )}
            </span>

            <strong>
              {formatParcelRole(
                permissions,
                tr
              )}
            </strong>

          </div>

        </div>


        <button
          className="button-secondary"
          onClick={() =>
            void loadData()
          }
        >

          <RefreshCw
            size={17}
          />

          {tr(
            "Actualizar",
            "Refresh"
          )}

        </button>

      </section>


      {/* TABS */}

      <nav
        className="parcel-detail-tabs"
        aria-label={tr(
          "Secciones de la parcela",
          "Parcel sections"
        )}
      >

        <button
          type="button"
          className={
            activeTab ===
              "details"
              ? "parcel-detail-tab active"
              : "parcel-detail-tab"
          }
          onClick={() =>
            setActiveTab(
              "details"
            )
          }
        >

          <Activity
            size={17}
          />

          <span>
            {tr(
              "Detalles de parcela",
              "Parcel details"
            )}
          </span>

        </button>


        <button
          type="button"
          className={
            activeTab ===
              "trace"
              ? "parcel-detail-tab active"
              : "parcel-detail-tab"
          }
          onClick={() =>
            setActiveTab(
              "trace"
            )
          }
        >

          <GitBranch
            size={17}
          />

          <span>
            {tr(
              "Trazabilidad",
              "Traceability"
            )}
          </span>

        </button>


        {canManageMembers && (

          <button
            type="button"
            className={
              activeTab ===
                "permissions"
                ? "parcel-detail-tab active"
                : "parcel-detail-tab"
            }
            onClick={() =>
              setActiveTab(
                "permissions"
              )
            }
          >

            <ShieldCheck
              size={17}
            />

            <span>
              {tr(
                "Permisos",
                "Permissions"
              )}
            </span>

          </button>
        )}

      </nav>


      {activeTab === "details" ? (

        <>

          {/* METRICS */}

          <section className="state-metrics-grid">

            <article className="state-metric">

              <div className="state-metric-icon green">
                <Droplets
                  size={21}
                />
              </div>

              <div>

                <span>
                  {tr(
                    "Humedad del suelo",
                    "Soil moisture"
                  )}
                </span>

                <strong>

                  {extractValue(
                    soilWater
                  )}

                  {" "}

                  <small>
                    {soilWater
                      ?.unit ||
                      ""}
                  </small>

                </strong>

                <em>

                  {tr(
                    "Confianza",
                    "Confidence"
                  )}{" "}

                  {formatConfidence(
                    soilWater
                  )}

                </em>

              </div>

            </article>


            <article className="state-metric">

              <div className="state-metric-icon orange">
                <Thermometer
                  size={21}
                />
              </div>

              <div>

                <span>
                  {tr(
                    "Temperatura",
                    "Temperature"
                  )}
                </span>

                <strong>

                  {extractValue(
                    temperature
                  )}

                  {" "}

                  <small>
                    {temperature
                      ?.unit ||
                      ""}
                  </small>

                </strong>

                <em>

                  {tr(
                    "Confianza",
                    "Confidence"
                  )}{" "}

                  {formatConfidence(
                    temperature
                  )}

                </em>

              </div>

            </article>


            <article className="state-metric">

              <div className="state-metric-icon purple">
                <Satellite
                  size={21}
                />
              </div>

              <div>

                <span>

                  NDVI

                  <HelpTooltip
                    term="NDVI"
                    text={tr(
                      "Índice de vegetación que ayuda a representar el vigor y la actividad de la cobertura vegetal.",
                      "Vegetation index used to represent vegetation vigor and activity."
                    )}
                  />

                </span>

                <strong>
                  {extractValue(
                    ndvi
                  )}
                </strong>

                <em>

                  {tr(
                    "Confianza",
                    "Confidence"
                  )}{" "}

                  {formatConfidence(
                    ndvi
                  )}

                </em>

              </div>

            </article>


            <article className="state-metric">

              <div className="state-metric-icon cyan">
                <Satellite
                  size={21}
                />
              </div>

              <div>

                <span>

                  NDMI

                  <HelpTooltip
                    term="NDMI"
                    text={tr(
                      "Índice relacionado con el contenido de humedad de la vegetación observado mediante imágenes satelitales.",
                      "Index related to vegetation moisture content observed through satellite imagery."
                    )}
                  />

                </span>

                <strong>
                  {extractValue(
                    ndmi
                  )}
                </strong>

                <em>

                  {tr(
                    "Confianza",
                    "Confidence"
                  )}{" "}

                  {formatConfidence(
                    ndmi
                  )}

                </em>

              </div>

            </article>

          </section>


          {/* 3D TWIN */}

          <section
            ref={
              twinFullscreenRef
            }
            className="panel twin-visualization-panel"
          >

            <div className="panel-header">

              <div className="panel-header-title">

                <div className="panel-icon">
                  <Leaf
                    size={20}
                  />
                </div>

                <div>

                  <h2>
                    {tr(
                      "Gemelo Digital de la Parcela",
                      "Parcel Digital Twin"
                    )}
                  </h2>

                  <p>
                    TwinState · PostGIS · IoT · Copernicus
                  </p>

                </div>

              </div>


              <div className="twin-panel-actions">

                <span className="status-badge active">

                  {state
                    ?.quality_gate_status ||
                    "—"}

                </span>


                <button
                  type="button"
                  className="twin-fullscreen-button"
                  aria-pressed={
                    isTwinFullscreen
                  }
                  title={
                    isTwinFullscreen
                      ? tr(
                          "Salir de pantalla completa",
                          "Exit full screen"
                        )
                      : tr(
                          "Abrir gemelo en pantalla completa",
                          "Open twin in full screen"
                        )
                  }
                  onClick={() =>
                    void toggleTwinFullscreen()
                  }
                >

                  {isTwinFullscreen ? (
                    <Minimize2
                      size={17}
                    />
                  ) : (
                    <Maximize2
                      size={17}
                    />
                  )}

                  <span>

                    {isTwinFullscreen
                      ? tr(
                          "Salir",
                          "Exit"
                        )
                      : tr(
                          "Pantalla completa",
                          "Full screen"
                        )}

                  </span>

                </button>

              </div>

            </div>


            <TemporalTwinControls
              currentMoisture={
                currentSoilMoisture
              }
              forecast={
                mlForecast
              }
              selectedHour={
                temporalHour
              }
              onSelectedHourChange={
                setTemporalHour
              }
            />


            <div className="real-3d-stage">

              <TwinScene
                state={
                  state
                }
                sensors={
                  sensors
                }
                mode="detailed"
                soilMoistureOverride={
                  temporalSoilMoisture
                }
                geometry={
                  parcelGeometry
                    ?.geometry ??
                  null
                }
                cropType={
                  parcel.crop_type
                }
                areaHa={
                  parcel.area_ha
                }
              />

            </div>

          </section>


          <ParcelSensorsPanel
            sensors={
              sensors
            }
            parcelId={
              parcel.id
            }
            parcelName={
              parcel.name
            }
            canManageSensors={
              canManageSensors
            }
            unavailable={
              sensorsUnavailable
            }
          />


          <DecisionArchitecturePanel
            mlAvailable={
              mlForecast !== null
            }
            recommendationAvailable={
              Boolean(
                state
                  ?.recommendation
              )
            }
          />


          {/* COMPLEMENTARY ML */}

          {mlForecast ? (

            <SoilMoistureForecastCard
              forecast={
                mlForecast
              }
              history={
                mlHistory
              }
            />

          ) : mlUnavailable ? (

            <section className="panel ml-forecast-panel">

              <div className="panel-header">

                <div className="panel-header-title">

                  <div className="panel-icon purple-icon">
                    <BrainCircuit
                      size={20}
                    />
                  </div>

                  <div>

                    <h2>
                      {tr(
                        "Módulo predictivo complementario",
                        "Complementary predictive module"
                      )}
                    </h2>

                    <p>
                      {tr(
                        "Random Forest · sin autoridad decisional",
                        "Random Forest · no decision authority"
                      )}
                    </p>

                  </div>

                </div>

              </div>


              <div className="ml-unavailable">

                <TriangleAlert
                  size={25}
                />

                <strong>
                  {tr(
                    "Pronóstico complementario no disponible",
                    "Complementary forecast unavailable"
                  )}
                </strong>

                <span>

                  {mlUnavailableMessage ||
                    tr(
                      "No fue posible construir el pronóstico complementario.",
                      "The complementary forecast could not be generated."
                    )}

                </span>

                <small>
                  {tr(
                    "Esto no afecta el TwinState, el motor de inferencia, la evaluación de escenarios ni la recomendación.",
                    "This does not affect the TwinState, the inference engine, scenario evaluation or the recommendation."
                  )}
                </small>

              </div>


              {mlHistory &&
                mlHistory.count > 0 && (

                  <SoilMoistureHistoryChart
                    history={
                      mlHistory
                    }
                    forecast={
                      null
                    }
                    compact
                  />
                )}

            </section>

          ) : null}


          {/* DECISION */}

          <section className="decision-grid">

            <article className="panel">

              <div className="panel-header">

                <div className="panel-header-title">

                  <div className="panel-icon purple-icon">
                    <BrainCircuit
                      size={20}
                    />
                  </div>

                  <div>

                    <h2>

                      {tr(
                        "Recomendación de riego",
                        "Irrigation recommendation"
                      )}

                      <HelpTooltip
                        term={tr(
                          "Recomendación de riego",
                          "Irrigation recommendation"
                        )}
                        text={tr(
                          "Cantidad de agua sugerida por el motor de decisión según el estado actual, restricciones, preferencias y confianza del gemelo.",
                          "Amount of water suggested by the decision engine according to the current state, constraints, preferences and twin confidence."
                        )}
                      />

                    </h2>

                    <p>
                      {tr(
                        "Generada con IA explicable",
                        "Generated with explainable AI"
                      )}
                    </p>

                  </div>

                </div>

              </div>


              <div className="recommendation-real">

                <span className="recommendation-label">
                  {tr(
                    "Riego recomendado",
                    "Recommended irrigation"
                  )}
                </span>


                <div className="recommendation-real-value">

                  {recommendation
                    ?.irrigation_mm ??
                    "—"}

                  <small>
                    mm
                  </small>

                </div>


                <div className="recommendation-meta">

                  <span>

                    {tr(
                      "Puntaje",
                      "Score"
                    )}

                    <HelpTooltip
                      term={tr(
                        "Puntaje",
                        "Score"
                      )}
                      text={tr(
                        "Valor agregado usado para comparar alternativas de riego según criterios agronómicos, preferencias y confianza.",
                        "Aggregate value used to compare irrigation alternatives according to agronomic criteria, preferences and confidence."
                      )}
                    />

                    <strong>

                      {typeof recommendation
                        ?.score ===
                        "number"
                        ? recommendation
                            .score
                            .toFixed(3)
                        : "—"}

                    </strong>

                  </span>


                  <span>

                    {tr(
                      "Estado",
                      "Status"
                    )}

                    <strong>

                      {formatRecommendationStatus(
                        recommendation
                          ?.status,
                        tr
                      )}

                    </strong>

                  </span>

                </div>


                {recommendation
                  ?.reasons && (

                  <div className="reason-list">

                    {recommendation
                      .reasons
                      .map(
                        (
                          reason,
                          index
                        ) => (

                          <div
                            key={
                              index
                            }
                          >

                            <Activity
                              size={14}
                            />

                            {reason}

                          </div>
                        )
                      )}

                  </div>
                )}

              </div>

            </article>


            <article className="panel">

              <div className="panel-header">

                <div className="panel-header-title">

                  <div className="panel-icon">
                    <ShieldCheck
                      size={20}
                    />
                  </div>

                  <div>

                    <h2>

                      {tr(
                        "Confianza y evidencia",
                        "Confidence and evidence"
                      )}

                      <HelpTooltip
                        term={tr(
                          "Confianza y evidencia",
                          "Confidence and evidence"
                        )}
                        text={tr(
                          "Resume cuánta información útil existe, qué datos necesitan actualización y qué tan confiable es el estado actual.",
                          "Summarizes how much useful information is available, which data need updating and how reliable the current state is."
                        )}
                      />

                    </h2>

                    <p>
                      {tr(
                        "Calidad del estado actual",
                        "Current state quality"
                      )}
                    </p>

                  </div>

                </div>

              </div>


              <div className="trust-content">

                <div className="trust-row">

                  <Database
                    size={18}
                  />

                  <span>

                    {tr(
                      "Datos válidos",
                      "Valid data"
                    )}

                    <HelpTooltip
                      term={tr(
                        "Datos válidos",
                        "Valid data"
                      )}
                      text={tr(
                        "Cantidad de evidencias disponibles que el gemelo puede utilizar para representar el estado actual.",
                        "Number of available evidence items that the twin can use to represent the current state."
                      )}
                    />

                  </span>

                  <strong>
                    {state
                      ?.evidence
                      ?.operational ??
                      "—"}
                  </strong>

                </div>


                <div className="trust-row">

                  <TriangleAlert
                    size={18}
                  />

                  <span>

                    {tr(
                      "Datos por actualizar",
                      "Data requiring update"
                    )}

                    <HelpTooltip
                      term={tr(
                        "Datos por actualizar",
                        "Data requiring update"
                      )}
                      text={tr(
                        "Variables cuya vigencia o calidad requiere una nueva medición o actualización.",
                        "Variables whose freshness or quality requires a new measurement or update."
                      )}
                    />

                  </span>

                  <strong>
                    {state
                      ?.evidence
                      ?.update_required
                      ?.length ??
                      0}
                  </strong>

                </div>


                <div className="trust-row">

                  <Activity
                    size={18}
                  />

                  <span>

                    {tr(
                      "Inconsistencias detectadas",
                      "Detected inconsistencies"
                    )}

                    <HelpTooltip
                      term={tr(
                        "Inconsistencias",
                        "Inconsistencies"
                      )}
                      text={tr(
                        "Diferencias detectadas entre fuentes o afirmaciones que el sistema registra para su evaluación.",
                        "Differences detected between sources or statements that the system preserves for evaluation."
                      )}
                    />

                  </span>

                  <strong>
                    {state
                      ?.conflicts_count ??
                      0}
                  </strong>

                </div>


                <div className="trust-row">

                  <ShieldCheck
                    size={18}
                  />

                  <span>

                    {tr(
                      "Nivel de riesgo",
                      "Risk level"
                    )}

                    <HelpTooltip
                      term={tr(
                        "Nivel de riesgo",
                        "Risk level"
                      )}
                      text={tr(
                        "Nivel de precaución asociado a la recomendación según incertidumbre y calidad de los datos.",
                        "Precaution level associated with the recommendation according to uncertainty and data quality."
                      )}
                    />

                  </span>

                  <strong>
                    {formatRiskLevel(
                      risk
                        ?.level,
                      tr
                    )}
                  </strong>

                </div>


                <div className="trust-row">

                  <BrainCircuit
                    size={18}
                  />

                  <span>

                    {tr(
                      "Confiabilidad del estado actual",
                      "Current state reliability"
                    )}

                    <HelpTooltip
                      term={tr(
                        "Confiabilidad del estado actual",
                        "Current state reliability"
                      )}
                      text={tr(
                        "Estimación de qué tan consistente y confiable es el estado calculado por el gemelo digital.",
                        "Estimate of how consistent and reliable the state calculated by the digital twin is."
                      )}
                    />

                  </span>

                  <strong>

                    {typeof risk
                      ?.confidence ===
                      "number"
                      ? `${(
                          risk
                            .confidence *
                          100
                        ).toFixed(1)}%`
                      : "—"}

                  </strong>

                </div>


                {rainfall
                  ?.requires_update && (

                  <div className="update-warning">

                    <Droplets
                      size={17}
                    />

                    {tr(
                      "Lluvia requiere actualización",
                      "Rainfall data requires an update"
                    )}

                  </div>
                )}

              </div>

            </article>

          </section>


          {/* PARTICIPATORY HITL */}

          {parcelId && (

            <div className="participatory-stack">

              {canRespondRecommendation ? (

                <FarmerDecisionPanel
                  parcelId={
                    parcelId
                  }
                />

              ) : (

                <section className="panel permission-restricted-panel">

                  <ShieldCheck
                    size={22}
                  />

                  <div>

                    <strong>
                      {tr(
                        "Respuesta a recomendaciones no disponible",
                        "Recommendation response unavailable"
                      )}
                    </strong>

                    <span>
                      {tr(
                        "Tu rol en esta parcela no posee el permiso RESPOND_RECOMMENDATION.",
                        "Your role for this parcel does not have the RESPOND_RECOMMENDATION permission."
                      )}
                    </span>

                  </div>

                </section>
              )}


              {canManageKnowledge ? (

                <FarmerKnowledgeForm
                  parcelId={
                    parcelId
                  }
                />

              ) : (

                <section className="panel permission-restricted-panel">

                  <ShieldCheck
                    size={22}
                  />

                  <div>

                    <strong>
                      {tr(
                        "Registro de conocimiento no disponible",
                        "Knowledge registration unavailable"
                      )}
                    </strong>

                    <span>
                      {tr(
                        "Tu rol en esta parcela no posee el permiso MANAGE_KNOWLEDGE.",
                        "Your role for this parcel does not have the MANAGE_KNOWLEDGE permission."
                      )}
                    </span>

                  </div>

                </section>
              )}

            </div>
          )}

        </>

      ) : activeTab === "trace" ? (

        <>

          {parcelId && (

            <DecisionTracePanel
              parcelId={
                parcelId
              }
            />
          )}

        </>

      ) : (

        <>

          {parcelId &&
          canManageMembers ? (

            <ParcelMembersPanel
              parcelId={
                parcelId
              }
            />

          ) : (

            <section className="panel permission-restricted-panel">

              <ShieldCheck
                size={22}
              />

              <div>

                <strong>
                  {tr(
                    "Gestión de permisos no disponible",
                    "Permission management unavailable"
                  )}
                </strong>

                <span>
                  {tr(
                    "Tu rol en esta parcela no posee el permiso MANAGE_MEMBERS.",
                    "Your role for this parcel does not have the MANAGE_MEMBERS permission."
                  )}
                </span>

              </div>

            </section>
          )}

        </>
      )}

    </div>
  );
}