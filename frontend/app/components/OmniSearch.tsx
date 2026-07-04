"use client";

import React, { useState } from 'react';
import { 
  Search as SearchIcon, 
  Sparkles, 
  ArrowUpRight,
  ChevronRight,
  User, 
  FolderGit2, 
  FileText, 
  Cpu, 
  Calendar, 
  Layers3, 
  Network
} from 'lucide-react';
import { Entity } from '../mockData';
import { querySearch } from '../services/searchService';

interface OmniSearchProps {
  onSelectEntity: (entity: Entity) => void;
}

export default function OmniSearch({ onSelectEntity }: OmniSearchProps) {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<Entity[]>([]);
  const [aiSummary, setAiSummary] = useState('');
  const [recentQueries, setRecentQueries] = useState<string[]>([
    "Lead engineer of Payments 2.0",
    "Onboarding manual guide",
    "Project Atlas specs"
  ]);

  const suggestedQueries = [
    "Who worked on Project Atlas?",
    "What technologies are used in Payments 2.0?",
    "Summarize everything about our onboarding process.",
    "Show every document related to authentication."
  ];

  const handleSearch = async (val: string) => {
    setQuery(val);
    if (!val.trim()) {
      setResults([]);
      setAiSummary('');
      return;
    }
    
    // Add to recent queries
    if (!recentQueries.includes(val)) {
      setRecentQueries(prev => [val, ...prev.slice(0, 3)]);
    }

    try {
      const found = await querySearch(val);
      setResults(found);

      const valLower = val.toLowerCase();
      if (valLower.includes('atlas') || valLower.includes('search')) {
        setAiSummary("Project Atlas is the next-generation semantic search mapping system built to synchronize cloud enterprise file repositories. Principal PM Alex Rivera handles product features, while Jane Doe advises on technical distributed specs. Sync updates are held bi-weekly.");
      } else if (valLower.includes('payments') || valLower.includes('billing')) {
        setAiSummary("Payments 2.0 covers core billing checkout engine updates. Lead Architect Jane Doe manages the TypeScript and Rust FFI hooks codebases, secured by OAuth2 policies drafted by Sarah Chen.");
      } else if (valLower.includes('onboarding') || valLower.includes('setup')) {
        setAiSummary("The Company Onboarding Playbook is indexed from Notion, authored by Principal PM Alex Rivera. It serves as a guide for engineering division setups, covering credentials and community guidelines.");
      } else if (valLower.includes('auth') || valLower.includes('security')) {
        setAiSummary("Sarah Chen (Senior Security Specialist) authored the Enterprise Authentication Specs stored in Google Drive. This document secures the billing checkout flows of Payments 2.0.");
      } else {
        setAiSummary(`I found ${found.length} semantic connections matching "${val}" inside the Acme Corp directory. Select any entity block below to inspect its relationship paths.`);
      }
    } catch (err) {
      console.error(err);
    }
  };

  const selectSuggestion = (s: string) => {
    handleSearch(s);
  };

  const getIcon = (type: string) => {
    switch (type) {
      case 'person': return User;
      case 'project': return FolderGit2;
      case 'document': return FileText;
      case 'technology': return Cpu;
      case 'meeting': return Calendar;
      case 'department': return Layers3;
      case 'integration': return Network;
      default: return FileText;
    }
  };

  // Grouped search categories
  const relatedDocs = results.filter(e => e.type === 'document');
  const people = results.filter(e => e.type === 'person');
  const projects = results.filter(e => e.type === 'project');
  const sources = results.filter(e => e.type === 'integration' || e.type === 'technology');

  return (
    <div className="flex-1 max-w-4xl mx-auto py-8 space-y-8">
      {/* Semantic Search Title Headers */}
      <div className="space-y-2 text-center md:text-left">
        <div className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-indigo-950/40 border border-indigo-900/40 text-[10px] text-indigo-400 font-mono font-medium">
          <Sparkles className="w-3.5 h-3.5" />
          Semantic Search
        </div>
        <h2 className="text-3xl font-extrabold text-white tracking-tight">
          Semantic Search
        </h2>
        <p className="text-sm text-zinc-500 max-w-xl">
          Ask Anything
        </p>
      </div>

      {/* Search Input Bar */}
      <div className="relative">
        <div className="absolute inset-y-0 left-4 flex items-center pointer-events-none">
          <SearchIcon className="h-5 w-5 text-zinc-600" />
        </div>
        <input
          type="text"
          value={query}
          onChange={(e) => handleSearch(e.target.value)}
          placeholder="Ask a natural language query... e.g. Who worked on Project Atlas?"
          className="w-full bg-zinc-900/60 border border-zinc-800 focus:border-indigo-500/80 focus:ring-1 focus:ring-indigo-500/30 rounded-2xl pl-12 pr-4 py-4 text-xs text-white placeholder-zinc-500 outline-none transition-all duration-300 shadow-[0_4px_30px_rgba(0,0,0,0.4)]"
        />
        {query && (
          <button 
            onClick={() => handleSearch('')}
            className="absolute right-4 top-1/2 -translate-y-1/2 text-xs text-zinc-500 hover:text-zinc-300 font-mono cursor-pointer"
          >
            Clear
          </button>
        )}
      </div>

      {/* Results dossier view */}
      {query ? (
        <div className="space-y-6 pt-4 border-t border-zinc-900">
          {/* AI Summary Block */}
          {aiSummary && (
            <div className="p-5 rounded-2xl bg-zinc-900/20 border border-zinc-900 space-y-2">
              <span className="text-[10px] text-indigo-400 font-mono font-bold uppercase tracking-wider block">AI Summary</span>
              <p className="text-xs text-zinc-300 leading-relaxed font-sans">{aiSummary}</p>
            </div>
          )}

          {/* Grouped results grids */}
          {results.length === 0 ? (
            <div className="p-8 rounded-2xl bg-zinc-900/10 border border-zinc-900 text-center space-y-2">
              <p className="text-xs text-zinc-500">No nodes or relations found matching &ldquo;{query}&rdquo;.</p>
              <p className="text-[10px] text-zinc-600">Try asking about &ldquo;Atlas&rdquo;, &ldquo;Payments&rdquo;, or &ldquo;Authentication&rdquo;.</p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Column 1: Related Docs & Sources */}
              <div className="space-y-6">
                {/* Related Documents */}
                <div className="space-y-3">
                  <h3 className="text-xs font-bold text-zinc-400 uppercase tracking-wider">Related Docs</h3>
                  <div className="space-y-2">
                    {relatedDocs.length === 0 ? (
                      <p className="text-xs text-zinc-600 italic">No document links matched.</p>
                    ) : (
                      relatedDocs.map((doc) => (
                        <button
                          key={doc.id}
                          onClick={() => onSelectEntity(doc)}
                          className="w-full text-left p-3 rounded-xl border border-zinc-900 bg-zinc-900/20 hover:bg-zinc-900/60 hover:border-zinc-800 transition flex items-center justify-between group cursor-pointer"
                        >
                          <div className="flex items-center gap-2">
                            <FileText className="w-3.5 h-3.5 text-zinc-500 group-hover:text-indigo-400 transition" />
                            <span className="text-xs text-zinc-300 font-medium group-hover:text-white truncate">{doc.name}</span>
                          </div>
                          <ArrowUpRight className="w-3 h-3 text-zinc-650 group-hover:text-indigo-400" />
                        </button>
                      ))
                    )}
                  </div>
                </div>

                {/* Sources & Tech */}
                <div className="space-y-3">
                  <h3 className="text-xs font-bold text-zinc-400 uppercase tracking-wider">Sources & Technologies</h3>
                  <div className="space-y-2">
                    {sources.length === 0 ? (
                      <p className="text-xs text-zinc-600 italic">No source connector links matched.</p>
                    ) : (
                      sources.map((src) => {
                        const Icon = getIcon(src.type);
                        return (
                          <button
                            key={src.id}
                            onClick={() => onSelectEntity(src)}
                            className="w-full text-left p-3 rounded-xl border border-zinc-900 bg-zinc-900/20 hover:bg-zinc-900/60 hover:border-zinc-800 transition flex items-center justify-between group cursor-pointer"
                          >
                            <div className="flex items-center gap-2">
                              <Icon className="w-3.5 h-3.5 text-zinc-500 group-hover:text-indigo-400 transition" />
                              <span className="text-xs text-zinc-300 font-medium group-hover:text-white truncate">{src.name}</span>
                            </div>
                            <ArrowUpRight className="w-3 h-3 text-zinc-650 group-hover:text-indigo-400" />
                          </button>
                        );
                      })
                    )}
                  </div>
                </div>
              </div>

              {/* Column 2: People & Projects */}
              <div className="space-y-6">
                {/* Connected People */}
                <div className="space-y-3">
                  <h3 className="text-xs font-bold text-zinc-400 uppercase tracking-wider">People</h3>
                  <div className="space-y-2">
                    {people.length === 0 ? (
                      <p className="text-xs text-zinc-600 italic">No employees matched.</p>
                    ) : (
                      people.map((p) => (
                        <button
                          key={p.id}
                          onClick={() => onSelectEntity(p)}
                          className="w-full text-left p-3 rounded-xl border border-zinc-900 bg-zinc-900/20 hover:bg-zinc-900/60 hover:border-zinc-800 transition flex items-center justify-between group cursor-pointer"
                        >
                          <div className="flex items-center gap-2">
                            <User className="w-3.5 h-3.5 text-zinc-500 group-hover:text-indigo-400 transition" />
                            <span className="text-xs text-zinc-300 font-medium group-hover:text-white truncate">{p.name}</span>
                          </div>
                          <ArrowUpRight className="w-3 h-3 text-zinc-650 group-hover:text-indigo-400" />
                        </button>
                      ))
                    )}
                  </div>
                </div>

                {/* Connected Projects */}
                <div className="space-y-3">
                  <h3 className="text-xs font-bold text-zinc-400 uppercase tracking-wider">Projects</h3>
                  <div className="space-y-2">
                    {projects.length === 0 ? (
                      <p className="text-xs text-zinc-600 italic">No projects matched.</p>
                    ) : (
                      projects.map((proj) => (
                        <button
                          key={proj.id}
                          onClick={() => onSelectEntity(proj)}
                          className="w-full text-left p-3 rounded-xl border border-zinc-900 bg-zinc-900/20 hover:bg-zinc-900/60 hover:border-zinc-800 transition flex items-center justify-between group cursor-pointer"
                        >
                          <div className="flex items-center gap-2">
                            <FolderGit2 className="w-3.5 h-3.5 text-zinc-500 group-hover:text-indigo-400 transition" />
                            <span className="text-xs text-zinc-300 font-medium group-hover:text-white truncate">{proj.name}</span>
                          </div>
                          <ArrowUpRight className="w-3 h-3 text-zinc-650 group-hover:text-indigo-400" />
                        </button>
                      ))
                    )}
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      ) : (
        /* Suggested and Recent queries grid */
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Suggested Queries */}
          <div className="space-y-3">
            <span className="text-[10px] uppercase font-bold tracking-wider text-zinc-500 block font-mono">
              Suggested queries
            </span>
            <div className="space-y-2">
              {suggestedQueries.map((s, idx) => (
                <button
                  key={idx}
                  onClick={() => selectSuggestion(s)}
                  className="w-full text-left p-3.5 rounded-xl border border-zinc-905 bg-zinc-900/10 hover:bg-zinc-900/30 hover:border-zinc-800 transition flex items-center justify-between group cursor-pointer"
                >
                  <span className="text-xs text-zinc-400 group-hover:text-zinc-200 transition font-sans">
                    {s}
                  </span>
                  <ChevronRight className="w-4 h-4 text-zinc-600 group-hover:text-indigo-400 transition" />
                </button>
              ))}
            </div>
          </div>

          {/* Recent Queries */}
          <div className="space-y-3">
            <span className="text-[10px] uppercase font-bold tracking-wider text-zinc-500 block font-mono">
              Recent Queries
            </span>
            <div className="space-y-2">
              {recentQueries.map((s, idx) => (
                <button
                  key={idx}
                  onClick={() => selectSuggestion(s)}
                  className="w-full text-left p-3.5 rounded-xl border border-zinc-905 bg-zinc-900/10 hover:bg-zinc-900/30 hover:border-zinc-800 transition flex items-center justify-between group cursor-pointer"
                >
                  <span className="text-xs text-zinc-400 group-hover:text-zinc-200 transition font-sans truncate">
                    &ldquo;{s}&rdquo;
                  </span>
                  <ChevronRight className="w-4 h-4 text-zinc-600 group-hover:text-indigo-400 transition" />
                </button>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
