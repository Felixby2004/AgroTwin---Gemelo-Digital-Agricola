import {
  createContext,
  useContext,
  useMemo,
  useState,
  type ReactNode,
} from "react";


export type Language =
  | "es"
  | "en";


type TranslationDictionary =
Record<string, {
  es: string;
  en: string;
}>;


const TRANSLATIONS:
TranslationDictionary = {

  "brand.subtitle": {
    es: "CONFIANZA DIGITAL",
    en: "DIGITAL TRUST",
  },

  "sidebar.digitalTwins": {
    es: "GEMELOS DIGITALES",
    en: "DIGITAL TWINS",
  },

  "sidebar.dashboard": {
    es: "Vista General",
    en: "Overview",
  },

  "sidebar.parcels": {
    es: "Mapa de Parcelas",
    en: "Parcel Map",
  },

  "sidebar.sensors": {
    es: "Sensores",
    en: "Sensors",
  },

  "sidebar.glossary": {
    es: "Glosario",
    en: "Glossary",
  },

  "sidebar.dataSovereignty": {
    es: "SOBERANÍA DE DATOS",
    en: "DATA SOVEREIGNTY",
  },

  "sidebar.governance": {
    es: "Gobernanza",
    en: "Governance",
  },

  "sidebar.reportsSection": {
    es: "REPORTES",
    en: "REPORTS",
  },

  "sidebar.reports": {
    es: "Reportes",
    en: "Reports",
  },

  "sidebar.logout": {
    es: "Cerrar sesión",
    en: "Sign out",
  },

  "topbar.title": {
    es: "Plataforma de Gemelos Digitales",
    en: "Digital Twin Platform",
  },

  "topbar.subtitle": {
    es: "Agricultura de precisión con IA explicable & soberanía de datos",
    en: "Precision agriculture with explainable AI & data sovereignty",
  },

  "topbar.expand": {
    es: "Expandir menú",
    en: "Expand menu",
  },

  "topbar.collapse": {
    es: "Contraer menú",
    en: "Collapse menu",
  },

  "theme.dark": {
    es: "Activar modo oscuro",
    en: "Enable dark mode",
  },

  "theme.light": {
    es: "Activar modo claro",
    en: "Enable light mode",
  },

  "language.spanish": {
    es: "Español",
    en: "Spanish",
  },

  "language.english": {
    es: "Inglés",
    en: "English",
  },

  "login.platform": {
    es: "Plataforma de Gemelos Digitales - Confianza Digital",
    en: "Digital Twin Platform - Digital Trust",
  },

  "login.title": {
    es: "Inicia sesión",
    en: "Sign in",
  },

  "login.subtitle": {
    es: "Accede a tu plataforma de agricultura de precisión",
    en: "Access your precision agriculture platform",
  },

  "login.email": {
    es: "Correo electrónico",
    en: "Email",
  },

  "login.emailPlaceholder": {
    es: "correo@ejemplo.com",
    en: "email@example.com",
  },

  "login.password": {
    es: "Contraseña",
    en: "Password",
  },

  "login.submit": {
    es: "Iniciar sesión",
    en: "Sign in",
  },

  "login.loading": {
    es: "Ingresando...",
    en: "Signing in...",
  },

  "login.invalid": {
    es: "Correo o contraseña inválidos.",
    en: "Invalid email or password.",
  },

  "role.USER": {
    es: "Usuario",
    en: "User",
  },

  "role.ADMIN": {
    es: "Administrador",
    en: "Administrator",
  },

  "role.FARMER": {
    es: "Agricultor",
    en: "Farmer",
  },

  "role.RESEARCHER": {
    es: "Investigador",
    en: "Researcher",
  },

  "role.AGRONOMIST": {
    es: "Agrónomo",
    en: "Agronomist",
  },

  "role.EXPERT": {
    es: "Experto",
    en: "Expert",
  },

  "common.loading": {
    es: "Cargando...",
    en: "Loading...",
  },

  "common.cancel": {
    es: "Cancelar",
    en: "Cancel",
  },

  "common.save": {
    es: "Guardar",
    en: "Save",
  },

  "common.search": {
    es: "Buscar",
    en: "Search",
  },

  "parcels.titlePrefix": {
    es: "Mapa de",
    en: "Parcel",
  },

  "parcels.titleHighlight": {
    es: "Parcelas",
    en: "Map",
  },

  "parcels.subtitle": {
    es: "Explora todas las parcelas registradas y accede a su gemelo digital",
    en: "Explore all registered parcels and access their digital twin",
  },

  "parcels.total": {
    es: "Total",
    en: "Total",
  },

  "parcels.stable": {
    es: "Estables",
    en: "Stable",
  },

  "parcels.attention": {
    es: "Atención",
    en: "Attention",
  },

  "parcels.new": {
    es: "Nueva parcela",
    en: "New parcel",
  },

  "parcels.searchPlaceholder": {
    es: "Buscar por parcela o cultivo...",
    en: "Search by parcel or crop...",
  },

  "parcels.allStatuses": {
    es: "Todos los estados",
    en: "All statuses",
  },

  "parcels.highRisk": {
    es: "Riesgo alto",
    en: "High risk",
  },

  "parcels.blocked": {
    es: "Bloqueadas",
    en: "Blocked",
  },

  "parcels.territorialView": {
    es: "Vista territorial",
    en: "Territorial view",
  },

  "parcels.geometryRegistered": {
    es: "Parcelas con geometría geográfica registrada",
    en: "Parcels with registered geographic geometry",
  },

  "parcels.locationTitle": {
    es: "Ubicación de parcelas",
    en: "Parcel location",
  },

  "parcels.locationHelp": {
    es: "Selecciona una parcela y dibuja su límite real sobre el mapa.",
    en: "Select a parcel and draw its real boundary on the map.",
  },

  "parcels.select": {
    es: "Seleccionar parcela...",
    en: "Select parcel...",
  },

  "parcels.all": {
    es: "Todas las parcelas",
    en: "All parcels",
  },

  "parcels.openHelp": {
    es: "Selecciona una parcela para abrir su gemelo digital detallado",
    en: "Select a parcel to open its detailed digital twin",
  },

  "parcels.noResults": {
    es: "No se encontraron parcelas con estos filtros.",
    en: "No parcels were found with these filters.",
  },

  "parcels.cropUndefined": {
    es: "Cultivo no definido",
    en: "Crop not defined",
  },

  "parcels.soilMoisture": {
    es: "Humedad",
    en: "Moisture",
  },

  "parcels.irrigation": {
    es: "Riego",
    en: "Irrigation",
  },

  "parcels.temperature": {
    es: "Temp.",
    en: "Temp.",
  },

  "parcels.validData": {
    es: "Datos válidos",
    en: "Valid data",
  },

  "parcels.evidence": {
    es: "Evidencias",
    en: "Evidence",
  },

  "parcels.conflicts": {
    es: "Conflictos",
    en: "Conflicts",
  },

  "parcels.edit": {
    es: "Editar",
    en: "Edit",
  },

  "parcels.openTwin": {
    es: "Abrir gemelo digital",
    en: "Open digital twin",
  },

  "parcels.noAccess": {
    es: "Sin acceso",
    en: "No access",
  },

  "parcels.riskStable": {
    es: "Estable",
    en: "Stable",
  },

  "parcels.riskAttention": {
    es: "Atención",
    en: "Attention",
  },

  "parcels.riskHigh": {
    es: "Riesgo alto",
    en: "High risk",
  },

  "parcels.riskBlocked": {
    es: "Bloqueado",
    en: "Blocked",
  },

  "parcels.riskUnknown": {
    es: "Sin evaluar",
    en: "Not evaluated",
  },

  "sensors.title": {
    es: "Sensores IoT",
    en: "IoT Sensors",
  },

  "sensors.subtitle": {
    es: "Dispositivos conectados, calidad de datos y lecturas operacionales por parcela.",
    en: "Connected devices, data quality and operational readings by parcel.",
  },

  "sensors.refresh": {
    es: "Actualizar",
    en: "Refresh",
  },

  "sensors.refreshing": {
    es: "Actualizando...",
    en: "Refreshing...",
  },

  "sensors.registered": {
    es: "Sensores registrados",
    en: "Registered sensors",
  },

  "sensors.active": {
    es: "Activos",
    en: "Active",
  },

  "sensors.stale": {
    es: "Desactualizados",
    en: "Stale",
  },

  "sensors.attention": {
    es: "Requieren atención",
    en: "Need attention",
  },

  "sensors.searchPlaceholder": {
    es: "Buscar sensor, parcela o variable...",
    en: "Search sensor, parcel or variable...",
  },

  "sensors.allParcels": {
    es: "Todas las parcelas",
    en: "All parcels",
  },

  "sensors.allStatuses": {
    es: "Todos los estados",
    en: "All statuses",
  },

  "sensors.noData": {
    es: "Sin datos",
    en: "No data",
  },

  "sensors.error": {
    es: "Error",
    en: "Error",
  },

  "sensors.inactive": {
    es: "Inactivos",
    en: "Inactive",
  },

  "sensors.allTypes": {
    es: "Todos los tipos",
    en: "All types",
  },

  "sensors.devices": {
    es: "Dispositivos",
    en: "Devices",
  },

  "sensors.result": {
    es: "resultado",
    en: "result",
  },

  "sensors.results": {
    es: "resultados",
    en: "results",
  },

  "sensors.noFiltered": {
    es: "No hay sensores con estos filtros",
    en: "No sensors match these filters",
  },

  "sensors.adjustFilters": {
    es: "Ajusta los filtros o registra nuevas lecturas IoT para visualizar dispositivos.",
    en: "Adjust the filters or register new IoT readings to display devices.",
  },

  "sensors.lastReading": {
    es: "Última lectura",
    en: "Latest reading",
  },

  "sensors.parcel": {
    es: "Parcela",
    en: "Parcel",
  },

  "sensors.quality": {
    es: "Calidad",
    en: "Quality",
  },

  "sensors.lastCommunication": {
    es: "Última comunicación",
    en: "Last communication",
  },

  "sensors.viewDetail": {
    es: "Ver detalle e historial",
    en: "View details and history",
  },

  "sensorDetail.kicker": {
    es: "Detalle del dispositivo",
    en: "Device details",
  },

  "sensorDetail.type": {
    es: "Tipo",
    en: "Type",
  },

  "sensorDetail.latestQuality": {
    es: "Calidad última lectura",
    en: "Latest reading quality",
  },

  "sensorDetail.location": {
    es: "Ubicación",
    en: "Location",
  },

  "sensorDetail.notRegistered": {
    es: "No registrada",
    en: "Not registered",
  },

  "sensorDetail.variables": {
    es: "Variables configuradas",
    en: "Configured variables",
  },

  "sensorDetail.history": {
    es: "Historial reciente",
    en: "Recent history",
  },

  "sensorDetail.historyHelp": {
    es: "Últimas 30 lecturas almacenadas como evidencia de máquina.",
    en: "Last 30 readings stored as machine evidence.",
  },

  "sensorDetail.loadingHistory": {
    es: "Cargando historial...",
    en: "Loading history...",
  },

  "sensorDetail.noHistory": {
    es: "Este sensor todavía no tiene lecturas registradas.",
    en: "This sensor does not have registered readings yet.",
  },

  "sensorDetail.date": {
    es: "Fecha",
    en: "Date",
  },

  "sensorDetail.variable": {
    es: "Variable",
    en: "Variable",
  },

  "sensorDetail.reading": {
    es: "Lectura",
    en: "Reading",
  },

  "sensorDetail.status": {
    es: "Estado",
    en: "Status",
  },

  "sensorDetail.current": {
    es: "Vigente",
    en: "Current",
  },

  "sensorDetail.outdated": {
    es: "Desactualizada",
    en: "Stale",
  },

  "dashboard.loading": {
    es: "Cargando estado global...",
    en: "Loading global status...",
  },
  "dashboard.loadError": {
    es: "No se pudo cargar el estado global de las parcelas.",
    en: "Could not load the global parcel status.",
  },
  "dashboard.title": {
    es: "Vista General",
    en: "Overview",
  },
  "dashboard.subtitle": {
    es: "Supervisión global de parcelas, recomendaciones y estado operativo",
    en: "Global monitoring of parcels, recommendations and operational status",
  },
  "dashboard.viewMap": {
    es: "Ver mapa de parcelas",
    en: "View parcel map",
  },
  "dashboard.parcels": {
    es: "Parcelas",
    en: "Parcels",
  },
  "dashboard.registered": {
    es: "Registradas en el sistema",
    en: "Registered in the system",
  },
  "dashboard.stableState": {
    es: "Estado estable",
    en: "Stable status",
  },
  "dashboard.lowRisk": {
    es: "Riesgo LOW",
    en: "LOW risk",
  },
  "dashboard.needAttention": {
    es: "Requieren atención",
    en: "Need attention",
  },
  "dashboard.attentionRiskBlock": {
    es: "Atención, riesgo o bloqueo",
    en: "Attention, risk or blocking",
  },
  "dashboard.aiRecommendations": {
    es: "Recomendaciones IA",
    en: "AI recommendations",
  },
  "dashboard.availableNow": {
    es: "Disponibles actualmente",
    en: "Currently available",
  },
  "dashboard.parcelStatus": {
    es: "Estado de las parcelas",
    en: "Parcel status",
  },
  "dashboard.summaryTwins": {
    es: "Vista resumida de todos los gemelos digitales",
    en: "Summary view of all digital twins",
  },
  "dashboard.viewAll": {
    es: "Ver todas",
    en: "View all",
  },
  "dashboard.noAccess": {
    es: "Sin acceso",
    en: "No access",
  },
  "dashboard.cropUndefined": {
    es: "Cultivo no definido",
    en: "Crop not defined",
  },
  "dashboard.moisture": {
    es: "Humedad",
    en: "Moisture",
  },
  "dashboard.irrigation": {
    es: "Riego",
    en: "Irrigation",
  },
  "dashboard.noStatus": {
    es: "Sin estado",
    en: "No status",
  },
  "dashboard.viewDetail": {
    es: "Ver detalle",
    en: "View details",
  },
  "dashboard.recentRecommendations": {
    es: "Recomendaciones recientes",
    en: "Recent recommendations",
  },
  "dashboard.decisionsByParcel": {
    es: "Decisiones disponibles por parcela",
    en: "Available decisions by parcel",
  },
  "dashboard.noRecommendations": {
    es: "No existen recomendaciones disponibles.",
    en: "No recommendations are available.",
  },
  "dashboard.irrigationRecommendation": {
    es: "Recomendación de riego",
    en: "Irrigation recommendation",
  },
  "dashboard.score": {
    es: "Puntaje",
    en: "Score",
  },
  "dashboard.operationalStatus": {
    es: "Estado operativo",
    en: "Operational status",
  },
  "dashboard.globalMonitoring": {
    es: "Supervisión global",
    en: "Global monitoring",
  },
  "dashboard.stableParcels": {
    es: "Parcelas estables",
    en: "Stable parcels",
  },
  "dashboard.noRelevantRisk": {
    es: "Sin riesgo relevante",
    en: "No relevant risk",
  },
  "dashboard.mediumRisk": {
    es: "Riesgo MEDIUM",
    en: "MEDIUM risk",
  },
  "dashboard.highRisk": {
    es: "Riesgo alto",
    en: "High risk",
  },
  "dashboard.priorityReview": {
    es: "Revisión prioritaria",
    en: "Priority review",
  },
  "dashboard.blocked": {
    es: "Bloqueadas",
    en: "Blocked",
  },
  "dashboard.noAutonomousRecommendation": {
    es: "Sin recomendación autónoma",
    en: "No autonomous recommendation",
  },

  "governance.loadError": {
    es: "No se pudo cargar la gobernanza de la parcela.",
    en: "Could not load parcel governance.",
  },
  "governance.parcelsLoadError": {
    es: "No se pudieron cargar las parcelas.",
    en: "Could not load parcels.",
  },
  "governance.updateError": {
    es: "No se pudo actualizar el consentimiento.",
    en: "Could not update consent.",
  },
  "governance.title": {
    es: "Soberanía y Gobernanza",
    en: "Data Sovereignty & Governance",
  },
  "governance.subtitle": {
    es: "Consentimientos, permisos, auditoría y control de datos",
    en: "Consents, permissions, audit and data control",
  },
  "governance.activeConsents": {
    es: "Consentimientos activos",
    en: "Active consents",
  },
  "governance.revoked": {
    es: "Revocados",
    en: "Revoked",
  },
  "governance.auditEvents": {
    es: "Eventos de auditoría",
    en: "Audit events",
  },
  "governance.consents": {
    es: "Consentimientos",
    en: "Consents",
  },
  "governance.parcelFallback": {
    es: "Parcela",
    en: "Parcel",
  },
  "governance.loading": {
    es: "Cargando...",
    en: "Loading...",
  },
  "governance.noConsents": {
    es: "No existen consentimientos.",
    en: "No consents are available.",
  },
  "governance.revoke": {
    es: "Revocar",
    en: "Revoke",
  },
  "governance.activate": {
    es: "Activar",
    en: "Activate",
  },
  "governance.auditTraceability": {
    es: "Auditoría y trazabilidad",
    en: "Audit and traceability",
  },
  "governance.latestOperations": {
    es: "Últimas operaciones",
    en: "Latest operations",
  },
  "governance.allowed": {
    es: "Permitido",
    en: "Allowed",
  },
  "governance.denied": {
    es: "Bloqueado",
    en: "Blocked",
  },
  "governance.status.ACTIVE": {
    es: "ACTIVO",
    en: "ACTIVE",
  },
  "governance.status.REVOKED": {
    es: "REVOCADO",
    en: "REVOKED",
  },

  "reports.previewError": {
    es: "No se pudo generar la vista previa.",
    en: "Could not generate preview.",
  },
  "reports.pdfPreviewError": {
    es: "No se pudo generar la vista previa PDF.",
    en: "Could not generate the PDF preview.",
  },
  "reports.parcelsLoadError": {
    es: "No se pudieron cargar las parcelas.",
    en: "Could not load parcels.",
  },
  "reports.downloadBlocked": {
    es: "La descarga fue bloqueada. Verifica permisos y consentimiento de exportación.",
    en: "The download was blocked. Check permissions and export consent.",
  },
  "reports.title": {
    es: "Centro de Reportes",
    en: "Reports Center",
  },
  "reports.subtitle": {
    es: "Vista previa y exportación trazable en PDF, Word y Excel",
    en: "Preview and traceable export to PDF, Word and Excel",
  },
  "reports.pdf": {
    es: "Reporte PDF",
    en: "PDF Report",
  },
  "reports.pdfHelp": {
    es: "Informe técnico legible",
    en: "Readable technical report",
  },
  "reports.word": {
    es: "Documento Word",
    en: "Word Document",
  },
  "reports.wordHelp": {
    es: "Reporte editable",
    en: "Editable report",
  },
  "reports.excel": {
    es: "Libro Excel",
    en: "Excel Workbook",
  },
  "reports.excelHelp": {
    es: "Datos estructurados",
    en: "Structured data",
  },
  "reports.exportControl": {
    es: "Control de exportación",
    en: "Export control",
  },
  "reports.exportSubtitle": {
    es: "Soberanía de datos · permisos · trazabilidad",
    en: "Data sovereignty · permissions · traceability",
  },
  "reports.userPermission": {
    es: "Permiso de usuario",
    en: "User permission",
  },
  "reports.exportRequired": {
    es: "EXPORT_DATA requerido",
    en: "EXPORT_DATA required",
  },
  "reports.activeConsent": {
    es: "Consentimiento activo",
    en: "Active consent",
  },
  "reports.purpose": {
    es: "Purpose EXPORT + PARCEL_DATA",
    en: "Purpose EXPORT + PARCEL_DATA",
  },
  "reports.traceability": {
    es: "Trazabilidad",
    en: "Traceability",
  },
  "reports.provenancePreserved": {
    es: "Provenance preservada",
    en: "Provenance preserved",
  },
  "reports.preview": {
    es: "Vista previa",
    en: "Preview",
  },
  "reports.parcelFallback": {
    es: "Parcela",
    en: "Parcel",
  },
  "reports.loading": {
    es: "Cargando...",
    en: "Loading...",
  },
  "reports.pdfPreview": {
    es: "Vista previa PDF",
    en: "PDF Preview",
  },
  "reports.generating": {
    es: "Generando vista previa...",
    en: "Generating preview...",
  },
  "reports.digitalTwinReport": {
    es: "Reporte del Gemelo Digital Agrícola",
    en: "Agricultural Digital Twin Report",
  },
  "reports.summary": {
    es: "Resumen",
    en: "Summary",
  },
  "reports.evidence": {
    es: "Evidencias",
    en: "Evidence",
  },
  "reports.decisions": {
    es: "Decisiones",
    en: "Decisions",
  },
  "reports.activeConsents": {
    es: "Consentimientos activos",
    en: "Active consents",
  },
  "reports.pdfPreviewTitle": {
    es: "Vista previa del PDF",
    en: "PDF preview",
  },
  "reports.generatedByFastAPI": {
    es: "Documento generado por FastAPI",
    en: "Document generated by FastAPI",
  },
  "reports.closePreview": {
    es: "Cerrar vista previa",
    en: "Close preview",
  },
  "reports.visualizeBeforeDownload": {
    es: "Visualiza el documento antes de descargarlo",
    en: "Preview the document before downloading",
  },
  "reports.previewInstruction": {
    es: "Pulsa “Vista previa PDF” para mostrar exactamente el reporte generado por el backend.",
    en: "Click “PDF Preview” to display exactly the report generated by the backend.",
  },

  "glossary.title": {
    es: "Glosario",
    en: "Glossary",
  },
  "glossary.subtitle": {
    es: "Términos utilizados por AgroTwin explicados en lenguaje sencillo.",
    en: "Terms used by AgroTwin explained in plain language.",
  },

};


