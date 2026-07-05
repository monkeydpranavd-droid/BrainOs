import { apiClient } from "../lib/api";
import type { Document, DocumentVersion } from "../lib/types";

export interface DocumentUploadPayload {
  organization_id: string;
  workspace_id: string;
  folder_id?: string | null;
  knowledge_base_id?: string | null;
  change_notes?: string | null;
}

export const DocumentService = {
  /** Upload document directly (for smaller files) */
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

  /** Upload single file slice chunk */
  async uploadChunk(sessionId: string, chunkIndex: number, chunkBlob: Blob): Promise<void> {
    const formData = new FormData();
    formData.append("session_id", sessionId);
    formData.append("chunk_index", chunkIndex.toString());
    formData.append("file", chunkBlob, "chunk");

    return apiClient.post<void>("/documents/upload-chunk", formData);
  },

  /** Assemble uploaded chunks */
  async assembleChunks(
    sessionId: string,
    totalChunks: number,
    payload: DocumentUploadPayload,
    filename: string,
    mimeType: string
  ): Promise<Document> {
    const formData = new FormData();
    formData.append("session_id", sessionId);
    formData.append("total_chunks", totalChunks.toString());
    formData.append("organization_id", payload.organization_id);
    formData.append("workspace_id", payload.workspace_id);
    formData.append("filename", filename);
    formData.append("mime_type", mimeType);

    if (payload.folder_id) {
      formData.append("folder_id", payload.folder_id);
    }
    if (payload.knowledge_base_id) {
      formData.append("knowledge_base_id", payload.knowledge_base_id);
    }
    if (payload.change_notes) {
      formData.append("change_notes", payload.change_notes);
    }

    return apiClient.post<Document>("/documents/assemble-chunks", formData);
  },

  /** Helper method: Upload a file in 2MB chunks with real-time progress callbacks */
  async uploadInChunks(
    file: File,
    payload: DocumentUploadPayload,
    onProgress: (percent: number) => void
  ): Promise<Document> {
    const CHUNK_SIZE = 2 * 1024 * 1024; // 2MB chunk slices
    const totalChunks = Math.ceil(file.size / CHUNK_SIZE);
    const sessionId = crypto.randomUUID();

    for (let idx = 0; idx < totalChunks; idx++) {
      const start = idx * CHUNK_SIZE;
      const end = Math.min(start + CHUNK_SIZE, file.size);
      const chunkBlob = file.slice(start, end);

      // Upload chunk
      await this.uploadChunk(sessionId, idx, chunkBlob);

      // Update progress (90% allocated to chunks, last 10% to server assembly)
      const percent = Math.round((idx + 1) / totalChunks * 90);
      onProgress(percent);
    }

    // Call assemble
    const doc = await this.assembleChunks(
      sessionId,
      totalChunks,
      payload,
      file.name,
      file.type || "application/octet-stream"
    );

    onProgress(100);
    return doc;
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

  async listChunks(docId: string): Promise<any[]> {
    return apiClient.get<any[]>(`/documents/${docId}/chunks`);
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
