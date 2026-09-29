import { api } from "./client";

export type FarmerDecisionResponseType =
  | "ACCEPT"
  | "MODIFY"
  | "REJECT";

export interface FarmerDecisionResponse {
  response_type: FarmerDecisionResponseType;
  modified_action: Record<string, unknown> | null;
  rationale: string | null;
  responded_at?: string | null;
  metadata?: Record<string, unknown> | null;
}

export interface DecisionTrace {
  trace_id: string;
  created_at: string;
  parcel_id: string | null;

  evidence_ids: string[];
  knowledge_ids: string[];
  conflict_ids: string[];
  transformation_ids: string[];

  feasible_scenarios: Array<Record<string, unknown>>;
  rejected_scenarios: Array<Record<string, unknown>>;
  ranking: Array<Record<string, unknown>>;

  provisional_recommendation: Record<string, unknown> | null;
  farmer_response: FarmerDecisionResponse | null;
  final_action: Record<string, unknown> | null;
  outcome: Record<string, unknown> | null;
  metadata: Record<string, unknown>;
}

export interface FarmerDecisionResponseCreate {
  response_type: FarmerDecisionResponseType;
  modified_action?: Record<string, unknown> | null;
  rationale?: string | null;
}

export async function getDecisionTracesByParcel(
  parcelId: string
): Promise<DecisionTrace[]> {
  const response = await api.get<DecisionTrace[]>(
    `/parcels/${parcelId}/decision-traces`
  );

  return response.data;
}

export async function registerFarmerResponse(
  traceId: string,
  payload: FarmerDecisionResponseCreate
): Promise<DecisionTrace> {
  const response = await api.post<DecisionTrace>(
    `/decision-traces/${traceId}/response`,
    payload
  );

  return response.data;
}
