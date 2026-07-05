"use client";

import React, { useEffect, useState } from 'react';
import { 
  Slack, 
  Github, 
  HardDrive, 
  CheckCircle2, 
  RefreshCw, 
  Settings2
} from 'lucide-react';
import { getIntegrations, IntegrationItem } from '../services/integrationsService';

export default function IntegrationsControl() {
  const [integrations, setIntegrations] = useState<IntegrationItem[]>([]);

  useEffect(() => {
    getIntegrations().then(setIntegrations);
  }, []);

  const iconConfig: Record<string, { icon: React.ComponentType<{ className?: string }>; iconColor: string }> = {
    slack: { icon: Slack, iconColor: 'text-pink-400 bg-pink-950/20 border-pink-900/30' },
    github: { icon: Github, iconColor: 'text-indigo-400 bg-indigo-950/20 border-indigo-900/30' },
    drive: { icon: HardDrive, iconColor: 'text-sky-400 bg-sky-950/20 border-sky-900/30' },
  };

  return (
    <div className="space-y-4 max-w-5xl mx-auto w-full py-2">
      <div className="flex justify-between items-center mb-2">
        <div>
          <h2 className="text-sm font-semibold text-white tracking-tight">Active Connectors</h2>
          <p className="text-xs text-zinc-500 mt-0.5 font-sans">Manage pipeline streams synchronizing external platform structures</p>
        </div>
        <button className="px-3 py-1.5 bg-zinc-900 border border-zinc-800 rounded-lg text-xs font-semibold text-zinc-300 hover:text-white transition flex items-center gap-1.5 cursor-pointer">
          <Settings2 className="w-3.5 h-3.5" />
          System Settings
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {integrations.map((integ) => {
          const config = iconConfig[integ.id] || { icon: HardDrive, iconColor: 'text-zinc-400 bg-zinc-950/30 border-zinc-900/50' };
          const Icon = config.icon;
          return (
            <div key={integ.id} className="p-4 bg-zinc-900/40 border border-zinc-800/80 rounded-xl flex flex-col justify-between min-h-[190px] space-y-3">
              <div>
                {/* Header */}
                <div className="flex justify-between items-start mb-2">
                  <div className={`w-8 h-8 rounded-lg border flex items-center justify-center ${config.iconColor}`}>
                    <Icon className="w-4.5 h-4.5" />
                  </div>
                  {integ.status === 'active' ? (
                    <span className="px-2 py-0.5 rounded-full text-[9px] font-mono bg-emerald-950 text-emerald-400 border border-emerald-900/50 flex items-center gap-1">
                      <CheckCircle2 className="w-2.5 h-2.5" />
                      Active
                    </span>
                  ) : (
                    <span className="px-2 py-0.5 rounded-full text-[9px] font-mono bg-amber-950 text-amber-400 border border-amber-900/50 flex items-center gap-1">
                      <RefreshCw className="w-2.5 h-2.5 animate-spin" />
                      Syncing
                    </span>
                  )}
                </div>

                {/* Details */}
                <h3 className="text-xs font-bold text-white mb-1">{integ.name}</h3>
                <p className="text-[11px] text-zinc-400 leading-normal line-clamp-2">{integ.desc}</p>
              </div>

              {/* Ingest Stats */}
              <div className="pt-2 border-t border-zinc-900 grid grid-cols-3 gap-2 text-center">
                <div>
                  <span className="text-[8px] text-zinc-600 block uppercase font-mono">Volume</span>
                  <span className="text-[10px] font-semibold text-zinc-300">{Object.values(integ.stats)[0]}</span>
                </div>
                <div>
                  <span className="text-[8px] text-zinc-600 block uppercase font-mono">Activity</span>
                  <span className="text-[10px] font-semibold text-zinc-300">{Object.values(integ.stats)[1]}</span>
                </div>
                <div>
                  <span className="text-[8px] text-zinc-600 block uppercase font-mono">Interval</span>
                  <span className="text-[10px] font-semibold text-zinc-300">{Object.values(integ.stats)[2]}</span>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
