import { apiClient } from "../lib/api";
import type { KnowledgeBase } from "../lib/types";

export const KnowledgeBaseService = {
  async list(workspaceId: string): Promise<KnowledgeBase[]> {
    return apiClient.get<KnowledgeBase[]>(`/knowledge-bases?workspace_id=${workspaceId}`);
  },

  async create(payload: {
    organization_id: string;
    workspace_id: string;
    name: string;
    description?: string;
    visibility?: "public" | "private";
  }): Promise<KnowledgeBase> {
    return apiClient.post<KnowledgeBase>("/knowledge-bases", payload);
  },
};
