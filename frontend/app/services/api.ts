// ─────────────────────────────────────────────────────────────────────────────
// services/api.ts  (legacy shim — kept for backward compatibility)
// All existing service files (dashboardService, analyticsService, etc.) import
// apiRequest() from here.  The implementation now delegates to lib/client so
// there is exactly ONE fetch layer in the entire app.
// ─────────────────────────────────────────────────────────────────────────────

import { request } from "../lib/client";

/** @deprecated Use apiClient from lib/api instead. */
export const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL?.replace(/\/$/, "") ?? "http://127.0.0.1:8000";

/**
 * Generic typed fetcher.
 * Existing services call this — no changes needed in those files.
 * New services should use apiClient from lib/api directly.
 *
 * @deprecated Use apiClient from lib/api instead.
 */
export async function apiRequest<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  return request<T>(endpoint, {
    method: (options.method as string) ?? "GET",
    headers: options.headers as Record<string, string>,
    body: options.body as string | undefined,
  });
}
