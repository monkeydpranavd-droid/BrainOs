"use client";

/**
 * AuthProvider — Clean rebuild from scratch (Bypassed for Dev Mode).
 *
 * Design principles:
 * 1. Single source of truth: Supabase session only (Mocked statically).
 * 2. Bypassed Supabase auth state listener: Automatically loads developer mock user.
 * 3. Bypassed Route guard: Keeps the user permanently signed in and routes to dashboard.
 */

import React, {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useRef,
  useState,
  type ReactNode,
} from "react";
import { usePathname, useRouter } from "next/navigation";
import { useQueryClient } from "@tanstack/react-query";
import type { Session } from "@supabase/supabase-js";

import { setAuthToken, clearAuthToken } from "../lib/client";
import type { User, Organization, Workspace } from "../lib/types";
import { AuthService } from "../services/AuthService";
import { OrganizationService } from "../services/OrganizationService";
import { WorkspaceService } from "../services/WorkspaceService";

// ── Public routes that don't require auth ─────────────────────────────────────
const PUBLIC_ROUTES = ["/login", "/signup", "/forgot-password", "/reset-password", "/verify-email"];

const isPublic = (path: string | null) =>
  PUBLIC_ROUTES.some((r) => path?.startsWith(r));

// ── Context shape ─────────────────────────────────────────────────────────────
interface AuthCtx {
  user: User | null;
  session: Session | null;
  loading: boolean;
  organizations: Organization[];
  workspaces: Workspace[];
  activeOrg: Organization | null;
  activeWorkspace: Workspace | null;
  selectOrganization: (orgId: string) => Promise<void>;
  selectWorkspace: (wsId: string) => void;
  logout: () => Promise<void>;
  refresh: () => Promise<void>;
}

const AuthContext = createContext<AuthCtx | null>(null);

// ── Provider ──────────────────────────────────────────────────────────────────
export function AuthProvider({ children }: { children: ReactNode }) {
  const router   = useRouter();
  const pathname = usePathname();
  const qc       = useQueryClient();

  const [session,         setSession]         = useState<Session | null>(null);
  const [user,            setUser]            = useState<User | null>(null);
  const [loading,         setLoading]         = useState(true);
  const [organizations,   setOrganizations]   = useState<Organization[]>([]);
  const [workspaces,      setWorkspaces]      = useState<Workspace[]>([]);
  const [activeOrg,       setActiveOrg]       = useState<Organization | null>(null);
  const [activeWorkspace, setActiveWorkspace] = useState<Workspace | null>(null);

  // Guard against concurrent fetches
  const fetchingRef = useRef(false);

  // ── Core: load everything for an authenticated session ──────────────────────
  const loadSession = useCallback(async (sess: Session) => {
    if (fetchingRef.current) return;
    fetchingRef.current = true;

    try {
      setAuthToken(sess.access_token);

      // 1. Backend profile
      const profile = await AuthService.getMe();
      setUser(profile);

      // 2. Organizations
      const orgs = await OrganizationService.list();
      setOrganizations(orgs);

      if (orgs.length === 0) {
        setActiveOrg(null);
        setWorkspaces([]);
        setActiveWorkspace(null);
        return;
      }

      // 3. Pick active org (restore from storage or use first)
      const savedOrgId = localStorage.getItem("brainos_org");
      const org = orgs.find((o) => o.id === savedOrgId) ?? orgs[0];
      setActiveOrg(org);
      localStorage.setItem("brainos_org", org.id);

      // 4. Workspaces for that org
      const wss = await WorkspaceService.list(org.id);
      setWorkspaces(wss);

      const savedWsId = localStorage.getItem("brainos_ws");
      const ws = wss.find((w) => w.id === savedWsId) ?? wss[0] ?? null;
      setActiveWorkspace(ws);
      if (ws) localStorage.setItem("brainos_ws", ws.id);

    } catch (err) {
      console.error("[AuthProvider] loadSession error:", err);
    } finally {
      fetchingRef.current = false;
    }
  }, []);

  // ── Reset all state on sign-out ─────────────────────────────────────────────
  const clearSession = useCallback(() => {
    clearAuthToken();
    setSession(null);
    setUser(null);
    setOrganizations([]);
    setWorkspaces([]);
    setActiveOrg(null);
    setActiveWorkspace(null);
    localStorage.removeItem("brainos_org");
    localStorage.removeItem("brainos_ws");
    qc.clear();
    fetchingRef.current = false;
  }, [qc]);

  // ── Bootstrap: subscribe to Supabase auth events (Bypassed for Dev Mode) ─────
  useEffect(() => {
    // Construct a static mock session immediately
    const mockSession: Session = {
      access_token: "developer_token",
      token_type: "bearer",
      expires_in: 999999,
      refresh_token: "mock_refresh_token",
      user: {
        id: "00000000-0000-0000-0000-000000000000",
        email: "developer@brainos.ai",
        aud: "authenticated",
        role: "owner",
        created_at: new Date().toISOString(),
        app_metadata: {},
        user_metadata: {},
        factors: [],
      } as any,
    };

    setSession(mockSession);
    loadSession(mockSession).finally(() => {
      setLoading(false);
    });
  }, [loadSession]);

  // ── Route guard (Bypassed for Dev Mode) ─────────────────────────────────────
  useEffect(() => {
    if (loading) return;

    // Always keep logged in and redirect to home if they are on a public auth path
    if (isPublic(pathname)) {
      router.replace("/");
    }
  }, [loading, pathname, router]);

  // ── Public API ──────────────────────────────────────────────────────────────
  const selectOrganization = useCallback(async (orgId: string) => {
    const org = organizations.find((o) => o.id === orgId) ?? null;
    setActiveOrg(org);
    if (!org) {
      localStorage.removeItem("brainos_org");
      setWorkspaces([]);
      setActiveWorkspace(null);
      return;
    }
    localStorage.setItem("brainos_org", org.id);
    const wss = await WorkspaceService.list(org.id);
    setWorkspaces(wss);
    const ws = wss[0] ?? null;
    setActiveWorkspace(ws);
    if (ws) localStorage.setItem("brainos_ws", ws.id);
  }, [organizations]);

  const selectWorkspace = useCallback((wsId: string) => {
    const ws = workspaces.find((w) => w.id === wsId) ?? null;
    setActiveWorkspace(ws);
    if (ws) localStorage.setItem("brainos_ws", ws.id);
    else     localStorage.removeItem("brainos_ws");
  }, [workspaces]);

  const logout = useCallback(async () => {
    clearSession();
    router.replace("/login");
  }, [clearSession, router]);

  const refresh = useCallback(async () => {
    if (session) {
      fetchingRef.current = false; // allow re-fetch
      await loadSession(session);
    }
  }, [session, loadSession]);

  // ── Loading screen on protected pages ───────────────────────────────────────
  if (loading && !isPublic(pathname)) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center bg-slate-950 gap-4">
        <div className="h-10 w-10 rounded-full border-2 border-indigo-500 border-t-transparent animate-spin" />
        <p className="text-xs font-mono text-slate-500 tracking-widest uppercase">
          Authenticating…
        </p>
      </div>
    );
  }

  return (
    <AuthContext.Provider value={{
      user, session, loading,
      organizations, workspaces, activeOrg, activeWorkspace,
      selectOrganization, selectWorkspace, logout, refresh,
    }}>
      {children}
    </AuthContext.Provider>
  );
}

// ── Hook ──────────────────────────────────────────────────────────────────────
export function useAuth(): AuthCtx {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within <AuthProvider>");
  return ctx;
}
