"use client";

import React, { useEffect, useState } from 'react';
import { 
  FileText, 
  GitBranch, 
  Activity, 
  Search, 
  ArrowUpRight 
} from 'lucide-react';
import { 
  getDashboardStats, 
  getRecentSyncActions, 
  DashboardStats,
  SyncLog
} from '../services/dashboardService';

export default function Dashboard() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [syncLogs, setSyncLogs] = useState<SyncLog[]>([]);
  const [searchVal, setSearchVal] = useState('');

  useEffect(() => {
    getDashboardStats().then(setStats);
    getRecentSyncActions().then(setSyncLogs);
  }, []);

  const recentUploads = [
    { name: 'Payments API Roadmap', type: 'Confluence', time: 'Indexed 1h ago' },
    { name: 'Enterprise Authentication Specs', type: 'Google Drive', time: 'Indexed 3h ago' },
    { name: 'Company Onboarding Playbook', type: 'Notion', time: 'Indexed 1d ago' }
  ];

  const recentAIAnswers = [
    { query: 'Who is the lead engineer of Payments 2.0?', answer: 'Jane Doe is the Lead Architect and Lead Engineer...' },
    { query: 'Where is the onboarding guide stored?', answer: 'The Company Onboarding Playbook is stored in Notion...' },
    { query: 'Summarize Project Atlas technologies', answer: 'Project Atlas is built with Next.js 15 and TypeScript...' }
  ];

  return (
    <div className="space-y-12 max-w-5xl mx-auto w-full py-4">
      {/* Apple-style Hero Header & Status */}
      <div className="space-y-4">
        <div className="space-y-1.5">
          <h1 className="text-3xl font-bold tracking-tight text-white font-sans">
            Good Evening, John.
          </h1>
          <p className="text-sm text-zinc-400 font-sans">
            BrainOS has indexed <span className="text-indigo-400 font-semibold">347 documents</span>. <span className="text-indigo-400 font-semibold">3 integrations</span> are active.
          </p>
        </div>

        {/* Minimal Search Input Box */}
        <div className="relative max-w-xl">
          <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-zinc-500" />
          <input
            type="text"
            value={searchVal}
            onChange={(e) => setSearchVal(e.target.value)}
            placeholder="Ask BrainOS..."
            className="w-full bg-zinc-900/40 border border-zinc-800/80 focus:border-indigo-500/85 focus:ring-1 focus:ring-indigo-500/30 rounded-xl pl-10 pr-4 py-2.5 text-xs text-white placeholder-zinc-500 outline-none transition-all duration-300"
          />
        </div>
      </div>

      {/* Clean Metrics Grid */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-6 pt-2">
        <div className="space-y-1">
          <p className="text-3xl font-extrabold text-white tracking-tight font-mono">347</p>
          <p className="text-[11px] uppercase tracking-wider text-zinc-500 font-bold font-mono">Documents</p>
        </div>

        <div className="space-y-1">
          <p className="text-3xl font-extrabold text-white tracking-tight font-mono">18k</p>
          <p className="text-[11px] uppercase tracking-wider text-zinc-500 font-bold font-mono">Knowledge Graph</p>
        </div>

        <div className="space-y-1">
          <p className="text-3xl font-extrabold text-white tracking-tight font-mono">1,240</p>
          <p className="text-[11px] uppercase tracking-wider text-zinc-500 font-bold font-mono">Queries Today</p>
        </div>

        <div className="space-y-1">
          <p className="text-3xl font-extrabold text-white tracking-tight font-mono">18ms</p>
          <p className="text-[11px] uppercase tracking-wider text-zinc-500 font-bold font-mono">Average Response</p>
        </div>
      </div>

      {/* Three-Column Logs Section */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-8 pt-4 border-t border-zinc-900">
        {/* Column 1: Recent Activity */}
        <div className="space-y-4">
          <div>
            <h3 className="text-xs uppercase font-bold tracking-wider text-zinc-400">Recent Activity</h3>
            <p className="text-[10px] text-zinc-600 font-mono mt-0.5">Live vector crawl events</p>
          </div>
          <div className="space-y-3">
            {syncLogs.slice(0, 3).map((log, idx) => (
              <div key={idx} className="text-xs space-y-0.5">
                <span className="text-[9px] font-mono text-zinc-500 block">{log.type} &bull; {log.time}</span>
                <span className="text-zinc-300 font-medium block leading-relaxed">{log.action}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Column 2: Recent Uploads */}
        <div className="space-y-4">
          <div>
            <h3 className="text-xs uppercase font-bold tracking-wider text-zinc-400">Recent Uploads</h3>
            <p className="text-[10px] text-zinc-600 font-mono mt-0.5">Recently indexed documents</p>
          </div>
          <div className="space-y-3">
            {recentUploads.map((up, idx) => (
              <div key={idx} className="text-xs space-y-0.5">
                <span className="text-[9px] font-mono text-zinc-500 block">{up.type} &bull; {up.time}</span>
                <span className="text-zinc-300 font-medium block leading-relaxed">{up.name}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Column 3: Recent AI Answers */}
        <div className="space-y-4">
          <div>
            <h3 className="text-xs uppercase font-bold tracking-wider text-zinc-400">Recent AI Answers</h3>
            <p className="text-[10px] text-zinc-600 font-mono mt-0.5">Conversational highlights</p>
          </div>
          <div className="space-y-3">
            {recentAIAnswers.map((ai, idx) => (
              <div key={idx} className="text-xs space-y-0.5">
                <span className="text-[9px] font-mono text-indigo-400 block truncate font-semibold">&ldquo;{ai.query}&rdquo;</span>
                <span className="text-zinc-400 text-[11px] block leading-relaxed line-clamp-2">{ai.answer}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
