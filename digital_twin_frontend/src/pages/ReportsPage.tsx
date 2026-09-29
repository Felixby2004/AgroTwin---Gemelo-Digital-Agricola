import {
  useEffect,
  useState,
} from "react";

import {
  Download,
  FileSpreadsheet,
  FileText,
  FileType2,
  Eye,
  ShieldCheck,
  Database,
  BrainCircuit,
  X,
} from "lucide-react";

import {
  getParcels,
  type Parcel,
} from "../api/parcels";

import {
  getReportPreview,
  getPDFPreviewURL,
  downloadPDF,
  downloadDOCX,
  downloadXLSX,
  type ReportPreview,
} from "../api/reports";

import {
  PDFPreview,
} from "../components/PDFPreview";

import {
  useLanguage,
} from "../i18n/LanguageContext";


export function ReportsPage() {

  const {
    t,
  } = useLanguage();


  const [
    parcels,
    setParcels,
  ] = useState<Parcel[]>([]);


  const [
    selectedParcelId,
    setSelectedParcelId,
  ] = useState("");


  const [
    preview,
    setPreview,
  ] = useState<
    ReportPreview | null
  >(null);


  const [
    pdfPreviewUrl,
    setPdfPreviewUrl,
  ] = useState<
    string | null
  >(null);


  const [
    showPDFPreview,
    setShowPDFPreview,
  ] = useState(false);


  const [
    loading,
    setLoading,
  ] = useState(true);


  const [
    previewLoading,
    setPreviewLoading,
  ] = useState(false);


  const [
    downloading,
    setDownloading,
  ] = useState("");


  const [
    error,
    setError,
  ] = useState("");


  const loadPreview = async (
    parcelId: string
  ) => {

    try {

      setLoading(true);
      setError("");

      const data =
        await getReportPreview(
          parcelId
        );

      setPreview(
        data
      );

    } catch {

      setError(
        t("reports.previewError")
      );

    } finally {

      setLoading(false);

    }
  };


  const loadPDFPreview = async () => {

    if (!selectedParcelId) {
      return;
    }


    try {

      setPreviewLoading(
        true
      );

      setError("");


      if (
        pdfPreviewUrl
      ) {

        URL.revokeObjectURL(
          pdfPreviewUrl
        );

      }


      const url =
        await getPDFPreviewURL(
          selectedParcelId
        );


      setPdfPreviewUrl(
        url
      );

      setShowPDFPreview(
        true
      );

    } catch {

      setError(
        t("reports.pdfPreviewError")
      );

    } finally {

      setPreviewLoading(
        false
      );

    }
  };


  useEffect(() => {

    const init = async () => {

      try {

        const parcelData =
          await getParcels();


        setParcels(
          parcelData
        );


        const preferred =
          parcelData.find(
            (item) =>
              item.name ===
              "Adapter Test Parcel"
          ) ||
          parcelData[0];


        if (preferred) {

          setSelectedParcelId(
            preferred.id
          );

          await loadPreview(
            preferred.id
          );

        }

      } catch {

        setError(
          t("reports.parcelsLoadError")
        );

        setLoading(false);

      }
    };


    void init();

  }, []);


  useEffect(() => {

    return () => {

      if (
        pdfPreviewUrl
      ) {

        URL.revokeObjectURL(
          pdfPreviewUrl
        );

      }

    };

  }, [
    pdfPreviewUrl,
  ]);


  const selectedParcel =
    parcels.find(
      (item) =>
        item.id ===
        selectedParcelId
    );


  const handleDownload = async (
    type:
      | "pdf"
      | "docx"
      | "xlsx"
  ) => {

    if (!selectedParcel) {
      return;
    }


    try {

      setDownloading(
        type
      );

      setError("");


      if (
        type === "pdf"
      ) {

        await downloadPDF(
          selectedParcel.id,
          selectedParcel.name
        );

      }


      if (
        type === "docx"
      ) {

        await downloadDOCX(
          selectedParcel.id,
          selectedParcel.name
        );

      }


      if (
        type === "xlsx"
      ) {

        await downloadXLSX(
          selectedParcel.id,
          selectedParcel.name
        );

      }

    } catch {

      setError(
        t("reports.downloadBlocked")
      );

    } finally {

      setDownloading("");

    }
  };


  const summary =
    preview?.summary || {};


  return (
    <div>

      {/* ============================================= */}
      {/* HEADER                                       */}
      {/* ============================================= */}

      <section className="page-header">

        <div>

          <h1>
            {t("reports.title")}
          </h1>

          <p>
{t("reports.subtitle")}
          </p>

        </div>


        <select
          className="page-select"
          value={
            selectedParcelId
          }
          onChange={(event) => {

            const parcelId =
              event.target.value;

            setSelectedParcelId(
              parcelId
            );

            setShowPDFPreview(
              false
            );


            if (
              pdfPreviewUrl
            ) {

              URL.revokeObjectURL(
                pdfPreviewUrl
              );

              setPdfPreviewUrl(
                null
              );

            }


            void loadPreview(
              parcelId
            );

          }}
        >

          {parcels.map(
            (parcel) => (

              <option
                key={parcel.id}
                value={parcel.id}
              >
                {parcel.name}
              </option>

            )
          )}

        </select>

      </section>


      {error && (
        <div className="error">
          {error}
        </div>
      )}


      {/* ============================================= */}
      {/* DOWNLOAD CARDS                               */}
      {/* ============================================= */}

      <section className="report-download-grid">

        <button
          className="report-download-card pdf"
          onClick={() =>
            void handleDownload(
              "pdf"
            )
          }
          disabled={
            downloading !== ""
          }
        >

          <div className="report-format-icon">
            <FileText size={25} />
          </div>

          <div>

            <strong>
              {t("reports.pdf")}
            </strong>

            <span>
              {t("reports.pdfHelp")}
            </span>

          </div>

          <Download size={18} />

        </button>


        <button
          className="report-download-card docx"
          onClick={() =>
            void handleDownload(
              "docx"
            )
          }
          disabled={
            downloading !== ""
          }
        >

          <div className="report-format-icon">
            <FileType2 size={25} />
          </div>

          <div>

            <strong>
              {t("reports.word")}
            </strong>

            <span>
              {t("reports.wordHelp")}
            </span>

          </div>

          <Download size={18} />

        </button>


        <button
          className="report-download-card xlsx"
          onClick={() =>
            void handleDownload(
              "xlsx"
            )
          }
          disabled={
            downloading !== ""
          }
        >

          <div className="report-format-icon">
            <FileSpreadsheet size={25} />
          </div>

          <div>

            <strong>
              {t("reports.excel")}
            </strong>

            <span>
              {t("reports.excelHelp")}
            </span>

          </div>

          <Download size={18} />

        </button>

      </section>


      {/* ============================================= */}
      {/* EXPORT CONTROL — FULL WIDTH                  */}
      {/* ============================================= */}

      <section className="export-control-full panel">

        <div className="panel-header">

          <div className="panel-header-title">

            <div className="panel-icon purple-icon">
              <ShieldCheck size={20} />
            </div>

            <div>

              <h2>
                {t("reports.exportControl")}
              </h2>

              <p>
                {t("reports.exportSubtitle")}
              </p>

            </div>

          </div>

        </div>


        <div className="export-policy-horizontal">

          <div className="policy-item">

            <ShieldCheck size={20} />

            <div>

              <strong>
                {t("reports.userPermission")}
              </strong>

              <span>
                {t("reports.exportRequired")}
              </span>

            </div>

          </div>


          <div className="policy-item">

            <ShieldCheck size={20} />

            <div>

              <strong>
                {t("reports.activeConsent")}
              </strong>

              <span>
                {t("reports.purpose")}
              </span>

            </div>

          </div>


          <div className="policy-item">

            <ShieldCheck size={20} />

            <div>

              <strong>
                {t("reports.traceability")}
              </strong>

              <span>
                {t("reports.provenancePreserved")}
              </span>

            </div>

          </div>

        </div>

      </section>


      {/* ============================================= */}
      {/* FULL-WIDTH PREVIEW                           */}
      {/* ============================================= */}

      <section className="report-preview-full panel">

        <div className="panel-header">

          <div className="panel-header-title">

            <div className="panel-icon">
              <Eye size={20} />
            </div>


            <div>

              <h2>
                {t("reports.preview")}
              </h2>

              <p>
                {selectedParcel
                  ?.name ||
                  t("reports.parcelFallback")}
              </p>

            </div>

          </div>


          <button
            className="button-primary"
            onClick={() =>
              void loadPDFPreview()
            }
            disabled={
              previewLoading
            }
          >

            <Eye size={17} />

            {previewLoading
              ? "Cargando..."
              : t("reports.pdfPreview")}

          </button>

        </div>


        {loading ? (

          <div className="loading-row">
            {t("reports.generating")}
          </div>

        ) : (

          <div className="report-preview">

            <div className="report-preview-header">

              <div className="report-logo">
                <BrainCircuit size={25} />
              </div>


              <div>

                <h2>
                  {t("reports.digitalTwinReport")}
                </h2>

                <span>
                  {selectedParcel
                    ?.name}
                </span>

              </div>

            </div>


            <div className="preview-section">

              <h3>
                {t("reports.summary")}
              </h3>


              <div className="preview-summary-grid">

                <div>

                  <Database size={17} />

                  <span>
                    Evidencias
                  </span>

                  <strong>
                    {String(
                      summary[
                        "evidence_count"
                      ] ??
                      "—"
                    )}
                  </strong>

                </div>


                <div>

                  <Database size={17} />

                  <span>
                    Sensores
                  </span>

                  <strong>
                    {String(
                      summary[
                        "sensor_count"
                      ] ??
                      "—"
                    )}
                  </strong>

                </div>


                <div>

                  <BrainCircuit size={17} />

                  <span>
                    Aportes del agricultor
                  </span>

                  <strong>
                    {String(
                      summary[
                        "farmer_knowledge_count"
                      ] ??
                      "—"
                    )}
                  </strong>

                </div>


                <div>

                  <BrainCircuit size={17} />

                  <span>
                    Trazas de decisión
                  </span>

                  <strong>
                    {String(
                      summary[
                        "decision_trace_count"
                      ] ??
                      "—"
                    )}
                  </strong>

                </div>


                <div>

                  <ShieldCheck size={17} />

                  <span>
                    Restricciones HARD
                  </span>

                  <strong>
                    {String(
                      summary[
                        "hard_constraint_count"
                      ] ??
                      "—"
                    )}
                  </strong>

                </div>


                <div>

                  <ShieldCheck size={17} />

                  <span>
                    Consentimientos activos
                  </span>

                  <strong>
                    {String(
                      summary[
                        "active_consent_count"
                      ] ??
                      "—"
                    )}
                  </strong>

                </div>

              </div>


              <div className="report-ml-boundary">

                <BrainCircuit
                  size={20}
                />

                <div>

                  <strong>
                    Random Forest · módulo predictivo complementario
                  </strong>

                  <span>
                    {preview
                      ?.ml_complementary[
                        "forecast_available"
                      ]
                      ? (
                        "Pronóstico +24 h disponible. "
                        +
                        "No tiene autoridad decisional."
                      )
                      : (
                        "Pronóstico no disponible para esta parcela. "
                        +
                        "Esto no afecta al motor de inferencia."
                      )}

                  </span>

                  <small>
                    No modifica TrustedState, no participa en el
                    ranking de escenarios y no modifica la
                    recomendación.
                  </small>

                </div>

              </div>

            </div>


            {showPDFPreview &&
              pdfPreviewUrl && (

              <div className="pdf-preview-section">

                <div className="pdf-preview-toolbar">

                  <div>

                    <strong>
                      {t("reports.preview")} del PDF
                    </strong>

                    <span>
                      {t("reports.generatedByFastAPI")}
                    </span>

                  </div>


                  <div className="pdf-preview-actions">

                    <button
                      className="pdf-icon-button"
                      type="button"
                      title={t("reports.closePreview")}
                      onClick={() =>
                        setShowPDFPreview(
                          false
                        )
                      }
                    >
                      <X size={17} />
                    </button>

                  </div>

                </div>


                <PDFPreview
                  url={
                    pdfPreviewUrl
                  }
                />

              </div>

            )}


            {!showPDFPreview && (

              <div className="report-preview-message">

                <Eye size={28} />

                <strong>
                  {t("reports.visualizeBeforeDownload")}
                </strong>

                <span>
                  Pulsa “{t("reports.preview")} PDF” para mostrar
                  exactamente el reporte generado por el backend.
                </span>

              </div>

            )}

          </div>

        )}

      </section>

    </div>
  );
}