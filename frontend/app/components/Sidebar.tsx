"use client";

import React from "react";
import { useAuth } from "../providers/AuthProvider";
import { OrganizationPicker } from "./auth/OrganizationPicker";
import { WorkspacePicker } from "./auth/WorkspacePicker";
import { 
  Search, 
  Share2, 
  FileText, 
  Activity,
  LayoutDashboard,
  MessageSquare,
  BarChart3,
  Settings,
  Sparkles,
  LogOut
} from "lucide-react";

interface SidebarProps {
  currentTab: string;
  setCurrentTab: (tab: string) => void;
  syncStatus: string;
}

export default function Sidebar({ currentTab, setCurrentTab, syncStatus }: SidebarProps) {
  const { user, logout } = useAuth();

  const menuItems = [
    { id: "dashboard", label: "Dashboard", icon: LayoutDashboard },
    { id: "company-ai", label: "Company AI", icon: MessageSquare },
    { id: "documents", label: "Documents", icon: FileText },
    { id: "search", label: "Semantic Search", icon: Search },
    { id: "graph", label: "Knowledge Graph", icon: Share2 },
    { id: "integrations", label: "Integrations", icon: Activity },
    { id: "analytics", label: "Analytics", icon: BarChart3 },
    { id: "settings", label: "Settings", icon: Settings },
  ];

  const getInitials = (name: string) => {
    return name
      .split(" ")
      .map((n) => n[0])
      .join("")
      .toUpperCase()
      .substring(0, 2);
  };

  return (
    <aside className="w-64 border-r border-zinc-800 bg-zinc-950 flex flex-col justify-between h-screen sticky top-0">
      <div className="flex-1 flex flex-col min-h-0 overflow-y-auto">
        {/* Brand Logo */}
        <div className="p-6 border-b border-zinc-850 flex items-center justify-between shrink-0">
          <div className="flex items-center gap-2">
            <div className="w-7 h-7 rounded-lg bg-indigo-600 flex items-center justify-center font-bold text-sm tracking-wider text-white">
              B
            </div>
            <div>
              <h1 className="font-semibold text-sm tracking-tight text-white">BrainOS</h1>
              <p className="text-[10px] text-zinc-500 font-mono">ENTERPRISE CORE</p>
            </div>
          </div>
          <span className="px-2 py-0.5 text-[9px] font-mono bg-zinc-800 text-zinc-400 rounded-full border border-zinc-700/50">
            v1.0-alpha
          </span>
        </div>

        {/* Tenant Pickers */}
        <div className="p-4 space-y-3 border-b border-zinc-900/60 shrink-0">
          <OrganizationPicker />
          <WorkspacePicker />
        </div>

        {/* Sidebar Nav */}
        <nav className="p-4 space-y-1.5 flex-1">
          <p className="text-[10px] font-bold text-zinc-600 tracking-wider px-3 mb-2 uppercase font-mono">
            Navigation
          </p>
          {menuItems.map((item) => {
            const Icon = item.icon;
            const isActive = currentTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => setCurrentTab(item.id)}
                className={`w-full flex items-center gap-3 px-3 py-2 rounded-lg text-xs font-medium transition-all duration-200 cursor-pointer ${
                  isActive 
                    ? "bg-zinc-900 text-indigo-400 border border-zinc-805 shadow-[0_0_15px_rgba(99,102,241,0.08)]" 
                    : "text-zinc-400 hover:text-zinc-200 hover:bg-zinc-900/50 border border-transparent"
                }`}
              >
                <Icon className={`w-4 h-4 ${isActive ? "text-indigo-400" : "text-zinc-500"}`} />
                <span>{item.label}</span>
              </button>
            );
          })}
        </nav>

        {/* Sync Indicator Card */}
        <div className="px-4 py-2 shrink-0 mb-4">
          <div className="p-4 rounded-xl bg-zinc-900/40 border border-zinc-800/60">
            <div className="flex items-center justify-between mb-2">
              <span className="text-[10px] text-zinc-500 font-semibold uppercase tracking-wider font-mono">AI Processing</span>
              <span className="flex h-2 w-2 relative">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
              </span>
            </div>
            <p className="text-xs font-semibold text-zinc-200">Vector Index Ready</p>
            <div className="text-[10px] text-zinc-400 mt-1.5 space-y-0.5 font-mono">
              <p>Workspace Connected</p>
              <p>Sync status: {syncStatus}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Footer Profile & Logout */}
      <div className="p-4 border-t border-zinc-900 bg-zinc-950/60 space-y-3 shrink-0">
        {/* Storage Used */}
        <div className="space-y-1.5">
          <div className="flex justify-between text-[9px] text-zinc-500 font-mono">
            <span>Storage Used</span>
            <span>0.0 GB / 10 GB</span>
          </div>
          <div className="w-full h-1 bg-zinc-900 rounded-full overflow-hidden">
            <div className="bg-indigo-500 h-full w-0" />
          </div>
        </div>

        {/* Upgrade Button */}
        <button className="w-full py-1.5 px-3 bg-indigo-600/10 hover:bg-indigo-600/20 border border-indigo-500/20 hover:border-indigo-500/30 transition rounded-lg text-[10px] text-indigo-400 font-bold text-center flex items-center justify-center gap-1 cursor-pointer">
          <Sparkles className="w-3 h-3" />
          Upgrade to Pro
        </button>

        {/* User Profile Info & Logout */}
        {user && (
          <div className="flex items-center justify-between pt-2 border-t border-zinc-900/50">
            <div className="flex items-center gap-2 min-w-0">
              <div className="w-7 h-7 rounded-full bg-zinc-800 border border-zinc-700 flex items-center justify-center font-bold text-[10px] text-zinc-300 font-mono shrink-0">
                {user.full_name ? getInitials(user.full_name) : getInitials(user.email)}
              </div>
              <div className="truncate">
                <p className="text-[11px] font-semibold text-zinc-300 leading-none truncate">
                  {user.full_name || "Enterprise User"}
                </p>
                <p className="text-[9px] text-zinc-500 font-mono mt-0.5 truncate">
                  {user.email}
                </p>
              </div>
            </div>
            <button
              onClick={() => logout()}
              className="p-1.5 hover:bg-zinc-900 border border-transparent hover:border-zinc-850 rounded-lg text-zinc-500 hover:text-red-400 transition-all cursor-pointer"
              title="Sign Out"
            >
              <LogOut className="w-3.5 h-3.5" />
            </button>
          </div>
        )}
      </div>
    </aside>
  );
}
