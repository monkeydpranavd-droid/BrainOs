import { DocumentService } from "./DocumentService";

export const StorageService = {
  /** Fetch signed temporary preview link for a document */
  async getPreviewUrl(docId: string): Promise<string> {
    const { preview_url } = await DocumentService.getPreview(docId);
    return preview_url;
  },
};
