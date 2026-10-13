import { api } from "./client";


export interface ChatResponse {
  session_id: string;
  answer: string;

  parcel_id: string | null;
  parcel_name: string | null;

  orchestrator: string;
}


export interface ChatContext {
  parcelId?: string | null;
}


export async function sendChatMessage(
  message: string,
  sessionId: string,
  context?: ChatContext,
): Promise<ChatResponse> {

  const response = await api.post<ChatResponse>(
    "/api/chat",
    {
      message,
      session_id: sessionId,
      parcel_id:
        context?.parcelId ?? null,
    },
  );

  return response.data;
}
