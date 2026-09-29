import { api } from "./client";


export interface TrustedStateItem {
  variable: string;

  value:
    | number
    | string
    | Record<string, unknown>
    | null;

  unit: string | null;

  confidence_score: number;

  uncertainty_level: string;

  requires_update: boolean;

  selected_evidence_id:
    | string
    | null;
}


export interface Recommendation {
  status: string;

  allowed: boolean;

  irrigation_mm: number;

  score: number;

  reasons: string[];
}


export interface RiskData {
  level: string;

  confidence: number;

  requires_human_confirmation: boolean;

  reasons: string[];
}


export interface ParcelState {

  parcel: {
    id: string;
    name: string;
    crop_type: string | null;
    area_ha: number | null;
  };

  quality_gate_status: string;

  recommendation_allowed: boolean;

  evidence: {
    total: number;
    operational: number;
    excluded: number;
    update_required: string[];
  };

  farmer_knowledge: {
    total: number;
    constraints: number;
    preferences: number;
    observations: number;
    events: number;
    local_knowledge: number;
  };

  trusted_state: TrustedStateItem[];

  conflicts_count: number;

  conflicts: unknown[];

  recommendation:
    | Recommendation
    | null;

  risk:
    | RiskData
    | null;

  latest_trace:
    | {
        trace_id: string;
        created_at: string;

        provisional_recommendation:
          | {
              irrigation_mm: number;
              score: number;
              reasons: string[];
              status: string;
              source: string;
            }
          | null;

        farmer_response:
          | Record<string, unknown>
          | null;

        final_action:
          | Record<string, unknown>
          | null;
      }
    | null;
}


export async function getParcelState(
  parcelId: string
): Promise<ParcelState> {

  const response =
    await api.get<ParcelState>(
      `/parcels/${parcelId}/state`
    );

  return response.data;
}