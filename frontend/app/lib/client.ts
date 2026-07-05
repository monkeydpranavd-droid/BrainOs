// ─────────────────────────────────────────────────────────────────────────────
// lib/client.ts
// Enterprise-grade HTTP client built on native fetch.
// ─────────────────────────────────────────────────────────────────────────────

import type { APIError } from "./types";

const DEFAULT_TIMEOUT_MS = 10_000;

const BASE_URL =
  process.env.NEXT_PUBLIC_BACKEND_URL?.replace(/\/$/, "") ??
  process.env.NEXT_PUBLIC_API_URL?.replace(/\/$/, "") ??
  "http://127.0.0.1:8000";

let _authToken: string | null = null;

export function setAuthToken(token: string): void {
  _authToken = token;
}

export function clearAuthToken(): void {
  _authToken = null;
}

// ── Request interceptor ───────────────────────────────────────────────────────
async function applyRequestInterceptor(headers: Record<string, string>): Promise<Record<string, string>> {
  const mutated = { ...headers };

  if (typeof window !== "undefined") {
    // Client-side execution
    if (_authToken) {
      mutated["Authorization"] = `Bearer ${_authToken}`;
    } else {
      try {
        const { supabaseClient } = await import("./supabase/client");
        const { data: { session } } = await supabaseClient.auth.getSession();
        if (session?.access_token) {
          mutated["Authorization"] = `Bearer ${session.access_token}`;
        }
      } catch (err) {
        // Fallback or unauthenticated
      }
    }
  }

  return mutated;
}

// ── Response interceptor ──────────────────────────────────────────────────────
async function applyResponseInterceptor(response: Response): Promise<Response> {
  if (response.status === 401) {
    if (typeof window !== "undefined") {
      if (!window.location.pathname.startsWith("/login")) {
        clearAuthToken();
        window.location.href = "/login";
      }
    }
  }
  return response;
}

// ── Error builder ─────────────────────────────────────────────────────────────
interface EnhancedAPIError extends APIError {
  rawBody?: unknown;
}

async function buildAPIError(response: Response): Promise<EnhancedAPIError> {
  let detail = response.statusText;
  let rawBody: unknown = null;
  try {
    const text = await response.text();
    try {
      const parsed = JSON.parse(text);
      rawBody = parsed;
      const bodyObj = parsed as Record<string, unknown>;
      if (bodyObj && typeof bodyObj.detail === "string") {
        detail = bodyObj.detail;
      } else if (bodyObj && typeof bodyObj.detail === "object") {
        detail = JSON.stringify(bodyObj.detail);
      } else if (bodyObj && typeof bodyObj.error === "string") {
        detail = bodyObj.error;
      }
    } catch {
      rawBody = text;
      detail = text || response.statusText;
    }
  } catch {
    // Body read failed
  }
  return { status: response.status, statusText: response.statusText, detail, rawBody };
}

// ── Core request function ─────────────────────────────────────────────────────
export interface RequestOptions extends Omit<RequestInit, "headers"> {
  headers?: Record<string, string>;
  timeoutMs?: number;
}

export async function request<T>(
  path: string,
  options: RequestOptions = {}
): Promise<T> {
  const { headers = {}, timeoutMs = DEFAULT_TIMEOUT_MS, ...rest } = options;

  const interceptorHeaders = await applyRequestInterceptor(headers);
  const isMultipart = rest.body instanceof FormData;

  const mergedHeaders: Record<string, string> = {
    Accept: "application/json",
    ...interceptorHeaders,
  };

  if (!isMultipart) {
    mergedHeaders["Content-Type"] = "application/json";
  }

  // Prepend "/api/v1" if path is not "/" and does not already contain "/api/v1"
  let formattedPath = path;
  if (formattedPath !== "/" && !formattedPath.startsWith("/api/v1/") && !formattedPath.startsWith("api/v1/")) {
    const cleanPath = formattedPath.startsWith("/") ? formattedPath : `/${formattedPath}`;
    formattedPath = `/api/v1${cleanPath}`;
  }

  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), timeoutMs);

  let response: Response;
  const method = options.method || "GET";
  const fullUrl = `${BASE_URL}${formattedPath}`;

  try {
    response = await fetch(fullUrl, {
      ...rest,
      headers: mergedHeaders,
      signal: controller.signal,
    });
  } catch (err) {
    clearTimeout(timer);
    if (err instanceof DOMException && err.name === "AbortError") {
      const timeoutErr = {
        status: 408,
        statusText: "Request Timeout",
        detail: `Request to ${path} timed out after ${timeoutMs}ms`,
      };
      console.error("API REQUEST FAILURE (TIMEOUT):", {
        method,
        url: fullUrl,
        error: timeoutErr,
      });
      throw timeoutErr;
    }
    const networkErr = {
      status: 0,
      statusText: "Network Error",
      detail: err instanceof Error ? err.message : "Could not reach backend.",
    };
    console.error("API REQUEST FAILURE (NETWORK):", {
      method,
      url: fullUrl,
      error: networkErr,
    });
    throw networkErr;
  } finally {
    clearTimeout(timer);
  }

  await applyResponseInterceptor(response);

  if (!response.ok) {
    const apiError = await buildAPIError(response);
    
    console.error("API REQUEST FAILURE (RESPONSE ERROR):");
    console.error(`- Method: ${method}`);
    console.error(`- URL: ${fullUrl}`);
    console.error(`- Status: ${response.status}`);
    console.error(`- Status Text: ${response.statusText}`);
    console.error(`- Error Detail:`, apiError.detail);
    console.error(`- Response Body:`, apiError.rawBody);
    
    throw apiError;
  }

  if (response.status === 204) {
    return undefined as unknown as T;
  }

  return response.json() as Promise<T>;
}

// ── Convenience methods ───────────────────────────────────────────────────────
export const apiClient = {
  get: <T>(path: string, options?: RequestOptions) =>
    request<T>(path, { method: "GET", ...options }),

  post: <T>(path: string, body: unknown, options?: RequestOptions) =>
    request<T>(path, {
      method: "POST",
      body: body instanceof FormData ? body : JSON.stringify(body),
      ...options,
    }),

  put: <T>(path: string, body: unknown, options?: RequestOptions) =>
    request<T>(path, {
      method: "PUT",
      body: JSON.stringify(body),
      ...options,
    }),

  delete: <T>(path: string, options?: RequestOptions) =>
    request<T>(path, { method: "DELETE", ...options }),

  patch: <T>(path: string, body: unknown, options?: RequestOptions) =>
    request<T>(path, {
      method: "PATCH",
      body: JSON.stringify(body),
      ...options,
    }),
};
