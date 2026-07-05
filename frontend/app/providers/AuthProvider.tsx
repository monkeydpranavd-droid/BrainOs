"use client";

import React, { createContext, useContext, useEffect, useState, ReactNode } from "react";
import { usePathname, useRouter } from "next/navigation";
import { useQueryClient } from "@tanstack/react-query";
import { supabaseClient } from "../lib/supabase/client";
import { setAuthToken, clearAuthToken } from "../lib/client";
import { AuthService } from "../services/AuthService";
import { OrganizationService } from "../services/OrganizationService";
import { WorkspaceService } from "../services/WorkspaceService";
import type { User, Organization, Workspace } from "../lib/types";
import type { Session } from "@supabase/supabase-js";
import { Loader2 } from "lucide-react";

interface AuthContextType {
  user: User | null;
  session: Session | null;
  loading: boolean;
  activeOrg: Organization | null;
  activeWorkspace: Workspace | null;
  organizations: Organization[];
  workspaces: Workspace[];
  selectOrganization: (orgId: string) => Promise<void>;
  selectWorkspace: (wsId: string) => void;
  logout: () => Promise<void>;
  refresh: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

const PUBLIC_ROUTES = [
  "/login",
  "/signup",
  "/forgot-password",
  "/reset-password",
  "/verify-email"
];

export function AuthProvider({ children }: { children: ReactNode }) {
  const [session, setSession] = useState<Session | null>(null);
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  
  const [organizations, setOrganizations] = useState<Organization[]>([]);
  const [workspaces, setWorkspaces] = useState<Workspace[]>([]);
  const [activeOrg, setActiveOrg] = useState<Organization | null>(null);
  const [activeWorkspace, setActiveWorkspace] = useState<Workspace | null>(null);

  const pathname = usePathname();
  const router = useRouter();
  const queryClient = useQueryClient();

  // 1. Refresh user details and sync with backend
  const syncUserSession = async (token: string) => {
    try {
      setAuthToken(token);
      const profile = await AuthService.getMe();
      setUser(profile);
      
      // Load organizations
      const orgs = await OrganizationService.list();
      setOrganizations(orgs);
      
      // Select active organization from storage or fallback
      const savedOrgId = localStorage.getItem("brainos_active_org_id");
      const matchedOrg = orgs.find((o) => o.id === savedOrgId) || orgs[0] || null;
      
      if (matchedOrg) {
        setActiveOrg(matchedOrg);
        localStorage.setItem("brainos_active_org_id", matchedOrg.id);
        
        // Load workspaces for organization
        const wsList = await WorkspaceService.list(matchedOrg.id);
        setWorkspaces(wsList);
        
        const savedWsId = localStorage.getItem("brainos_active_ws_id");
        const matchedWs = wsList.find((w) => w.id === savedWsId) || wsList[0] || null;
        if (matchedWs) {
          setActiveWorkspace(matchedWs);
          localStorage.setItem("brainos_active_ws_id", matchedWs.id);
        } else {
          setActiveWorkspace(null);
        }
      } else {
        setActiveOrg(null);
        setWorkspaces([]);
        setActiveWorkspace(null);
      }
    } catch (err) {
      console.error("Failed to sync auth session details:", err);
      // Clear token if backend fails profile check
      clearAuthToken();
      setUser(null);
    }
  };

  // 2. Auth State subscription and session restore
  useEffect(() => {
    // Initial Session load
    supabaseClient.auth.getSession().then(({ data: { session } }) => {
      setSession(session);
      if (session?.access_token) {
        syncUserSession(session.access_token).finally(() => setLoading(false));
      } else {
        setLoading(false);
      }
    });

    const { data: { subscription } } = supabaseClient.auth.onAuthStateChange(
      async (event, currentSession) => {
        setSession(currentSession);
        if (currentSession?.access_token) {
          setAuthToken(currentSession.access_token);
          await syncUserSession(currentSession.access_token);
        } else {
          clearAuthToken();
          setUser(null);
          setOrganizations([]);
          setWorkspaces([]);
          setActiveOrg(null);
          setActiveWorkspace(null);
          localStorage.removeItem("brainos_active_org_id");
          localStorage.removeItem("brainos_active_ws_id");
        }
        setLoading(false);
      }
    );

    return () => {
      subscription.unsubscribe();
    };
  }, []);

  // 3. Global client-side route guard
  useEffect(() => {
    if (!loading) {
      const isPublicRoute = PUBLIC_ROUTES.some((route) => pathname?.startsWith(route));
      if (!user && !isPublicRoute) {
        router.push("/login");
      } else if (user && isPublicRoute) {
        router.push("/");
      }
    }
  }, [loading, user, pathname, router]);

  const selectOrganization = async (orgId: string) => {
    const org = organizations.find((o) => o.id === orgId) || null;
    setActiveOrg(org);
    if (org) {
      localStorage.setItem("brainos_active_org_id", org.id);
      // Load workspaces
      const wsList = await WorkspaceService.list(org.id);
      setWorkspaces(wsList);
      const defaultWs = wsList[0] || null;
      setActiveWorkspace(defaultWs);
      if (defaultWs) {
        localStorage.setItem("brainos_active_ws_id", defaultWs.id);
      } else {
        localStorage.removeItem("brainos_active_ws_id");
      }
    } else {
      localStorage.removeItem("brainos_active_org_id");
      localStorage.removeItem("brainos_active_ws_id");
      setWorkspaces([]);
      setActiveWorkspace(null);
    }
  };

  const selectWorkspace = (wsId: string) => {
    const ws = workspaces.find((w) => w.id === wsId) || null;
    setActiveWorkspace(ws);
    if (ws) {
      localStorage.setItem("brainos_active_ws_id", ws.id);
    } else {
      localStorage.removeItem("brainos_active_ws_id");
    }
  };

  const logout = async () => {
    setLoading(true);
    try {
      await AuthService.signOut();
    } catch (err) {
      console.error("Logout error:", err);
    }
    clearAuthToken();
    setUser(null);
    setSession(null);
    setOrganizations([]);
    setWorkspaces([]);
    setActiveOrg(null);
    setActiveWorkspace(null);
    localStorage.clear();
    queryClient.clear();
    setLoading(false);
    router.push("/login");
  };

  const refresh = async () => {
    const currentSession = await AuthService.getSession();
    if (currentSession?.access_token) {
      await syncUserSession(currentSession.access_token);
    }
  };

  const isPublicRoute = PUBLIC_ROUTES.some((route) => pathname?.startsWith(route));

  // Show a professional global loader only on protected pages when checking auth state
  if (loading && !isPublicRoute) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center bg-slate-950 text-slate-100 gap-4">
        <Loader2 className="h-8 w-8 animate-spin text-indigo-500" />
        <p className="text-xs font-mono text-slate-500 tracking-wider">Syncing security credentials...</p>
      </div>
    );
  }

  return (
    <AuthContext.Provider
      value={{
        user,
        session,
        loading,
        activeOrg,
        activeWorkspace,
        organizations,
        workspaces,
        selectOrganization,
        selectWorkspace,
        logout,
        refresh,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used inside AuthProvider");
  }
  return context;
}
