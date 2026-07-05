import { apiClient } from "../lib/api";
import type { Workspace, WorkspaceMember } from "../lib/types";

export const WorkspaceService = {
  async list(orgId: string): Promise<Workspace[]> {
    return apiClient.get<Workspace[]>(`/workspaces?org_id=${orgId}`);
  },

  async create(payload: {
    organization_id: string;
    name: string;
    description?: string;
    visibility?: "public" | "private";
  }): Promise<Workspace> {
    return apiClient.post<Workspace>("/workspaces", payload);
  },

  async getById(workspaceId: string): Promise<Workspace> {
    return apiClient.get<Workspace>(`/workspaces/${workspaceId}`);
  },

  async addMember(workspaceId: string, userId: string, role: string): Promise<WorkspaceMember> {
    return apiClient.post<WorkspaceMember>(`/workspaces/${workspaceId}/members`, {
      user_id: userId,
      role,
    });
  },
};
