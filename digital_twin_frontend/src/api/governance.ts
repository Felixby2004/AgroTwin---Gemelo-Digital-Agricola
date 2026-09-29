import { api } from "./client";


export interface Consent {
  consent_id: string;
  parcel_id: string;
  subject_id: string;
  purposes: string[];
  permissions: string[];
  allowed_data_categories: string[];
  created_at: string;
  valid_until: string | null;
  status: string;
  metadata: Record<string, unknown>;
}


export interface AuditEvent {
  audit_id: string;
  parcel_id: string | null;
  actor_id: string;
  action: string;
  allowed: boolean;
  consent_id: string | null;
  purpose: string | null;
  data_category: string | null;
  created_at: string;
  details: Record<string, unknown>;
}


export async function getParcelConsents(
  parcelId: string
): Promise<Consent[]> {
  const response = await api.get<Consent[]>(
    `/governance/consents/parcel/${parcelId}`
  );

  return response.data;
}


export async function getParcelAudit(
  parcelId: string
): Promise<AuditEvent[]> {
  const response = await api.get<AuditEvent[]>(
    `/governance/audit/parcel/${parcelId}`
  );

  return response.data;
}


export async function updateConsentStatus(
  consentId: string,
  status: "ACTIVE" | "REVOKED" | "EXPIRED"
): Promise<Consent> {
  const response = await api.patch<Consent>(
    `/governance/consents/${consentId}/status`,
    {
      status,
    }
  );

  return response.data;
}