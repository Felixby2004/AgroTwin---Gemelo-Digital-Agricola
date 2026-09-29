import { api } from "./client";


export type SensorOperationalStatus =
  | "ACTIVE"
  | "STALE"
  | "NO_DATA"
  | "ERROR"
  | "INACTIVE";


export interface Sensor {
  sensor_id: string;
  parcel_id: string;
  name: string;
  sensor_type: string;
  variables: string[];
  latitude: number | null;
  longitude: number | null;
  manufacturer: string | null;
  model: string | null;
  installed_at: string | null;
  is_active: boolean;
  operational_status:
    SensorOperationalStatus | string;
  latest_value: unknown | null;
  latest_unit: string | null;
  latest_variable: string | null;
  latest_quality_score: number | null;
  latest_observed_at: string | null;
  metadata: Record<string, unknown>;
  created_at: string;
  updated_at: string;
}


export interface SensorReadingHistoryItem {
  evidence_id: string;
  variable: string;
  value: unknown;
  unit: string | null;
  quality_score: number | null;
  status: string;
  observed_at: string | null;
}


export async function getSensors(
  parcelId?: string
): Promise<Sensor[]> {

  const response =
    await api.get<Sensor[]>(
      "/sensors",
      {
        params:
          parcelId
            ? {
                parcel_id:
                  parcelId,
              }
            : undefined,
      }
    );

  return response.data;
}


export async function getParcelSensors(
  parcelId: string
): Promise<Sensor[]> {

  const response =
    await api.get<Sensor[]>(
      `/sensors/parcel/${parcelId}`
    );

  return response.data;
}


export async function getSensor(
  sensorId: string
): Promise<Sensor> {

  const response =
    await api.get<Sensor>(
      `/sensors/${encodeURIComponent(
        sensorId
      )}`
    );

  return response.data;
}


export async function getSensorReadings(
  sensorId: string,
  limit = 50
): Promise<SensorReadingHistoryItem[]> {

  const response =
    await api.get<
      SensorReadingHistoryItem[]
    >(
      `/sensors/${encodeURIComponent(
        sensorId
      )}/readings`,
      {
        params: {
          limit,
        },
      }
    );

  return response.data;
}
