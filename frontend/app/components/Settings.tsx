"use client";

import React, { useState } from 'react';
import { 
  Save, 
  CheckCircle,
  Building,
  Monitor,
  Cpu,
  Layers,
  Bell,
  CheckSquare,
  Square
} from 'lucide-react';

export default function SettingsView() {
  const [companyName, setCompanyName] = useState('Acme Corp');
  const [theme, setTheme] = useState('dark');
  const [aiModel, setAiModel] = useState('gemini-1.5-pro');
  const [embeddingModel, setEmbeddingModel] = useState('gecko-embedding');
  const [notifications, setNotifications] = useState('slack');
  const [connectedServices, setConnectedServices] = useState({
    slack: true,
    drive: true,
    github: true,
    notion: false
  });
  const [isSaved, setIsSaved] = useState(false);

  const handleSave = () => {
    setIsSaved(true);
    setTimeout(() => {
      setIsSaved(false);
    }, 2000);
  };

  const toggleService = (key: keyof typeof connectedServices) => {
    setConnectedServices(prev => ({
      ...prev,
      [key]: !prev[key]
    }));
  };

  return (
    <div className="space-y-8 max-w-3xl mx-auto w-full py-4">
      {/* Title & Save Trigger */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-sm font-semibold text-white tracking-tight">System Settings</h2>
          <p className="text-xs text-zinc-500 mt-0.5 font-sans">Manage company details, model routes, notifications and connected indexing nodes</p>
        </div>
        <button
          onClick={handleSave}
          className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 transition rounded-xl text-xs font-semibold text-white flex items-center gap-1.5 cursor-pointer"
        >
          {isSaved ? <CheckCircle className="w-3.5 h-3.5" /> : <Save className="w-3.5 h-3.5" />}
          {isSaved ? 'Settings Saved' : 'Save Changes'}
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Company Name */}
        <div className="p-5 bg-zinc-900/40 border border-zinc-800/80 rounded-2xl space-y-3">
          <div className="flex items-center gap-2 text-zinc-400">
            <Building className="w-4 h-4 text-indigo-400" />
            <span className="text-xs uppercase font-bold tracking-wider">Company Name</span>
          </div>
          <input
            type="text"
            value={companyName}
            onChange={(e) => setCompanyName(e.target.value)}
            className="w-full bg-zinc-950 border border-zinc-850 focus:border-indigo-500 text-xs text-white rounded-xl p-2.5 outline-none font-sans"
          />
        </div>

        {/* Theme Settings */}
        <div className="p-5 bg-zinc-900/40 border border-zinc-800/80 rounded-2xl space-y-3">
          <div className="flex items-center gap-2 text-zinc-400">
            <Monitor className="w-4 h-4 text-indigo-400" />
            <span className="text-xs uppercase font-bold tracking-wider">Theme</span>
          </div>
          <select
            value={theme}
            onChange={(e) => setTheme(e.target.value)}
            className="w-full bg-zinc-950 border border-zinc-850 focus:border-indigo-500 text-xs text-white rounded-xl p-2.5 outline-none font-sans"
          >
            <option value="dark">Dark Theme</option>
            <option value="light">Light Theme</option>
            <option value="system">System Default</option>
          </select>
        </div>

        {/* AI Model Routing */}
        <div className="p-5 bg-zinc-900/40 border border-zinc-800/80 rounded-2xl space-y-3">
          <div className="flex items-center gap-2 text-zinc-400">
            <Cpu className="w-4 h-4 text-indigo-400" />
            <span className="text-xs uppercase font-bold tracking-wider">AI Model</span>
          </div>
          <select
            value={aiModel}
            onChange={(e) => setAiModel(e.target.value)}
            className="w-full bg-zinc-950 border border-zinc-850 focus:border-indigo-500 text-xs text-white rounded-xl p-2.5 outline-none font-sans"
          >
            <option value="gemini-1.5-pro">Gemini 1.5 Pro</option>
            <option value="gemini-1.5-flash">Gemini 1.5 Flash</option>
            <option value="brain-fine-tuned">BrainOS Custom Fine-tuned</option>
          </select>
        </div>

        {/* Embedding Model */}
        <div className="p-5 bg-zinc-900/40 border border-zinc-800/80 rounded-2xl space-y-3">
          <div className="flex items-center gap-2 text-zinc-400">
            <Layers className="w-4 h-4 text-indigo-400" />
            <span className="text-xs uppercase font-bold tracking-wider">Embedding Model</span>
          </div>
          <select
            value={embeddingModel}
            onChange={(e) => setEmbeddingModel(e.target.value)}
            className="w-full bg-zinc-950 border border-zinc-850 focus:border-indigo-500 text-xs text-white rounded-xl p-2.5 outline-none font-sans"
          >
            <option value="gecko-embedding">Gecko Text Embedding</option>
            <option value="custom-vectorizer">Custom Vectorizer</option>
          </select>
        </div>

        {/* System Notifications */}
        <div className="p-5 bg-zinc-900/40 border border-zinc-800/80 rounded-2xl space-y-3">
          <div className="flex items-center gap-2 text-zinc-400">
            <Bell className="w-4 h-4 text-indigo-400" />
            <span className="text-xs uppercase font-bold tracking-wider">Notifications</span>
          </div>
          <select
            value={notifications}
            onChange={(e) => setNotifications(e.target.value)}
            className="w-full bg-zinc-950 border border-zinc-850 focus:border-indigo-500 text-xs text-white rounded-xl p-2.5 outline-none font-sans"
          >
            <option value="slack">Slack Alerts</option>
            <option value="email">Email Logs</option>
            <option value="muted">Muted</option>
          </select>
        </div>

        {/* Connected Sync Services */}
        <div className="p-5 bg-zinc-900/40 border border-zinc-800/80 rounded-2xl space-y-3">
          <div className="flex items-center gap-2 text-zinc-400">
            <CheckSquare className="w-4 h-4 text-indigo-400" />
            <span className="text-xs uppercase font-bold tracking-wider">Connected Services</span>
          </div>
          
          <div className="grid grid-cols-2 gap-3 text-xs pt-1 font-sans">
            {(Object.keys(connectedServices) as Array<keyof typeof connectedServices>).map((key) => {
              const checked = connectedServices[key];
              return (
                <button
                  key={key}
                  onClick={() => toggleService(key)}
                  className="flex items-center gap-2 p-2 rounded-lg bg-zinc-950/80 border border-zinc-850 text-left hover:border-zinc-700 transition cursor-pointer text-zinc-300 hover:text-white"
                >
                  {checked ? (
                    <CheckSquare className="w-3.5 h-3.5 text-indigo-400" />
                  ) : (
                    <Square className="w-3.5 h-3.5 text-zinc-650" />
                  )}
                  <span className="capitalize">{key === 'drive' ? 'Google Drive' : key}</span>
                </button>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
}
