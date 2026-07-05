"use client";

import React, { useState, useEffect } from "react";
import { useQuery } from "@tanstack/react-query";
import { DocumentService } from "../services/DocumentService";
import { useAuth } from "../providers/AuthProvider";
import { DocumentUpload } from "./documents/DocumentUpload";
import { 
  FileText, 
  Search, 
  ArrowUpRight,
  Loader2,
  FileCode,
  FileSpreadsheet,
  Image as ImageIcon,
  Music,
  Video as VideoIcon,
  Archive,
  RefreshCw,
  Clock,
  CheckCircle,
  Tag,
  Trash2,
  X,
  File as FileIcon
} from "lucide-react";
import type { Document } from "../lib/types";

interface DocumentsProps {
  onSelectEntity?: (entity: any) => void;
}

export default function Documents({ onSelectEntity }: DocumentsProps) {
  const { activeWorkspace } = useAuth();
  const [filterQuery, setFilterQuery] = useState("");
  const [statusFilter, setStatusFilter] = useState<string>("all");
  const [typeFilter, setTypeFilter] = useState<string>("all");
  const [showUpload, setShowUpload] = useState(false);
  const [selectedDoc, setSelectedDoc] = useState<Document | null>(null);
  const [docChunks, setDocChunks] = useState<any[]>([]);
  const [loadingChunks, setLoadingChunks] = useState(false);

  // Fetch real documents for active workspace
  const { data: realDocs = [], isLoading, refetch } = useQuery({
    queryKey: ["documents", activeWorkspace?.id],
    queryFn: () => {
      if (!activeWorkspace) return Promise.resolve([]);
      return DocumentService.list(activeWorkspace.id);
    },
    enabled: !!activeWorkspace,
  });

  // Automatically poll active workspace documents if any are processing/ingesting
  useEffect(() => {
    if (!realDocs.length) return;
    const hasActiveIngestion = realDocs.some(
      (doc) => !["ready", "failed"].includes(doc.status)
    );

    if (hasActiveIngestion) {
      const interval = setInterval(() => {
        refetch();
      }, 3000); // Poll every 3s
      return () => clearInterval(interval);
    }
  }, [realDocs, refetch]);

  // Fetch chunks when a document is inspected
  const handleInspect = async (doc: Document) => {
    setSelectedDoc(doc);
    setLoadingChunks(true);
    try {
      const chunks = await DocumentService.listChunks(doc.id);
      setDocChunks(chunks || []);
    } catch (err) {
      console.error("Failed to load chunks:", err);
      setDocChunks([]);
    } finally {
      setLoadingChunks(false);
    }
  };

  const handleDelete = async (docId: string) => {
    if (!window.confirm("Are you sure you want to delete this document?")) return;
    try {
      await DocumentService.delete(docId);
      refetch();
      if (selectedDoc?.id === docId) {
        setSelectedDoc(null);
      }
    } catch (err) {
      console.error("Delete failed:", err);
    }
  };

  // Get file category based on extension
  const getFileCategory = (filename: string): string => {
    const ext = filename.split(".").pop()?.toLowerCase() || "";
    if (["pdf", "docx", "doc", "txt", "rtf", "md"].includes(ext)) return "document";
    if (["csv", "xls", "xlsx"].includes(ext)) return "spreadsheet";
    if (["ppt", "pptx"].includes(ext)) return "presentation";
    if (["py", "js", "ts", "java", "c", "cpp", "go", "rs", "html", "css", "json", "xml", "yaml", "sql"].includes(ext)) return "code";
    if (["png", "jpg", "jpeg", "webp", "svg"].includes(ext)) return "image";
    if (["mp3", "wav", "m4a"].includes(ext)) return "audio";
    if (["mp4", "mov", "avi"].includes(ext)) return "video";
    if (["zip"].includes(ext)) return "archive";
    return "other";
  };

  // Render correct file icon
  const renderFileIcon = (filename: string) => {
    const cat = getFileCategory(filename);
    switch (cat) {
      case "document": return <FileText className="w-5 h-5 text-indigo-400 shrink-0" />;
      case "spreadsheet": return <FileSpreadsheet className="w-5 h-5 text-emerald-400 shrink-0" />;
      case "code": return <FileCode className="w-5 h-5 text-amber-400 shrink-0" />;
      case "image": return <ImageIcon className="w-5 h-5 text-sky-400 shrink-0" />;
      case "audio": return <Music className="w-5 h-5 text-fuchsia-400 shrink-0" />;
      case "video": return <VideoIcon className="w-5 h-5 text-rose-400 shrink-0" />;
      case "archive": return <Archive className="w-5 h-5 text-zinc-400 shrink-0" />;
      default: return <FileIcon className="w-5 h-5 text-slate-400 shrink-0" />;
    }
  };

  // Status mapping to pipeline steps
  const pipelineSteps = [
    { key: "uploaded", label: "Uploaded" },
    { key: "stored", label: "Stored" },
    { key: "metadata", label: "Metadata" },
    { key: "extracted", label: "Extracted" },
    { key: "chunked", label: "Chunked" },
    { key: "embedding_pending", label: "Embedding" },
    { key: "ready", label: "Ready" }
  ];

  const getStepProgress = (status: string) => {
    if (status === "failed") return -1;
    const idx = pipelineSteps.findIndex(s => s.key === status);
    return idx === -1 ? 0 : idx + 1;
  };

  // Filtering logic
  const filteredDocs = realDocs.filter((doc) => {
    const matchesQuery = 
      doc.original_filename.toLowerCase().includes(filterQuery.toLowerCase()) ||
      (doc.title && doc.title.toLowerCase().includes(filterQuery.toLowerCase())) ||
      (doc.summary && doc.summary.toLowerCase().includes(filterQuery.toLowerCase()));

    const matchesStatus = statusFilter === "all" || doc.status === statusFilter;
    const matchesType = typeFilter === "all" || getFileCategory(doc.original_filename) === typeFilter;

    return matchesQuery && matchesStatus && matchesType;
  });

  return (
    <div className="flex gap-6 w-full py-4 min-h-[calc(100vh-8rem)]">
      {/* Main Files Grid Column */}
      <div className="flex-1 space-y-6 min-w-0">
        <div className="flex justify-between items-center bg-slate-900/40 border border-slate-800/80 p-6 rounded-2xl">
          <div>
            <h1 className="text-xl font-bold tracking-tight bg-gradient-to-r from-white to-slate-400 bg-clip-text text-transparent">
              Knowledge Repository
            </h1>
            <p className="text-xs text-slate-400 mt-1">
              Ingest, process, and structure enterprise files for context-aware RAG pipelines
            </p>
          </div>
          <button
            onClick={() => setShowUpload(!showUpload)}
            className="py-2.5 px-4 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl text-xs font-semibold shadow-lg shadow-indigo-600/20 cursor-pointer transition-all active:translate-y-[1px]"
          >
            {showUpload ? "Hide Upload Zone" : "Upload Files"}
          </button>
        </div>

        {showUpload && activeWorkspace && (
          <div className="p-6 bg-slate-900/60 border border-slate-800 rounded-2xl shadow-xl animate-in slide-in-from-top-4 duration-200">
            <DocumentUpload onUploadSuccess={() => refetch()} />
          </div>
        )}

        {/* Filters and search header */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 p-4 bg-slate-900/20 border border-slate-900 rounded-2xl">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
            <input
              type="text"
              value={filterQuery}
              onChange={(e) => setFilterQuery(e.target.value)}
              placeholder="Search indexed files..."
              className="w-full bg-slate-950/60 border border-slate-850 focus:border-indigo-500/80 rounded-xl pl-9 pr-4 py-2 text-xs text-white placeholder-slate-500 outline-none transition"
            />
          </div>

          <div className="flex items-center gap-3">
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="bg-slate-950/60 border border-slate-850 rounded-xl px-3 py-2 text-xs text-slate-300 outline-none focus:border-indigo-500/80 cursor-pointer"
            >
              <option value="all">All Statuses</option>
              <option value="ready">Ready</option>
              <option value="embedding_pending">Embedding Pending</option>
              <option value="chunked">Chunked</option>
              <option value="processing">Processing</option>
              <option value="failed">Failed</option>
            </select>

            <select
              value={typeFilter}
              onChange={(e) => setTypeFilter(e.target.value)}
              className="bg-slate-950/60 border border-slate-850 rounded-xl px-3 py-2 text-xs text-slate-300 outline-none focus:border-indigo-500/80 cursor-pointer"
            >
              <option value="all">All File Types</option>
              <option value="document">Documents</option>
              <option value="spreadsheet">Spreadsheets</option>
              <option value="code">Source Code</option>
              <option value="image">Images</option>
              <option value="audio">Audio</option>
              <option value="video">Video</option>
              <option value="archive">Archives</option>
            </select>
          </div>
        </div>

        {/* Documents Grid */}
        {isLoading ? (
          <div className="flex items-center justify-center p-20">
            <Loader2 className="h-8 w-8 animate-spin text-indigo-500" />
          </div>
        ) : filteredDocs.length === 0 ? (
          <div className="text-center p-20 border border-slate-900 rounded-2xl bg-slate-950/20 text-slate-400 italic">
            No documents found matching the criteria. Click "Upload Files" to ingest resources.
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {filteredDocs.map((doc) => {
              const progress = getStepProgress(doc.status);
              const isProcessing = progress > 0 && progress < 7;
              
              return (
                <div 
                  key={doc.id}
                  onClick={() => handleInspect(doc)}
                  className={`flex flex-col justify-between p-5 rounded-2xl border transition-all duration-200 cursor-pointer hover:translate-y-[-2px] hover:shadow-lg ${
                    selectedDoc?.id === doc.id
                      ? "border-indigo-500/80 bg-indigo-950/10 shadow-md shadow-indigo-500/5"
                      : "border-slate-850 bg-slate-900/30 hover:border-slate-800 hover:bg-slate-900/50"
                  }`}
                >
                  <div className="flex items-start justify-between gap-4 min-w-0">
                    <div className="flex items-center gap-3 min-w-0">
                      {renderFileIcon(doc.original_filename)}
                      <div className="min-w-0">
                        <span className="block font-semibold text-slate-200 truncate">{doc.original_filename}</span>
                        <span className="block text-[10px] text-slate-500 mt-1 font-mono uppercase tracking-wider">
                          {(doc.file_size / (1024 * 1024)).toFixed(3)} MB • {doc.mime_type.split("/").pop()}
                        </span>
                      </div>
                    </div>
                    
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        handleDelete(doc.id);
                      }}
                      className="p-1.5 hover:bg-slate-950 border border-slate-850 hover:border-red-900/50 hover:text-red-400 rounded-lg transition-colors cursor-pointer text-slate-500"
                    >
                      <Trash2 className="w-3.5 h-3.5" />
                    </button>
                  </div>

                  {/* Summary/Description snippet */}
                  <p className="text-xs text-slate-400 mt-3 line-clamp-2 leading-relaxed">
                    {doc.summary || doc.description || "Ingestion pipeline analyzing document structures..."}
                  </p>

                  {/* Status Bar */}
                  <div className="mt-4 pt-3 border-t border-slate-900/50">
                    <div className="flex items-center justify-between text-[9px] font-mono text-slate-500 mb-1.5">
                      <span>Status:</span>
                      {doc.status === "ready" && (
                        <span className="text-emerald-400 flex items-center gap-1">
                          <CheckCircle className="w-3 h-3" /> READY
                        </span>
                      )}
                      {doc.status === "failed" && (
                        <span className="text-red-400 font-bold">FAILED</span>
                      )}
                      {isProcessing && (
                        <span className="text-indigo-400 flex items-center gap-1 font-semibold animate-pulse">
                          <Clock className="w-3 h-3 animate-spin" /> {doc.status.toUpperCase()}
                        </span>
                      )}
                    </div>
                    <div className="w-full bg-slate-950 rounded-full h-1 overflow-hidden flex gap-0.5">
                      {pipelineSteps.map((step, sIdx) => {
                        let stepColor = "bg-slate-900";
                        if (doc.status === "failed") {
                          stepColor = "bg-red-950/60";
                        } else if (progress >= sIdx + 1) {
                          stepColor = sIdx === 6 ? "bg-emerald-500" : "bg-indigo-500";
                        }
                        return (
                          <div 
                            key={step.key} 
                            className={`flex-1 h-1 transition-colors duration-300 ${stepColor}`} 
                            title={step.label}
                          />
                        );
                      })}
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* Details / Inspection Panel Column */}
      {selectedDoc && (
        <div className="w-96 bg-slate-900/60 border border-slate-800 rounded-2xl p-6 flex flex-col justify-between max-h-[calc(100vh-8rem)] sticky top-24 overflow-y-auto animate-in slide-in-from-right-4 duration-200">
          <div className="space-y-6">
            <div className="flex items-start justify-between pb-4 border-b border-slate-800">
              <div className="flex items-center gap-3 min-w-0">
                {renderFileIcon(selectedDoc.original_filename)}
                <div className="min-w-0">
                  <h3 className="text-sm font-bold text-slate-200 truncate">{selectedDoc.original_filename}</h3>
                  <span className="text-[10px] font-mono text-slate-500">Document Inspector</span>
                </div>
              </div>
              <button 
                onClick={() => setSelectedDoc(null)}
                className="p-1 hover:bg-slate-950 border border-slate-850 rounded-lg text-slate-500 hover:text-slate-350 cursor-pointer"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            {/* Ingestion Profile Summary */}
            <div className="space-y-3">
              <h4 className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Asset Properties</h4>
              <div className="bg-slate-950 border border-slate-850 rounded-xl p-4 space-y-2 text-[11px] font-mono text-slate-300">
                <div className="flex justify-between"><span className="text-slate-500">Checksum:</span><span className="truncate max-w-xs">{selectedDoc.checksum.substring(0, 16)}...</span></div>
                <div className="flex justify-between"><span className="text-slate-500">MIME Type:</span><span>{selectedDoc.mime_type}</span></div>
                <div className="flex justify-between"><span className="text-slate-500">Size:</span><span>{(selectedDoc.file_size / (1024 * 1024)).toFixed(3)} MB</span></div>
                <div className="flex justify-between"><span className="text-slate-500">Language:</span><span className="uppercase">{selectedDoc.language || "Unknown"}</span></div>
                <div className="flex justify-between"><span className="text-slate-500">Version:</span><span>v{selectedDoc.current_version}</span></div>
                {selectedDoc.page_count && (
                  <div className="flex justify-between"><span className="text-slate-500">Page/Sheet Count:</span><span>{selectedDoc.page_count}</span></div>
                )}
              </div>
            </div>

            {/* AI Summary Block */}
            <div className="space-y-3">
              <h4 className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Document Abstract</h4>
              <div className="p-4 bg-slate-900 border border-slate-850 rounded-xl text-xs text-slate-300 leading-relaxed max-h-40 overflow-y-auto">
                {selectedDoc.summary || "Summary text is being generated by the pipeline..."}
              </div>
            </div>

            {/* Semantic Chunks Block */}
            <div className="space-y-3">
              <div className="flex justify-between items-center">
                <h4 className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Indexed Chunks</h4>
                {loadingChunks && <Loader2 className="w-3.5 h-3.5 text-indigo-400 animate-spin" />}
              </div>
              <div className="space-y-2.5 max-h-60 overflow-y-auto pr-1">
                {loadingChunks ? (
                  <div className="text-center py-6 text-[11px] text-slate-500">Loading document slices...</div>
                ) : docChunks.length === 0 ? (
                  <div className="text-center py-6 text-[11px] text-slate-500 italic">No semantic slices generated yet.</div>
                ) : (
                  docChunks.map((chunk, cIdx) => (
                    <div key={chunk.id} className="p-3 bg-slate-950/80 border border-slate-850 rounded-xl space-y-1.5 text-[11px]">
                      <div className="flex justify-between items-center text-[10px] font-mono text-slate-500 pb-1 border-b border-slate-900">
                        <span>Chunk #{chunk.chunk_index + 1}</span>
                        <span>{chunk.token_count} Tokens</span>
                      </div>
                      <p className="text-slate-300 font-sans leading-relaxed line-clamp-3">
                        {chunk.content}
                      </p>
                      {chunk.chunk_metadata?.section && (
                        <div className="text-[9px] font-mono text-indigo-400 pt-1">
                          Section: {chunk.chunk_metadata.section}
                        </div>
                      )}
                    </div>
                  ))
                )}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
