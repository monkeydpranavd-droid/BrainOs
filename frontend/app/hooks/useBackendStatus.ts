// ─────────────────────────────────────────────────────────────────────────────
// hooks/useBackendStatus.ts
// React Query hook that polls the backend status endpoints.
//
// Why a dedicated hook:
//  • Decouples the fetching logic from any single component.
//  • Multiple components can call useBackendStatus() and share the same
//    cached query — no duplicate network requests.
//  • refetch() is exposed so components can implement a Retry button.
// ─────────────────────────────────────────────────────────────────────────────

"use client";

import { useQuery } from "@tanstack/react-query";
import { getRoot, getHealth, getDatabase } from "../services/backend";
import type { RootResponse, HealthResponse, DatabaseResponse, APIError } from "../lib/types";

// ── Query keys ────────────────────────────────────────────────────────────────
// Centralised here so invalidation from other hooks is explicit and safe.

export const backendQueryKeys = {
  root: ["backend", "root"] as const,
  health: ["backend", "health"] as const,
  database: ["backend", "database"] as const,
};

// ── Individual hooks ──────────────────────────────────────────────────────────

export function useRootStatus() {
  return useQuery<RootResponse, APIError>({
    queryKey: backendQueryKeys.root,
    queryFn: getRoot,
    retry: 2,
    staleTime: 30_000,
    refetchInterval: 60_000,
  });
}

export function useHealthStatus() {
  return useQuery<HealthResponse, APIError>({
    queryKey: backendQueryKeys.health,
    queryFn: getHealth,
    retry: 2,
    staleTime: 30_000,
    refetchInterval: 60_000,
  });
}

export function useDatabaseStatus() {
  return useQuery<DatabaseResponse, APIError>({
    queryKey: backendQueryKeys.database,
    queryFn: getDatabase,
    retry: 2,
    staleTime: 30_000,
    refetchInterval: 60_000,
  });
}

// ── Composite hook (used by Dashboard) ───────────────────────────────────────
// Runs both calls in parallel. Returns a unified loading / error state.

export interface BackendStatusResult {
  isLoading: boolean;
  isError: boolean;
  error: APIError | null;
  root: RootResponse | undefined;
  health: HealthResponse | undefined;
  database: DatabaseResponse | undefined;
  refetch: () => void;
}

export function useBackendStatus(): BackendStatusResult {
  const rootQuery = useRootStatus();
  const healthQuery = useHealthStatus();
  const dbQuery = useDatabaseStatus();

  const isLoading =
    rootQuery.isLoading || healthQuery.isLoading || dbQuery.isLoading;

  const isError =
    rootQuery.isError || healthQuery.isError || dbQuery.isError;

  const error =
    (rootQuery.error ?? healthQuery.error ?? dbQuery.error) as APIError | null;

  function refetch() {
    rootQuery.refetch();
    healthQuery.refetch();
    dbQuery.refetch();
  }

  return {
    isLoading,
    isError,
    error,
    root: rootQuery.data,
    health: healthQuery.data,
    database: dbQuery.data,
    refetch,
  };
}
