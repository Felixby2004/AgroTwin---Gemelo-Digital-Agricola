import { api } from "./client";

export interface LoginRequest {
  email: string;
  password: string;
}

export interface User {
  user_id: string;
  email: string;
  full_name: string;
  system_role: string;
  status: string;
  created_at: string;
  metadata: Record<string, unknown>;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
  expires_in_minutes: number;
  user: User;
}

export async function login(
  payload: LoginRequest
): Promise<LoginResponse> {
  const response = await api.post<LoginResponse>(
    "/auth/login",
    payload
  );

  return response.data;
}

export async function getMe(): Promise<User> {
  const response = await api.get<User>("/auth/me");

  return response.data;
}