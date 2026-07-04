"use client";

import React, { useState } from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import Sidebar from './components/Sidebar';
import OmniSearch from './components/OmniSearch';
import Graph from './components/Graph';
import Dashboard from './components/Dashboard';
import IntegrationsControl from './components/IntegrationsControl';
import EntityDetails from './components/EntityDetails';
import CompanyAI from './components/CompanyAI';
import Documents from './components/Documents';
import SettingsView from './components/Settings';
import AnalyticsView from './components/Analytics';
import { Entity } from './mockData';

const queryClient = new QueryClient();

export default function Page() {
  const [currentTab, setCurrentTab] = useState('company-ai');
  const [selectedEntity, setSelectedEntity] = useState<Entity | null>(null);

  const syncStatusMap: Record<string, string> = {
    dashboard: "Enterprise performance: 99.8% precision",
    'company-ai': "AI conversational assistant (Active)",
    documents: "Scanned and indexed files directory",
    search: "Indexing completed (3,410 nodes matched)",
    graph: "Neural relational nodes visualizer (Live)",
    integrations: "Google Drive, Slack & GitHub active",
    analytics: "Ingestion logs and search performance dashboard",
    settings: "Vector search parameters and API keys configuration"
  };

  const handleSelectEntity = (entity: Entity) => {
    setSelectedEntity(entity);
  };

  const getBreadcrumb = (tab: string) => {
    if (tab === 'company-ai') return 'Company AI';
    if (tab === 'graph') return 'Knowledge Graph';
    if (tab === 'search') return 'Semantic Search';
    return tab.charAt(0).toUpperCase() + tab.slice(1);
  };

  return (
    <QueryClientProvider client={queryClient}>
      <div className="flex bg-zinc-950 text-zinc-100 min-h-screen">
        {/* Navigation Sidebar */}
        <Sidebar 
          currentTab={currentTab} 
          setCurrentTab={setCurrentTab} 
          syncStatus={syncStatusMap[currentTab] || "BrainOS Online"} 
        />

        {/* Core Workspace Dashboard */}
        <main className="flex-1 flex flex-col min-h-screen">
          {/* Header Panel */}
          <header className="border-b border-zinc-900 bg-zinc-950/60 sticky top-0 z-20 backdrop-blur-md px-8 py-4 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-indigo-500"></span>
              <span className="text-xs font-mono text-zinc-300 font-semibold tracking-wider">
                BrainOS / {getBreadcrumb(currentTab)}
              </span>
            </div>
            <div className="flex items-center gap-4">
              <span className="text-xs text-zinc-500 font-mono">
                CPU: <span className="text-emerald-400">0.02%</span>
              </span>
              <div className="h-4 w-px bg-zinc-900"></div>
              <span className="text-xs text-zinc-500 font-mono">
                Nodes Indexed: <span className="text-indigo-400">3,410</span>
              </span>
            </div>
          </header>

          {/* Canvas Area */}
          <div className="flex-1 p-8 flex flex-col justify-start">
            {currentTab === 'dashboard' && (
              <Dashboard />
            )}

            {currentTab === 'company-ai' && (
              <CompanyAI onSelectEntity={handleSelectEntity} />
            )}

            {currentTab === 'documents' && (
              <Documents onSelectEntity={handleSelectEntity} />
            )}

            {currentTab === 'search' && (
              <OmniSearch onSelectEntity={handleSelectEntity} />
            )}
            
            {currentTab === 'graph' && (
              <div className="space-y-6">
                <div>
                  <h2 className="text-sm font-semibold text-white tracking-tight">Enterprise Knowledge Graph</h2>
                  <p className="text-xs text-zinc-500 mt-0.5">Explore semantic linkages and relationship structures between organizational entities.</p>
                </div>
                <Graph onSelectEntity={handleSelectEntity} selectedEntity={selectedEntity} />
              </div>
            )}

            {currentTab === 'integrations' && (
              <IntegrationsControl />
            )}

            {currentTab === 'analytics' && (
              <AnalyticsView />
            )}

            {currentTab === 'settings' && (
              <SettingsView />
            )}
          </div>
        </main>

        {/* Relational Entity Detail Sidebar Panel */}
        {selectedEntity && (
          <EntityDetails 
            entity={selectedEntity} 
            onClose={() => setSelectedEntity(null)} 
            onSelectEntity={handleSelectEntity}
          />
        )}
      </div>
    </QueryClientProvider>
  );
}
