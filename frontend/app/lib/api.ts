// ─────────────────────────────────────────────────────────────────────────────
// lib/api.ts
// Single re-export barrel for everything a feature module needs to import.
//
// Usage:
//   import { apiClient, setAuthToken } from '@/app/lib/api';
//   import type { HealthResponse, User }  from '@/app/lib/api';
// ─────────────────────────────────────────────────────────────────────────────

export { apiClient, setAuthToken, clearAuthToken, request } from "./client";
export type { RequestOptions } from "./client";
export type {
  // Current
  RootResponse,
  HealthResponse,
  DatabaseResponse,
  APIError,
  // Auth
  User,
  LoginPayload,
  AuthResponse,
  // Chat
  ChatMessage,
  ChatRequest,
  ChatResponse,
  // Documents
  Document,
  UploadResponse,
  // Agents
  Agent,
  // Util
  PaginatedResponse,
} from "./types";
