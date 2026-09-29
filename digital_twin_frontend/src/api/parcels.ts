import { api } from "./client";


export interface Parcel {
  id: string;
  name: string;
  crop_type: string | null;
  area_ha: number | null;
  created_at?: string;
}


export interface ParcelCreateInput {
  name: string;
  crop_type: string | null;
  area_ha: number | null;
  geometry_wkt?: string | null;
}


export interface ParcelUpdateInput {
  name: string;
  crop_type: string | null;
  area_ha: number | null;
}


export async function getParcels(): Promise<Parcel[]> {

  const response =
    await api.get<Parcel[]>(
      "/parcels"
    );

  return response.data;
}


export async function getParcel(
  parcelId: string
): Promise<Parcel> {

  const response =
    await api.get<Parcel>(
      `/parcels/${parcelId}`
    );

  return response.data;
}


export async function createParcel(
  payload: ParcelCreateInput
): Promise<Parcel> {

  const response =
    await api.post<Parcel>(
      "/parcels",
      payload
    );

  return response.data;
}


export async function updateParcel(
  parcelId: string,
  payload: ParcelUpdateInput
): Promise<Parcel> {

  const response =
    await api.put<Parcel>(
      `/parcels/${parcelId}`,
      payload
    );

  return response.data;
}


export interface ParcelMapProperties {
  parcel_id: string;
  name: string;
  crop_type: string | null;
  area_ha: number | null;
}


export interface ParcelMapFeature {
  type: "Feature";

  geometry: {
    type: string;
    coordinates: unknown;
  };

  properties: ParcelMapProperties;
}


export interface ParcelMapFeatureCollection {
  type: "FeatureCollection";
  features: ParcelMapFeature[];
}


export async function getParcelMap():
Promise<ParcelMapFeatureCollection> {

  const response =
    await api.get<ParcelMapFeatureCollection>(
      "/parcels/map"
    );

  return response.data;
}


export interface ParcelGeometryResponse {
  parcel_id: string;

  geometry: {
    type: "Polygon";

    coordinates:
      number[][][];
  };
}



export async function getParcelGeometry(
  parcelId: string
): Promise<ParcelGeometryResponse> {

  const response =
    await api.get<ParcelGeometryResponse>(
      `/parcels/${parcelId}/geometry`
    );

  return response.data;
}


export async function updateParcelGeometry(
  parcelId: string,
  geometry: {
    type: "Polygon";

    coordinates:
      number[][][];
  }
): Promise<ParcelGeometryResponse> {

  const response =
    await api.put<ParcelGeometryResponse>(
      `/parcels/${parcelId}/geometry`,
      {
        geometry,
      }
    );

  return response.data;
}


export async function deleteParcelGeometry(
  parcelId: string
): Promise<void> {

  await api.delete(
    `/parcels/${parcelId}/geometry`
  );
}
