"use client";

import React, { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { DocumentService } from "../services/DocumentService";
import { useAuth } from "../providers/AuthProvider";
import { DocumentUpload } from "./documents/DocumentUpload";
import { Entity, getConnectedEntities } from "../mockData";
import { 
  FileText, 
  Search, 
  ArrowUpRight,
  Loader2,
  FileDown
} from "lucide-react";

interface DocumentsProps {
  onSelectEntity: (entity: Entity) => void;
}

export default function Documents({ onSelectEntity }: DocumentsProps) {
  const { activeWorkspace } = useAuth();
  const [filterQuery, setFilterQuery] = useState("");
  const [showUpload, setShowUpload] = useState(false);

  // Fetch real documents for active workspace
  const { data: realDocs = [], isLoading, refetch } = useQuery({
    queryKey: ["documents", activeWorkspace?.id],
    queryFn: () => {
      if (!activeWorkspace) return Promise.resolve([]);
      return DocumentService.list(activeWorkspace.id);
    },
    enabled: !!activeWorkspace,
  });

  // Map real document entities to the UI model
  const mappedRealDocs: Entity[] = realDocs.map((doc) => ({
    id: doc.id,
    name: doc.original_filename,
    type: "document",
    details: doc.summary || doc.description || "Ingestion pipeline analyzing document structures...",
    meta: {
      source: "Supabase Storage",
      author: "Authorized User",
      lastUpdated: new Date(doc.updated_at).toLocaleDateString(),
      status: doc.status,
      version: `v${doc.current_version}`,
      size: `${(doc.file_size / (1024 * 1024)).toFixed(3)} MB`
    }
  }));

  const filteredDocs = mappedRealDocs.filter(
    (doc) =>
      doc.name.toLowerCase().includes(filterQuery.toLowerCase()) ||
      doc.details.toLowerCase().includes(filterQuery.toLowerCase())
  );

  return (
    <div className="space-y-8 flex-1 max-w-5xl mx-auto w-full py-4">
      {/* Upload Toggle & Form Container */}
      <div className="space-y-4">
        <div className="flex justify-between items-center">
          <div>
            <h2 className="text-sm font-semibold text-white tracking-tight">Upload & Connectors</h2>
            <p className="text-xs text-zinc-500 mt-0.5 font-sans">Index custom formats or link cloud file storage vaults</p>
          </div>
          <button
            onClick={() => setShowUpload(!showUpload)}
            className="py-2 px-4 bg-indigo-650 hover:bg-indigo-600 text-white rounded-xl text-xs font-semibold shadow-md shadow-indigo-650/15 cursor-pointer transition-all active:translate-y-[1px]"
          >
            {showUpload ? "Hide Upload Panel" : "Upload Document"}
          </button>
        </div>

        {showUpload && activeWorkspace && (
          <div className="p-6 bg-zinc-900/40 border border-zinc-850 rounded-2xl animate-in fade-in duration-200">
            <DocumentUpload onUploadSuccess={() => refetch()} />
          </div>
        )}
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
                  <th className="p-4">Version</th>
                  <th className="p-4">Last Synced</th>
                  <th className="p-4 text-right">Details</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-zinc-900/50">
                {isLoading ? (
                  <tr>
                    <td colSpan={5} className="p-8 text-center text-zinc-500">
                      <div className="flex items-center justify-center gap-2">
                        <Loader2 className="h-4 w-4 animate-spin text-indigo-500" />
                        Fetching active workspace documents...
                      </div>
                    </td>
                  </tr>
                ) : filteredDocs.length === 0 ? (
                  <tr>
                    <td colSpan={5} className="p-8 text-center text-zinc-500 italic">
                      No documents found in this workspace. Upload some files to begin!
                    </td>
                  </tr>
                ) : (
                  filteredDocs.map((doc) => {
                    const connected = getConnectedEntities(doc.id);
                    const docStatus = doc.meta.status;
                    return (
                      <tr 
                        key={doc.id}
                        className="hover:bg-zinc-900/25 transition group"
                      >
                        <td className="p-4 font-medium text-white max-w-xs">
                          <div className="flex items-center gap-3">
                            <FileText className="w-4.5 h-4.5 text-indigo-400 shrink-0" />
                            <div className="min-w-0">
                              <span className="block truncate font-semibold text-slate-200">{doc.name}</span>
                              <span className="block text-[10px] text-zinc-500 font-normal truncate mt-0.5">
                                {doc.details}
                              </span>
                            </div>
                          </div>
                        </td>
                        <td className="p-4">
                          <span className="px-2 py-0.5 rounded-md bg-zinc-900 border border-zinc-850 text-[10px] font-mono text-zinc-400">
                            {doc.meta.source}
                          </span>
                        </td>
                        <td className="p-4 text-zinc-400 font-mono">
                          {doc.meta.version}
                        </td>
                        <td className="p-4 text-zinc-500 font-mono">
                          {doc.meta.lastUpdated}
                        </td>
                        <td className="p-4 text-right">
                          <button
                            onClick={() => onSelectEntity(doc)}
                            className="px-3 py-1.5 rounded-lg bg-zinc-900 border border-zinc-800/80 hover:border-indigo-500/50 text-[11px] text-zinc-350 hover:text-white transition inline-flex items-center gap-1.5 cursor-pointer"
                          >
                            <span>Inspect</span>
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
