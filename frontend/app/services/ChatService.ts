import { apiClient } from "../lib/api";

const BASE_URL =
  typeof process !== "undefined" && process.env.NEXT_PUBLIC_BACKEND_URL
    ? process.env.NEXT_PUBLIC_BACKEND_URL.replace(/\/$/, "")
    : "http://127.0.0.1:8000";

const API_BASE_URL = `${BASE_URL}/api/v1`;

export interface Conversation {
  id: string;
  organization_id: string;
  workspace_id: string;
  title: string;
  created_at: string;
  updated_at: string;
}

export interface ChatMessage {
  id: string;
  conversation_id: string;
  role: "user" | "assistant";
  content: string;
  token_count: number;
  message_metadata?: {
    sources?: Array<{
      document_id: string;
      filename: string;
      page: number | null;
      chunk_index: number;
      confidence: number;
    }>;
    confidence_score?: number;
    suggested_followups?: string[];
  };
  created_at: string;
}

export const ChatService = {
  async createConversation(orgId: string, workspaceId: string, title?: string): Promise<Conversation> {
    return apiClient.post<Conversation>("/chat/new", {
      organization_id: orgId,
      workspace_id: workspaceId,
      title: title || "New Conversation"
    });
  },

  async listConversations(workspaceId: string): Promise<Conversation[]> {
    return apiClient.get<Conversation[]>(`/chat/history?workspace_id=${workspaceId}`);
  },

  async getMessages(convoId: string): Promise<ChatMessage[]> {
    return apiClient.get<ChatMessage[]>(`/chat/${convoId}/messages`);
  },

  async deleteConversation(convoId: string): Promise<void> {
    return apiClient.delete<void>(`/chat/history?conversation_id=${convoId}`);
  },

  async askStream(
    convoId: string,
    query: string,
    documentIds: string[] | null,
    onChunk: (text: string) => void,
    onMetadata: (data: any) => void,
    signal?: AbortSignal
  ): Promise<void> {
    const response = await fetch(`${API_BASE_URL}/chat/stream`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        conversation_id: convoId,
        query,
        document_ids: documentIds
      }),
      signal
    });

    if (!response.ok) {
      throw new Error(`Failed to stream chat: ${response.statusText}`);
    }

    const reader = response.body?.getReader();
    if (!reader) {
      throw new Error("Response body is not readable");
    }

    const decoder = new TextDecoder("utf-8");
    let buffer = "";

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split("\n");
      buffer = lines.pop() || "";

      for (const line of lines) {
        const cleaned = line.trim();
        if (!cleaned || !cleaned.startsWith("data: ")) continue;

        const dataStr = cleaned.slice(6);
        if (dataStr === "[DONE]") {
          break;
        }

        try {
          const parsed = JSON.parse(dataStr);
          if (parsed.type === "metadata") {
            onMetadata(parsed);
          } else if (parsed.type === "chunk") {
            onChunk(parsed.text);
          }
        } catch (err) {
          // Ignore parsing errors for partial lines
        }
      }
    }
  }
};
