import { api } from "./client";


/* ===================================================== */
/* TYPES                                                 */
/* ===================================================== */

export type MLModelStatus =
  | "MIXED_COMPLEMENTARY_MODEL"
  | "SUPPORTED_COMPLEMENTARY_MODEL"
  | "NO_CLEAR_ADVANTAGE"
  | string;


export type SoilMoistureTrend =
  | "INCREASING"
  | "DECREASING"
  | "STABLE"
  | "UNKNOWN";


export type SHAPDirection =
  | "INCREASE_MOISTURE"
  | "DECREASE_MOISTURE"
  | "NEUTRAL";


export interface MLFeatureAvailability {
  available: number;
  total: number;
  missing: string[];
}


export interface MLUncertainty {
  method: string;

  ensemble_std: number;

  p10: number;

  p90: number;
}


export interface SHAPFeatureContribution {
  feature: string;

  contribution_to_delta: number;

  direction: SHAPDirection;
}


export interface MLExplanation {
  method: string;

  explained_output: string;

  features: SHAPFeatureContribution[];
}


export interface SoilMoistureForecast {
  parcel_id: string;

  reference_timestamp: string;

  model: string;

  model_status: MLModelStatus;

  purpose: string;

  prediction_horizon_hours: number;

  provenance: string;

  decision_authority: boolean;

  modifies_trusted_state: boolean;

  modifies_recommendation: boolean;

  feature_availability: MLFeatureAvailability;

  current_soil_moisture: number;

  predicted_delta_24h: number;

  predicted_soil_moisture_24h: number;

  delta_percent: number | null;

  trend: SoilMoistureTrend;

  uncertainty: MLUncertainty;

  explanation: MLExplanation;
}




/* ===================================================== */
/* COMPLEMENTARY MOISTURE HISTORY                        */
/* ===================================================== */

export interface SoilMoistureHistoryPoint {
  timestamp: string;

  soil_moisture: number;

  unit: string | null;

  quality_score:
    | number
    | null;

  status: string;

  source_type:
    | string
    | null;

  source_name:
    | string
    | null;

  source_id:
    | string
    | null;
}


export interface SoilMoistureHistory {
  parcel_id: string;

  requested_hours: number;

  coverage_hours: number;

  count: number;

  variable: string;

  provenance: string;

  decision_authority: boolean;

  modifies_trusted_state: boolean;

  modifies_recommendation: boolean;

  points: SoilMoistureHistoryPoint[];
}


/* ===================================================== */
/* ML STATUS                                             */
/* ===================================================== */

export interface MLValidationMetrics {
  random_forest_mae?: number;
  random_forest_rmse?: number;
  random_forest_r2?: number;

  persistence_mae?: number;
  persistence_rmse?: number;
  persistence_r2?: number;

  mae_improvement_percent?: number;

  rmse_improvement_percent?: number;
}


export interface MLStatus {
  available: boolean;

  model: string;

  model_status: MLModelStatus;

  purpose: string;

  target: string;

  output: string;

  prediction_horizon_hours: number;

  provenance: string;

  decision_authority: boolean;

  modifies_trusted_state: boolean;

  modifies_recommendation: boolean;

  features: string[];

  validation_summary?: {
    method: string;

    period: string;

    status: string;

    aggregate?: MLValidationMetrics;

    final_test_2025?: MLValidationMetrics;
  };

  feature_importance?: Array<{
    feature: string;

    importance: number;
  }>;
}


/* ===================================================== */
/* API                                                   */
/* ===================================================== */

export async function getMLStatus():
Promise<MLStatus> {

  const response =
    await api.get<MLStatus>(
      "/ml/status"
    );

  return response.data;
}


export async function getParcelSoilMoistureForecast(
  parcelId: string
): Promise<SoilMoistureForecast> {

  const response =
    await api.get<SoilMoistureForecast>(
      `/ml/parcels/${parcelId}/soil-moisture-forecast`
    );

  return response.data;
}


export async function getParcelSoilMoistureHistory(
  parcelId: string,
  hours = 72
): Promise<SoilMoistureHistory> {

  const response =
    await api.get<SoilMoistureHistory>(
      `/ml/parcels/${parcelId}/soil-moisture-history`,
      {
        params: {
          hours,
        },
      }
    );

  return response.data;
}

