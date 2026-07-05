// ─────────────────────────────────────────────────────────────────────────────
// services/backend.ts
// All functions that talk to the FastAPI backend.
//
// Rules:
//  • Each function maps 1-to-1 with a backend endpoint.
//  • Return types are always imported from lib/types — never inlined.
//  • No component logic here. No useState. No hooks.
//  • Adding a new endpoint = add one typed function here, done.
// ─────────────────────────────────────────────────────────────────────────────

import { apiClient } from "../lib/client";
import type {
  RootResponse,
  HealthResponse,
  DatabaseResponse,
  LoginPayload,
  AuthResponse,
  User,
  ChatRequest,
  ChatResponse,
  Document,
  UploadResponse,
  Agent,
  PaginatedResponse,
} from "../lib/types";

// ── System status ─────────────────────────────────────────────────────────────

/** GET /  →  { message: "BrainOS Backend Running 🚀" } */
export async function getRoot(): Promise<RootResponse> {
  return apiClient.get<RootResponse>("/");
}

/** GET /health  →  { status: "healthy", message: "..." } */
export async function getHealth(): Promise<HealthResponse> {
  return apiClient.get<HealthResponse>("/health");
}

/** GET /database  →  { database: "Connected", ping: 1 } */
export async function getDatabase(): Promise<DatabaseResponse> {
  return apiClient.get<DatabaseResponse>("/database");
}

// ── Auth (future) ─────────────────────────────────────────────────────────────

/**
 * POST /auth/login
 * After calling this, pass the returned accessToken to setAuthToken()
 * from lib/client so subsequent requests are automatically authenticated.
 */
export async function login(_payload: LoginPayload): Promise<AuthResponse> {
  // TODO: return apiClient.post<AuthResponse>("/auth/login", payload);
  return Promise.reject(new Error("Auth not yet implemented on backend."));
}

/** POST /auth/logout */
export async function logout(): Promise<void> {
  // TODO: return apiClient.post<void>("/auth/logout", {});
  return Promise.reject(new Error("Auth not yet implemented on backend."));
}

/** GET /auth/me */
export async function getMe(): Promise<User> {
  // TODO: return apiClient.get<User>("/auth/me");
  return Promise.reject(new Error("Auth not yet implemented on backend."));
}

// ── AI Chat (future) ──────────────────────────────────────────────────────────

/**
 * POST /chat
 * For streaming responses, replace with a fetch() that reads ReadableStream.
 * The function signature stays the same — only the implementation changes.
 */
export async function chat(_request: ChatRequest): Promise<ChatResponse> {
  // TODO: return apiClient.post<ChatResponse>("/chat", request);
  return Promise.reject(new Error("Chat not yet implemented on backend."));
}

// ── Documents (future) ────────────────────────────────────────────────────────

/** GET /documents?page=&pageSize= */
export async function getDocuments(
  _page = 1,
  _pageSize = 20
): Promise<PaginatedResponse<Document>> {
  // TODO: return apiClient.get(`/documents?page=${page}&pageSize=${pageSize}`);
  return Promise.reject(new Error("Documents not yet implemented on backend."));
}

/**
 * POST /documents/upload
 * Uses multipart/form-data — caller builds the FormData.
 */
export async function uploadDocument(
  _formData: FormData
): Promise<UploadResponse> {
  // TODO: return request<UploadResponse>("/documents/upload", {
  //   method: "POST",
  //   body: formData,
  //   headers: {}, // Let browser set Content-Type for multipart
  // });
  return Promise.reject(new Error("Upload not yet implemented on backend."));
}

// ── Agents (future) ───────────────────────────────────────────────────────────

/** GET /agents */
export async function getAgents(): Promise<Agent[]> {
  // TODO: return apiClient.get<Agent[]>("/agents");
  return Promise.reject(new Error("Agents not yet implemented on backend."));
}
