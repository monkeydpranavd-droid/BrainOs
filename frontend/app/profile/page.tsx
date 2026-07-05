"use client";

import React, { useState } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "../providers/AuthProvider";
import { UserService } from "../services/UserService";
import Sidebar from "../components/Sidebar";
import { User as UserIcon, Clock, Settings, Save, ArrowLeft, Loader2 } from "lucide-react";

export default function ProfilePage() {
  const router = useRouter();
  const { user, refresh, loading: authLoading } = useAuth();
  
  const [fullName, setFullName] = useState(user?.full_name || "");
  const [avatarUrl, setAvatarUrl] = useState(user?.avatar_url || "");
  const [timezone, setTimezone] = useState("UTC");
  const [prefAI, setPrefAI] = useState("gemini-1.5-pro");
  
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setErrorMsg(null);
    setSuccess(false);

    try {
      await UserService.updateMe({
        full_name: fullName,
        avatar_url: avatarUrl,
      });
      await refresh();
      setSuccess(true);
    } catch (err: unknown) {
      const error = err as { detail?: string };
      setErrorMsg(error.detail || "Failed to update profile details.");
    } finally {
      setLoading(false);
    }
  };

  if (authLoading || !user) {
    return null;
  }

  return (
    <div className="flex bg-zinc-950 text-zinc-100 min-h-screen">
      {/* Navigation Sidebar */}
      <Sidebar 
        currentTab="settings" 
        setCurrentTab={(tab) => router.push("/")} 
        syncStatus="Configure user profile settings" 
      />

      <main className="flex-1 flex flex-col min-h-screen">
        {/* Header */}
        <header className="border-b border-zinc-900 bg-zinc-950/60 sticky top-0 z-20 backdrop-blur-md px-8 py-4 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <button
              onClick={() => router.push("/")}
              className="p-1 hover:bg-zinc-900 rounded-lg text-zinc-400 hover:text-white transition cursor-pointer"
            >
              <ArrowLeft className="h-4 w-4" />
            </button>
            <span className="text-xs font-mono text-zinc-300 font-semibold tracking-wider">
              BrainOS / User Profile
            </span>
          </div>
        </header>

        {/* Content Canvas */}
        <div className="p-8 max-w-2xl w-full mx-auto space-y-6">
          <div>
            <h1 className="text-2xl font-bold tracking-tight text-white flex items-center gap-2.5">
              <UserIcon className="h-6 w-6 text-indigo-400" />
              Profile Settings
            </h1>
            <p className="text-xs text-zinc-500 mt-1">
              Customize your profile details and core assistant model configurations
            </p>
          </div>

          {errorMsg && (
            <div className="p-4 bg-red-950/40 border border-red-900/50 rounded-lg text-red-400 text-sm">
              <p>{errorMsg}</p>
            </div>
          )}

          {success && (
            <div className="p-4 bg-emerald-950/40 border border-emerald-900/50 rounded-lg text-emerald-400 text-sm">
              <p>Profile settings saved successfully.</p>
            </div>
          )}

          <form key={user?.id || "loading"} onSubmit={handleSave} className="space-y-6 bg-zinc-900/40 border border-zinc-850 rounded-2xl p-6">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-semibold uppercase tracking-wider text-zinc-450 mb-2">
                  Email Address (Read-only)
                </label>
                <input
                  type="text"
                  disabled
                  value={user?.email || ""}
                  className="w-full px-3 py-2 bg-zinc-950 border border-zinc-850 rounded-lg text-sm text-zinc-500 cursor-not-allowed focus:outline-none"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold uppercase tracking-wider text-zinc-450 mb-2">
                  System Role
                </label>
                <input
                  type="text"
                  disabled
                  value={user?.role || "Member"}
                  className="w-full px-3 py-2 bg-zinc-950 border border-zinc-850 rounded-lg text-sm text-zinc-500 cursor-not-allowed focus:outline-none uppercase font-mono"
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-zinc-450 mb-2">
                Full Name
              </label>
              <input
                type="text"
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
                placeholder="John Doe"
                className="w-full px-3 py-2 bg-zinc-950 border border-zinc-850 focus:border-indigo-500 rounded-lg text-sm text-zinc-200 placeholder-zinc-700 focus:outline-none transition-colors"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-zinc-450 mb-2">
                Avatar URL
              </label>
              <input
                type="text"
                value={avatarUrl}
                onChange={(e) => setAvatarUrl(e.target.value)}
                placeholder="https://example.com/avatar.png"
                className="w-full px-3 py-2 bg-zinc-950 border border-zinc-850 focus:border-indigo-500 rounded-lg text-sm text-zinc-200 placeholder-zinc-700 focus:outline-none transition-colors"
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-semibold uppercase tracking-wider text-zinc-450 mb-2">
                  Timezone
                </label>
                <div className="relative">
                  <Clock className="absolute left-3 top-2.5 h-4 w-4 text-zinc-500" />
                  <select
                    value={timezone}
                    onChange={(e) => setTimezone(e.target.value)}
                    className="w-full pl-10 pr-3 py-2 bg-zinc-950 border border-zinc-850 focus:border-indigo-500 rounded-lg text-sm text-zinc-250 focus:outline-none transition-colors appearance-none"
                  >
                    <option value="UTC">UTC (GMT+0)</option>
                    <option value="EST">EST (GMT-5)</option>
                    <option value="PST">PST (GMT-8)</option>
                    <option value="IST">IST (GMT+5:30)</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold uppercase tracking-wider text-zinc-450 mb-2">
                  Default AI Model
                </label>
                <div className="relative">
                  <Settings className="absolute left-3 top-2.5 h-4 w-4 text-zinc-500" />
                  <select
                    value={prefAI}
                    onChange={(e) => setPrefAI(e.target.value)}
                    className="w-full pl-10 pr-3 py-2 bg-zinc-950 border border-zinc-850 focus:border-indigo-500 rounded-lg text-sm text-zinc-250 focus:outline-none transition-colors appearance-none"
                  >
                    <option value="gemini-1.5-pro">Gemini 1.5 Pro</option>
                    <option value="gpt-4o">GPT-4o (Enterprise)</option>
                    <option value="claude-3-5-sonnet">Claude 3.5 Sonnet</option>
                  </select>
                </div>
              </div>
            </div>

            <div className="pt-4 border-t border-zinc-850 flex justify-end">
              <button
                type="submit"
                disabled={loading}
                className="py-2.5 px-4 bg-indigo-600 hover:bg-indigo-500 disabled:bg-indigo-750 text-white font-semibold rounded-xl flex items-center gap-2 shadow-lg shadow-indigo-600/10 hover:translate-y-[-1px] active:translate-y-[0px] transition-all cursor-pointer text-sm"
              >
                {loading ? (
                  <Loader2 className="h-4 w-4 animate-spin" />
                ) : (
                  <>
                    <Save className="h-4 w-4" />
                    Save Settings
                  </>
                )}
              </button>
            </div>
          </form>
        </div>
      </main>
    </div>
  );
}
