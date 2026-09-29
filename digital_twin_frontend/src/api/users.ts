import {
  api,
} from "./client";

import type {
  User,
} from "./auth";


export interface UserCreatePayload {
  email: string;
  full_name: string;
  password: string;
  system_role:
    | "ADMIN"
    | "USER";
  metadata?: Record<
    string,
    unknown
  >;
}


export interface UserAdminUpdatePayload {
  full_name?: string;
  system_role?:
    | "ADMIN"
    | "USER";
  status?:
    | "ACTIVE"
    | "DISABLED";
  metadata?: Record<
    string,
    unknown
  >;
}


export interface UserProfileUpdatePayload {
  full_name?: string;
  metadata?: Record<
    string,
    unknown
  >;
}


export async function getUsers():
Promise<User[]> {

  const response =
    await api.get<User[]>(
      "/users"
    );

  return response.data;
}


export async function createUser(
  payload: UserCreatePayload
): Promise<User> {

  const response =
    await api.post<User>(
      "/users",
      payload
    );

  return response.data;
}


export async function updateUser(
  userId: string,
  payload:
    UserAdminUpdatePayload
): Promise<User> {

  const response =
    await api.put<User>(
      `/users/${userId}`,
      payload
    );

  return response.data;
}


export async function getMyProfile():
Promise<User> {

  const response =
    await api.get<User>(
      "/users/me/profile"
    );

  return response.data;
}


export async function updateMyProfile(
  payload:
    UserProfileUpdatePayload
): Promise<User> {

  const response =
    await api.put<User>(
      "/users/me/profile",
      payload
    );

  return response.data;
}
