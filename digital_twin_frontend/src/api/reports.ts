import { api } from "./client";

export interface ReportPreview {

  parcel_id: string;

  generated_at: string;

  parcel:
    Record<
      string,
      unknown
    >;

  summary:
    Record<
      string,
      unknown
    >;

  latest_decision:
    | Record<
        string,
        unknown
      >
    | null;

  evidence:
    Array<
      Record<
        string,
        unknown
      >
    >;

  sensors:
    Array<
      Record<
        string,
        unknown
      >
    >;

  farmer_knowledge:
    Array<
      Record<
        string,
        unknown
      >
    >;

  decision_traces:
    Array<
      Record<
        string,
        unknown
      >
    >;

  ml_complementary:
    Record<
      string,
      unknown
    >;

  governance:
    Record<
      string,
      unknown
    >;
}

export async function getReportPreview(
  parcelId: string
): Promise<ReportPreview> {

  const response =
    await api.get<ReportPreview>(
      `/reports/parcels/${parcelId}/preview`
    );

  return response.data;
}


/* ===================================================== */
/* PDF PREVIEW                                           */
/* ===================================================== */
export async function getPDFPreviewURL(
  parcelId: string
): Promise<string> {

  const response =
    await api.get(
      `/reports/parcels/${parcelId}/pdf-preview`,
      {
        responseType: "blob",
      }
    );


  const blob = new Blob(
    [response.data],
    {
      type: "application/pdf",
    }
  );


  return URL.createObjectURL(
    blob
  );
}

/* ===================================================== */
/* DOWNLOAD                                              */
/* ===================================================== */

async function downloadFile(
  url: string,
  filename: string
) {

  const response =
    await api.get(
      url,
      {
        responseType: "blob",
      }
    );


  const blobUrl =
    URL.createObjectURL(
      response.data
    );


  const link =
    document.createElement("a");


  link.href = blobUrl;

  link.download = filename;


  document.body.appendChild(
    link
  );


  link.click();


  link.remove();


  URL.revokeObjectURL(
    blobUrl
  );
}


export async function downloadPDF(
  parcelId: string,
  parcelName: string
) {

  return downloadFile(
    `/reports/parcels/${parcelId}/pdf`,
    `${parcelName}_report.pdf`
  );
}


export async function downloadDOCX(
  parcelId: string,
  parcelName: string
) {

  return downloadFile(
    `/reports/parcels/${parcelId}/docx`,
    `${parcelName}_report.docx`
  );
}


export async function downloadXLSX(
  parcelId: string,
  parcelName: string
) {

  return downloadFile(
    `/reports/parcels/${parcelId}/xlsx`,
    `${parcelName}_report.xlsx`
  );
}