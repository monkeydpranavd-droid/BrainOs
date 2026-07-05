import { apiClient } from "../lib/api";
import type { Folder } from "../lib/types";

export const FolderService = {
  async list(workspaceId: string): Promise<Folder[]> {
    return apiClient.get<Folder[]>(`/folders?workspace_id=${workspaceId}`);
  },

  async create(payload: {
    organization_id: string;
    workspace_id: string;
    name: string;
    parent_folder_id?: string | null;
  }): Promise<Folder> {
    return apiClient.post<Folder>("/folders", payload);
  },
};