interface LanguageContextValue {
  language: Language;

  setLanguage: (
    language: Language
  ) => void;

  toggleLanguage: () => void;

  t: (
    key: string
  ) => string;

  tr: (
    es: string,
    en: string
  ) => string;

  roleLabel: (
    role:
      | string
      | null
      | undefined
  ) => string;
}

const LanguageContext =
  createContext<
    LanguageContextValue
    | undefined
  >(undefined);


function getInitialLanguage():
Language {

  const stored =
    localStorage.getItem(
      "agrotwin_language"
    );


  if (
    stored === "es"
    ||
    stored === "en"
  ) {
    return stored;
  }


  const browserLanguage =
    navigator.language
      .toLowerCase();


  return browserLanguage
    .startsWith(
      "en"
    )
      ? "en"
      : "es";
}


export function LanguageProvider({
  children,
}: {
  children: ReactNode;
}) {

  const [
    language,
    setLanguageState,
  ] = useState<Language>(
    getInitialLanguage
  );


  const setLanguage =
    (
      next:
        Language
    ) => {

      setLanguageState(
        next
      );

      localStorage.setItem(
        "agrotwin_language",
        next
      );

      document
        .documentElement
        .setAttribute(
          "lang",
          next
        );
    };


  const toggleLanguage =
    () => {

      setLanguage(
        language === "es"
          ? "en"
          : "es"
      );
    };


  const value =
  useMemo<
    LanguageContextValue
  >(
    () => ({

      language,

      setLanguage,

      toggleLanguage,

      tr: (
        es: string,
        en: string
      ) => {

        return language === "es"
          ? es
          : en;
      },

      t: (
        key: string
      ) => {

        const item =
          TRANSLATIONS[
            key
          ];

        if (!item) {
          return key;
        }

        return item[
          language
        ];
      },

      roleLabel: (
        role
      ) => {

        if (!role) {
          return "";
        }

        const key =
          `role.${
            role.toUpperCase()
          }`;

        const item =
          TRANSLATIONS[
            key
          ];

        return item
          ? item[
              language
            ]
          : role;
      },

    }),
    [
      language,
    ]
  );

  return (
    <LanguageContext.Provider
      value={
        value
      }
    >
      {children}
    </LanguageContext.Provider>
  );
}


export function useLanguage() {

  const context =
    useContext(
      LanguageContext
    );


  if (!context) {
    throw new Error(
      "useLanguage must be used inside LanguageProvider"
    );
  }


  return context;
}
