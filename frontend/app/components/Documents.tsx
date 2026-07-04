"use client";

import React, { useState, useEffect } from 'react';
import { 
  FileText, 
  Search, 
  ArrowUpRight,
  FileCode2,
  Cloud,
  FileUp
} from 'lucide-react';
import { Entity, getConnectedEntities } from '../mockData';
import { getDocuments } from '../services/documentsService';

interface DocumentsProps {
  onSelectEntity: (entity: Entity) => void;
}

export default function Documents({ onSelectEntity }: DocumentsProps) {
  const [filterQuery, setFilterQuery] = useState('');
  const [docs, setDocs] = useState<Entity[]>([]);
  const [notification, setNotification] = useState('');

  useEffect(() => {
    getDocuments().then(setDocs);
  }, []);

  const triggerMockUpload = (type: string) => {
    setNotification(`Mock Sync: Connecting file explorer to upload ${type}...`);
    setTimeout(() => {
      setNotification('');
    }, 3000);
  };

  const filteredDocs = docs.filter(doc => 
    doc.name.toLowerCase().includes(filterQuery.toLowerCase()) ||
    doc.details.toLowerCase().includes(filterQuery.toLowerCase()) ||
    (typeof doc.meta.author === 'string' && doc.meta.author.toLowerCase().includes(filterQuery.toLowerCase()))
  );

  return (
    <div className="space-y-10 flex-1 max-w-5xl mx-auto w-full py-4">
      {/* Notifications/Toast banner */}
      {notification && (
        <div className="p-3 bg-indigo-950/40 border border-indigo-900/40 rounded-xl text-indigo-400 text-xs font-mono animate-pulse">
          {notification}
        </div>
      )}

      {/* Top Upload Section */}
      <div className="space-y-4">
        <div>
          <h2 className="text-sm font-semibold text-white tracking-tight">Upload & Connectors</h2>
          <p className="text-xs text-zinc-500 mt-0.5 font-sans">Index custom formats or link cloud file storage vaults</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <button
            onClick={() => triggerMockUpload('PDF')}
            className="p-5 rounded-xl border border-zinc-900 bg-zinc-900/10 hover:bg-zinc-900/40 hover:border-zinc-800 transition flex items-center justify-between group cursor-pointer text-left"
          >
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-lg bg-red-950/30 border border-red-900/35 flex items-center justify-center">
                <FileUp className="w-4 h-4 text-red-400" />
              </div>
              <div>
                <span className="block text-xs font-bold text-white">Upload PDF</span>
                <span className="block text-[10px] text-zinc-500 font-sans mt-0.5">Vectorize whitepapers & forms</span>
              </div>
            </div>
            <ArrowUpRight className="w-4 h-4 text-zinc-600 group-hover:text-red-400 transition" />
          </button>

          <button
            onClick={() => triggerMockUpload('DOCX')}
            className="p-5 rounded-xl border border-zinc-900 bg-zinc-900/10 hover:bg-zinc-900/40 hover:border-zinc-800 transition flex items-center justify-between group cursor-pointer text-left"
          >
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-lg bg-indigo-950/30 border border-indigo-900/35 flex items-center justify-center">
                <FileCode2 className="w-4 h-4 text-indigo-400" />
              </div>
              <div>
                <span className="block text-xs font-bold text-white">Upload DOCX</span>
                <span className="block text-[10px] text-zinc-500 font-sans mt-0.5">Index text formats & manuals</span>
              </div>
            </div>
            <ArrowUpRight className="w-4 h-4 text-zinc-600 group-hover:text-indigo-400 transition" />
          </button>

          <button
            onClick={() => triggerMockUpload('Google Drive connection')}
            className="p-5 rounded-xl border border-zinc-900 bg-zinc-900/10 hover:bg-zinc-900/40 hover:border-zinc-800 transition flex items-center justify-between group cursor-pointer text-left"
          >
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-lg bg-emerald-950/30 border border-emerald-900/35 flex items-center justify-center">
                <Cloud className="w-4 h-4 text-emerald-400" />
              </div>
              <div>
                <span className="block text-xs font-bold text-white">Connect Google Drive</span>
                <span className="block text-[10px] text-zinc-500 font-sans mt-0.5">Continuous folder crawler sync</span>
              </div>
            </div>
            <ArrowUpRight className="w-4 h-4 text-zinc-600 group-hover:text-emerald-400 transition" />
          </button>
        </div>
      </div>

      {/* Recent Documents Table Section */}
      <div className="space-y-4 pt-6 border-t border-zinc-900">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <h2 className="text-sm font-semibold text-white tracking-tight">Recent Documents</h2>
            <p className="text-xs text-zinc-500 mt-0.5">Browse indexed company files catalog</p>
          </div>

          {/* Filter Input */}
          <div className="relative w-full md:w-72">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-zinc-500" />
            <input
              type="text"
              value={filterQuery}
              onChange={(e) => setFilterQuery(e.target.value)}
              placeholder="Filter documents..."
              className="w-full bg-zinc-900/40 border border-zinc-800 focus:border-indigo-500/80 rounded-xl pl-9 pr-4 py-2 text-xs text-white placeholder-zinc-500 outline-none transition"
            />
          </div>
        </div>

        {/* Documents Table */}
        <div className="overflow-hidden rounded-2xl border border-zinc-900 bg-zinc-950/40">
          <div className="overflow-x-auto">
            <table className="w-full border-collapse text-left text-xs">
              <thead>
                <tr className="border-b border-zinc-900 bg-zinc-900/10 text-zinc-500 uppercase tracking-wider font-mono font-bold">
                  <th className="p-4">Document Title</th>
                  <th className="p-4">Source connector</th>
                  <th className="p-4">Author</th>
                  <th className="p-4">Last Synced</th>
                  <th className="p-4 text-right">Relations</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-zinc-900/50">
                {filteredDocs.length === 0 ? (
                  <tr>
                    <td colSpan={5} className="p-8 text-center text-zinc-500 italic">
                      No documents found matching the filter query.
                    </td>
                  </tr>
                ) : (
                  filteredDocs.map((doc) => {
                    const connected = getConnectedEntities(doc.id);
                    return (
                      <tr 
                        key={doc.id}
                        className="hover:bg-zinc-900/25 transition group"
                      >
                        <td className="p-4 font-medium text-white max-w-xs">
                          <div className="flex items-center gap-2">
                            <FileText className="w-4 h-4 text-indigo-400 shrink-0" />
                            <div>
                              <span className="block truncate">{doc.name}</span>
                              <span className="block text-[10px] text-zinc-500 font-normal truncate mt-0.5">{doc.details}</span>
                            </div>
                          </div>
                        </td>
                        <td className="p-4">
                          <span className="px-2.5 py-1 rounded-md bg-zinc-900 border border-zinc-800 text-[10px] font-mono text-zinc-300">
                            {doc.meta.source || 'Internal'}
                          </span>
                        </td>
                        <td className="p-4 text-zinc-400">
                          {doc.meta.author || 'System'}
                        </td>
                        <td className="p-4 text-zinc-500 font-mono">
                          {doc.meta.lastUpdated || '2026-07-01'}
                        </td>
                        <td className="p-4 text-right">
                          <button
                            onClick={() => onSelectEntity(doc)}
                            className="px-3 py-1.5 rounded-lg bg-zinc-900 border border-zinc-800/80 hover:border-indigo-500/50 text-[11px] text-zinc-300 hover:text-white transition inline-flex items-center gap-1.5 cursor-pointer"
                          >
                            <span>{connected.length} links</span>
                            <ArrowUpRight className="w-3 h-3 text-zinc-500 group-hover:text-indigo-400 transition" />
                          </button>
                        </td>
                      </tr>
                    );
                  })
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}
