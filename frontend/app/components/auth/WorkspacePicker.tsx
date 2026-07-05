"use client";

import React, { useState } from "react";
import { useAuth } from "../../providers/AuthProvider";
import { WorkspaceService } from "../../services/WorkspaceService";
import { LayoutDashboard, ChevronDown, Plus, Loader2, Check } from "lucide-react";

export function WorkspacePicker() {
  const {
    activeOrg,
    activeWorkspace,
    workspaces,
    selectWorkspace,
    refresh,
  } = useAuth();

  const [isOpen, setIsOpen] = useState(false);
  const [isCreating, setIsCreating] = useState(false);
  const [newWsName, setNewWsName] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSelect = (wsId: string) => {
    selectWorkspace(wsId);
    setIsOpen(false);
  };

  const handleCreateWorkspace = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!activeOrg || !newWsName.trim()) return;
    setLoading(true);
    try {
      await WorkspaceService.create({
        organization_id: activeOrg.id,
        name: newWsName,
        visibility: "public",
      });
      await refresh();
      setNewWsName("");
      setIsCreating(false);
      setIsOpen(false);
    } catch (err) {
      console.error("Failed to create workspace:", err);
    } finally {
      setLoading(false);
    }
  };

  if (!activeOrg) return null;

  return (
    <div className="relative">
      <button
        onClick={() => setIsOpen(!isOpen)}
        disabled={loading}
        className="w-full flex items-center justify-between px-3.5 py-2.5 bg-slate-900/60 border border-slate-800 hover:border-slate-700/80 rounded-xl text-sm font-medium transition-all text-left cursor-pointer group"
      >
        <div className="flex items-center gap-2.5 min-w-0">
          <div className="h-7 w-7 rounded-lg bg-violet-650 flex items-center justify-center text-white shrink-0 shadow-md shadow-violet-650/10">
            <LayoutDashboard className="h-4 w-4" />
          </div>
          <div className="truncate">
            <p className="text-xs text-slate-500 font-semibold uppercase tracking-wider leading-none mb-1">
              Workspace
            </p>
            <p className="text-sm font-semibold text-slate-200 truncate leading-none">
              {activeWorkspace ? activeWorkspace.name : "Select Workspace"}
            </p>
          </div>
        </div>
        <ChevronDown className="h-4 w-4 text-slate-500 group-hover:text-slate-450 transition-colors shrink-0 ml-1.5" />
      </button>

      {isOpen && (
        <div className="absolute top-full left-0 right-0 mt-2 bg-slate-900 border border-slate-800 rounded-xl shadow-xl z-50 p-2.5 space-y-2">
          {isCreating ? (
            <form onSubmit={handleCreateWorkspace} className="space-y-2">
              <input
                type="text"
                value={newWsName}
                onChange={(e) => setNewWsName(e.target.value)}
                placeholder="New workspace name"
                className="w-full px-3 py-1.5 bg-slate-950 border border-slate-800 rounded-lg text-sm placeholder-slate-650 focus:outline-none focus:border-indigo-500 text-slate-200"
                autoFocus
              />
              <div className="flex gap-2">
                <button
                  type="submit"
                  disabled={loading}
                  className="flex-1 py-1.5 px-3 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg text-xs font-semibold flex justify-center items-center gap-1 cursor-pointer"
                >
                  {loading ? <Loader2 className="h-3 w-3 animate-spin" /> : "Save"}
                </button>
                <button
                  type="button"
                  onClick={() => setIsCreating(false)}
                  className="py-1.5 px-3 bg-slate-950 hover:bg-slate-900 border border-slate-850 text-slate-400 rounded-lg text-xs font-semibold cursor-pointer"
                >
                  Cancel
                </button>
              </div>
            </form>
          ) : (
            <>
              <div className="max-h-40 overflow-y-auto space-y-0.5">
                {workspaces.map((ws) => {
                  const isActive = activeWorkspace?.id === ws.id;
                  return (
                    <button
                      key={ws.id}
                      onClick={() => handleSelect(ws.id)}
                      className={`w-full flex items-center justify-between px-2.5 py-1.5 rounded-lg text-sm text-left transition-colors cursor-pointer ${
                        isActive
                          ? "bg-violet-600/10 text-violet-400 font-semibold"
                          : "hover:bg-slate-950 text-slate-400 hover:text-slate-200"
                      }`}
                    >
                      <span className="truncate">{ws.name}</span>
                      {isActive && <Check className="h-4 w-4 shrink-0 ml-1.5" />}
                    </button>
                  );
                })}
              </div>
              <div className="border-t border-slate-800 pt-2">
                <button
                  onClick={() => setIsCreating(true)}
                  className="w-full flex items-center gap-2 px-2.5 py-1.5 hover:bg-slate-950 text-slate-400 hover:text-slate-200 rounded-lg text-xs font-semibold text-left transition-colors cursor-pointer"
                >
                  <Plus className="h-3.5 w-3.5 text-slate-500" />
                  New Workspace
                </button>
              </div>
            </>
          )}
        </div>
      )}
    </div>
  );
}
