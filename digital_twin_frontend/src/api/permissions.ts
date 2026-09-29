import {
  api,
} from "./client";


export type ParcelPermission =
  | "VIEW"
  | "EDIT"
  | "MANAGE_KNOWLEDGE"
  | "RUN_REASONING"
  | "RESPOND_RECOMMENDATION"
  | "MANAGE_GOVERNANCE"
  | "EXPORT_DATA"
  | "MANAGE_MEMBERS";


export type ParcelRole =
  | "OWNER"
  | "FARMER"
  | "AGRONOMIST"
  | "VIEWER";


export interface ParcelPermissions {
  parcel_id: string;
  user_id: string;
  system_role:
    | "ADMIN"
    | "USER";
  parcel_role:
    | ParcelRole
    | null;
  permissions:
    ParcelPermission[];
}


export async function getMyParcelPermissions(
  parcelId: string
): Promise<ParcelPermissions> {

  const response =
    await api.get<ParcelPermissions>(
      `/parcels/${parcelId}/my-permissions`
    );

  return response.data;
}


export function hasParcelPermission(
  permissions:
    ParcelPermissions
    | null
    | undefined,
  permission:
    ParcelPermission
): boolean {

  return (
    permissions
      ?.permissions
      .includes(
        permission
      )
    ?? false
  );
}
