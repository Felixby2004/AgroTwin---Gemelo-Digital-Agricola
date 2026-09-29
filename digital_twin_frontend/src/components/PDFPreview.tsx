import {
  useState,
} from "react";

import {
  Document,
  Page,
  pdfjs,
} from "react-pdf";

import {
  ChevronLeft,
  ChevronRight,
  FileText,
  Maximize2,
  Minus,
  Plus,
  RotateCcw,
} from "lucide-react";


pdfjs.GlobalWorkerOptions.workerSrc =
  new URL(
    "pdfjs-dist/build/pdf.worker.min.mjs",
    import.meta.url
  ).toString();


interface PDFPreviewProps {
  url: string;
}


export function PDFPreview({
  url,
}: PDFPreviewProps) {

  const [
    numPages,
    setNumPages,
  ] = useState(0);


  const [
    pageNumber,
    setPageNumber,
  ] = useState(1);


  const [
    scale,
    setScale,
  ] = useState(1);


  const handleLoadSuccess = ({
    numPages,
  }: {
    numPages: number;
  }) => {

    setNumPages(
      numPages
    );

    setPageNumber(1);
  };


  const previousPage = () => {

    setPageNumber(
      (current) =>
        Math.max(
          1,
          current - 1
        )
    );
  };


  const nextPage = () => {

    setPageNumber(
      (current) =>
        Math.min(
          numPages,
          current + 1
        )
    );
  };


  const zoomOut = () => {

    setScale(
      (current) =>
        Math.max(
          0.5,
          Number(
            (
              current - 0.1
            ).toFixed(1)
          )
        )
    );
  };


  const zoomIn = () => {

    setScale(
      (current) =>
        Math.min(
          2.5,
          Number(
            (
              current + 0.1
            ).toFixed(1)
          )
        )
    );
  };


  const resetZoom = () => {

    setScale(1);
  };


  return (
    <div className="pdf-document-preview">

      <div className="pdf-document-toolbar">

        <div className="pdf-document-info">

          <div className="pdf-document-icon">
            <FileText size={18} />
          </div>

          <div>

            <strong>
              Reporte PDF
            </strong>

            <span>
              Vista previa del documento generado
            </span>

          </div>

        </div>


        <div className="pdf-toolbar-actions">

          {/* ========================================= */}
          {/* PAGE CONTROLS                             */}
          {/* ========================================= */}

          <div className="pdf-page-controls">

            <button
              type="button"
              onClick={previousPage}
              disabled={
                pageNumber <= 1
              }
              title="Página anterior"
            >
              <ChevronLeft size={17} />
            </button>


            <span>
              Página{" "}
              <strong>
                {pageNumber}
              </strong>
              {" "}de{" "}
              <strong>
                {numPages || "—"}
              </strong>
            </span>


            <button
              type="button"
              onClick={nextPage}
              disabled={
                pageNumber >= numPages
              }
              title="Página siguiente"
            >
              <ChevronRight size={17} />
            </button>

          </div>


          {/* ========================================= */}
          {/* ZOOM CONTROLS                             */}
          {/* ========================================= */}

          <div className="pdf-zoom-controls">

            <button
              type="button"
              onClick={zoomOut}
              disabled={
                scale <= 0.5
              }
              title="Alejar"
            >
              <Minus size={16} />
            </button>


            <span>
              {Math.round(
                scale * 100
              )}%
            </span>


            <button
              type="button"
              onClick={zoomIn}
              disabled={
                scale >= 2.5
              }
              title="Acercar"
            >
              <Plus size={16} />
            </button>


            <button
              type="button"
              onClick={resetZoom}
              title="Restablecer zoom"
            >
              <RotateCcw size={15} />
            </button>

          </div>


          <a
            href={url}
            target="_blank"
            rel="noreferrer"
            title="Abrir PDF en otra pestaña"
            className="pdf-open-button"
          >
            <Maximize2 size={17} />
          </a>

        </div>

      </div>


      <div className="pdf-document-canvas">

        <Document
          file={url}
          onLoadSuccess={
            handleLoadSuccess
          }
          loading={
            <div className="pdf-loading">
              Cargando documento...
            </div>
          }
          error={
            <div className="pdf-loading error">
              No se pudo visualizar el PDF.
            </div>
          }
        >

          <Page
            pageNumber={
              pageNumber
            }
            width={900}
            scale={scale}
            renderTextLayer={false}
            renderAnnotationLayer={false}
          />

        </Document>

      </div>

    </div>
  );
}