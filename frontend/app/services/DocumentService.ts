import { apiClient } from "../lib/api";
import type { Document, DocumentVersion, Tag } from "../lib/types";

export interface DocumentUploadPayload {
  organization_id: string;
  workspace_id: string;
  folder_id?: string | null;
  knowledge_base_id?: string | null;
  change_notes?: string | null;
}

export const DocumentService = {
  async upload(file: File, payload: DocumentUploadPayload): Promise<Document> {
    const formData = new FormData();
    formData.append("file", file);
    formData.append("organization_id", payload.organization_id);
    formData.append("workspace_id", payload.workspace_id);
    
    if (payload.folder_id) {
      formData.append("folder_id", payload.folder_id);
    }
    if (payload.knowledge_base_id) {
      formData.append("knowledge_base_id", payload.knowledge_base_id);
    }
    if (payload.change_notes) {
      formData.append("change_notes", payload.change_notes);
    }

    return apiClient.post<Document>("/documents/upload", formData);
  },

  async list(
    workspaceId: string,
    folderId?: string | null,
    kbId?: string | null
  ): Promise<Document[]> {
    let path = `/documents?workspace_id=${workspaceId}`;
    if (folderId) path += `&folder_id=${folderId}`;
    if (kbId) path += `&kb_id=${kbId}`;
    return apiClient.get<Document[]>(path);
  },

  async getById(docId: string): Promise<Document> {
    return apiClient.get<Document>(`/documents/${docId}`);
  },

  async update(docId: string, payload: {
    title?: string;
    description?: string;
    folder_id?: string | null;
    knowledge_base_id?: string | null;
    summary?: string | null;
    language?: string | null;
  }): Promise<Document> {
    return apiClient.patch<Document>(`/documents/${docId}`, payload);
  },

  async delete(docId: string): Promise<void> {
    return apiClient.delete<void>(`/documents/${docId}`);
  },

  async listVersions(docId: string): Promise<DocumentVersion[]> {
    return apiClient.get<DocumentVersion[]>(`/documents/${docId}/versions`);
  },

  async getPreview(docId: string): Promise<{ preview_url: string }> {
    return apiClient.get<{ preview_url: string }>(`/documents/${docId}/preview`);
  },

  async assignTag(docId: string, tagName: string, color?: string): Promise<Document> {
    let path = `/documents/${docId}/tags?tag_name=${encodeURIComponent(tagName)}`;
    if (color) path += `&color=${encodeURIComponent(color)}`;
    return apiClient.post<Document>(path, {});
  },

  async search(workspaceId: string, query: string): Promise<Document[]> {
    return apiClient.get<Document[]>(
      `/search/documents?workspace_id=${workspaceId}&query=${encodeURIComponent(query)}`
    );
  },
};
