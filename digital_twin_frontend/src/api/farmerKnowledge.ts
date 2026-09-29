import { api } from "./client";

export type FarmerKnowledgeType =
  | "OBSERVATION"
  | "EVENT"
  | "CONSTRAINT"
  | "PREFERENCE"
  | "LOCAL_KNOWLEDGE";

export type ConstraintType =
  | "HARD"
  | "SOFT";

export interface FarmerKnowledgeRead {
  knowledge_id: string;
  parcel_id: string | null;
  knowledge_type: string;
  source_id: string;
  source_role: string;
  payload: Record<string, unknown>;
  created_at: string;
  valid_from: string | null;
  valid_until: string | null;
  spatial_scope: unknown;
  reported_confidence: number | null;
  validation_status: string;
  affects: string[];
  constraint_type: string | null;
  rationale: string | null;
  metadata: Record<string, unknown>;
}

interface CurrentUser {
  user_id: string;
  email: string;
  full_name: string;
  system_role: string;
  status: string;
}

export interface FarmerKnowledgeCreateInput {
  parcel_id: string;
  knowledge_type: FarmerKnowledgeType;
  payload: Record<string, unknown>;
  reported_confidence?: number;
  affects?: string[];
  constraint_type?: ConstraintType | null;
  rationale?: string | null;
  metadata?: Record<string, unknown>;
}

function createKnowledgeId(): string {
  const suffix =
    typeof crypto !== "undefined" &&
    typeof crypto.randomUUID === "function"
      ? crypto.randomUUID().replaceAll("-", "").slice(0, 12).toUpperCase()
      : Date.now().toString().slice(-12);

  return `FK-${suffix}`;
}

async function getCurrentUser(): Promise<CurrentUser> {
  const response = await api.get<CurrentUser>(
    "/auth/me"
  );

  return response.data;
}

export async function createFarmerKnowledge(
  input: FarmerKnowledgeCreateInput
): Promise<FarmerKnowledgeRead> {
  const currentUser =
    await getCurrentUser();

  const now =
    new Date().toISOString();

  const response =
    await api.post<FarmerKnowledgeRead>(
      "/farmer-knowledge",
      {
        knowledge_id:
          createKnowledgeId(),

        parcel_id:
          input.parcel_id,

        knowledge_type:
          input.knowledge_type,

        source_id:
          currentUser.user_id,

        source_role:
          "FARMER",

        payload:
          input.payload,

        created_at:
          now,

        valid_from:
          now,

        valid_until:
          null,

        spatial_scope:
          null,

        reported_confidence:
          input.reported_confidence ?? 0.8,

        validation_status:
          "CONFIRMED",

        affects:
          input.affects ?? [],

        constraint_type:
          input.constraint_type ?? null,

        rationale:
          input.rationale ?? null,

        metadata: {
          source:
            "PARTICIPATORY_FRONTEND",

          authenticated_user_id:
            currentUser.user_id,

          ...(
            input.metadata ?? {}
          ),
        },
      }
    );

  return response.data;
}
