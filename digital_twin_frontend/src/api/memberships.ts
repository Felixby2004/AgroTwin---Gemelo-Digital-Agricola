import {
  api,
} from "./client";

import type {
  ParcelRole,
} from "./permissions";


export interface ParcelMembership {
  parcel_id: string;
  user_id: string;

  /*
   * The backend may expose the parcel role as `role`
   * or `parcel_role`. Supporting both keeps this client
   * compatible with the current membership endpoints.
   */
  role?: ParcelRole;
  parcel_role?: ParcelRole;

  created_at?: string | null;
  updated_at?: string | null;
}


export function getMembershipRole(
  membership: ParcelMembership
): ParcelRole {

  return (
    membership.role
    ?? membership.parcel_role
    ?? "VIEWER"
  );
}


export async function getParcelMembers(
  parcelId: string
): Promise<ParcelMembership[]> {

  const response =
    await api.get<ParcelMembership[]>(
      `/parcels/${parcelId}/members`
    );

  return response.data;
}


export async function addParcelMember(
  parcelId: string,
  userId: string,
  role: ParcelRole
): Promise<ParcelMembership> {

  const response =
    await api.post<ParcelMembership>(
      `/parcels/${parcelId}/members`,
      {
        user_id: userId,

        /*
         * Current backend versions used during the project
         * have used both naming conventions. Pydantic ignores
         * the unused extra field under the default configuration.
         */
        role,
        parcel_role: role,
      }
    );

  return response.data;
}


export async function updateParcelMemberRole(
  parcelId: string,
  userId: string,
  role: ParcelRole
): Promise<ParcelMembership> {

  const response =
    await api.put<ParcelMembership>(
      `/parcels/${parcelId}/members/${userId}`,
      {
        role,
        parcel_role: role,
      }
    );

  return response.data;
}


export async function removeParcelMember(
  parcelId: string,
  userId: string
): Promise<void> {

  await api.delete(
    `/parcels/${parcelId}/members/${userId}`
  );
}
