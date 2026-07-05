// ─────────────────────────────────────────────────────────────────────────────
// lib/types.ts
// Central TypeScript contract for every backend response shape.
// ─────────────────────────────────────────────────────────────────────────────

export interface RootResponse {
  message: string;
}

export interface HealthResponse {
  status: "healthy" | "degraded" | "down";
  message: string;
}

export interface DatabaseResponse {
  database: "Connected" | "Disconnected";
  ping: number;
}

export interface APIError {
  status: number;
  statusText: string;
  detail: string;
}

// ── Auth ──────────────────────────────────────────────────────────────────────

export interface User {
  id: string;
  email: string;
  full_name: string | null;
  avatar_url: string | null;
  role: "owner" | "admin" | "member" | "viewer" | "guest";
  is_active: boolean;
  created_at: string;
}

export interface LoginPayload {
  email: string;
  password: string;
}

export interface AuthResponse {
  accessToken: string;
  tokenType: "bearer";
  user: User;
}

// ── Tenant Systems ────────────────────────────────────────────────────────────

export interface Organization {
  id: string;
  name: string;
  slug: string;
  logo_url: string | null;
  industry: string | null;
  website: string | null;
  description: string | null;
  plan: "free" | "pro" | "enterprise";
  status: "active" | "suspended" | "deleted";
  created_at: string;
  updated_at: string;
}

export interface OrganizationMember {
  id: string;
  organization_id: string;
  user_id: string;
  role: "owner" | "admin" | "member" | "guest";
  invited_by: string | null;
  joined_at: string;
}

export interface Workspace {
  id: string;
  organization_id: string;
  name: string;
  description: string | null;
  visibility: "public" | "private";
  created_by: string;
  created_at: string;
  updated_at: string;
}

export interface WorkspaceMember {
  id: string;
  workspace_id: string;
  user_id: string;
  role: "owner" | "editor" | "viewer";
  joined_at: string;
}

// ── Knowledge & Documents ─────────────────────────────────────────────────────

export interface KnowledgeBase {
  id: string;
  organization_id: string;
  workspace_id: string;
  name: string;
  description: string | null;
  visibility: "public" | "private";
  created_at: string;
}

export interface Folder {
  id: string;
  organization_id: string;
  workspace_id: string;
  parent_folder_id: string | null;
  name: string;
  path: string;
  created_at: string;
}

export interface Tag {
  id: string;
  organization_id: string;
  name: string;
  color: string;
}

export interface Document {
  id: string;
  organization_id: string;
  workspace_id: string;
  uploaded_by: string;
  folder_id: string | null;
  knowledge_base_id: string | null;
  title: string;
  description: string | null;
  original_filename: string;
  storage_path: string;
  mime_type: string;
  file_size: number;
  status: "pending" | "processing" | "processed" | "failed";
  checksum: string;
  current_version: number;
  summary: string | null;
  language: string | null;
  page_count: number | null;
  created_at: string;
  updated_at: string;
  tags?: Tag[];
}

export interface DocumentVersion {
  id: string;
  document_id: string;
  version: number;
  storage_path: string;
  checksum: string;
  uploaded_by: string;
  change_notes: string | null;
  created_at: string;
}

export interface DocumentChunk {
  id: string;
  document_id: string;
  chunk_index: number;
  content: string;
  page: number | null;
  token_count: number;
  embedding_status: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  pageSize: number;
  hasNext: boolean;
}

// ── Original App Feature Shapes (backward compatibility) ──────────────────────

export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
  timestamp?: string;
}

export interface ChatRequest {
  messages: ChatMessage[];
  sessionId?: string;
}

export interface ChatResponse {
  answer: string;
  sources: string[];
  sessionId: string;
  tokensUsed: number;
}

export interface Agent {
  id: string;
  name: string;
  description: string;
  status: "active" | "idle" | "error";
  lastRun?: string;
}

export interface UploadResponse {
  id: string;
  name: string;
  status: "queued";
}
