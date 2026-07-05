"use client";

import React, { useState, useRef } from "react";
import { useAuth } from "../../providers/AuthProvider";
import { DocumentService } from "../../services/DocumentService";
import { useQueryClient } from "@tanstack/react-query";
import { UploadCloud, File, X, AlertCircle, CheckCircle2, Loader2, RefreshCw } from "lucide-react";

interface UploadFileItem {
  id: string;
  file: File;
  progress: number;
  status: "idle" | "uploading" | "completed" | "failed" | "cancelled";
  error?: string;
  abortController?: AbortController;
}

export function DocumentUpload({
  folderId = null,
  kbId = null,
  onUploadSuccess,
}: {
  folderId?: string | null;
  kbId?: string | null;
  onUploadSuccess?: () => void;
}) {
  const { activeOrg, activeWorkspace } = useAuth();
  const queryClient = useQueryClient();
  const [filesList, setFilesList] = useState<UploadFileItem[]>([]);
  const [isDragOver, setIsDragOver] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const processUpload = async (item: UploadFileItem) => {
    if (!activeOrg || !activeWorkspace) return;

    // 1. Initial validation
    if (item.file.size > 100 * 1024 * 1024) {
      setFilesList((prev) =>
        prev.map((f) =>
          f.id === item.id
            ? { ...f, status: "failed", error: "File exceeds 100MB limit" }
            : f
        )
      );
      return;
    }

    const controller = new AbortController();
    setFilesList((prev) =>
      prev.map((f) =>
        f.id === item.id
          ? { ...f, status: "uploading", progress: 0, abortController: controller }
          : f
      )
    );

    try {
      // Direct upload if small (<2MB), otherwise upload in chunks
      if (item.file.size <= 2 * 1024 * 1024) {
        await DocumentService.upload(item.file, {
          organization_id: activeOrg.id,
          workspace_id: activeWorkspace.id,
          folder_id: folderId,
          knowledge_base_id: kbId,
        });
      } else {
        await DocumentService.uploadInChunks(
          item.file,
          {
            organization_id: activeOrg.id,
            workspace_id: activeWorkspace.id,
            folder_id: folderId,
            knowledge_base_id: kbId,
          },
          (progress) => {
            if (controller.signal.aborted) return;
            setFilesList((prev) =>
              prev.map((f) => (f.id === item.id ? { ...f, progress } : f))
            );
          }
        );
      }

      setFilesList((prev) =>
        prev.map((f) => (f.id === item.id ? { ...f, status: "completed", progress: 100 } : f))
      );

      queryClient.invalidateQueries({ queryKey: ["documents", activeWorkspace.id] });
      if (onUploadSuccess) onUploadSuccess();
    } catch (err: any) {
      if (controller.signal.aborted) {
        setFilesList((prev) =>
          prev.map((f) => (f.id === item.id ? { ...f, status: "cancelled", error: "Upload cancelled" } : f))
        );
        return;
      }
      setFilesList((prev) =>
        prev.map((f) => (f.id === item.id ? { ...f, status: "failed", error: err.detail || "Upload failed" } : f))
      );
    }
  };

  const handleFiles = (newFiles: FileList) => {
    const items: UploadFileItem[] = Array.from(newFiles).map((file) => ({
      id: crypto.randomUUID(),
      file,
      progress: 0,
      status: "idle",
    }));

    setFilesList((prev) => [...prev, ...items]);
    items.forEach((item) => {
      processUpload(item);
    });
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(true);
  };

  const handleDragLeave = () => {
    setIsDragOver(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
    if (e.dataTransfer.files.length > 0) {
      handleFiles(e.dataTransfer.files);
    }
  };

  const handleRemoveItem = (id: string) => {
    const item = filesList.find((f) => f.id === id);
    if (item?.abortController) {
      item.abortController.abort();
    }
    setFilesList((prev) => prev.filter((f) => f.id !== id));
  };

  const handleRetry = (item: UploadFileItem) => {
    processUpload(item);
  };

  return (
    <div className="space-y-4">
      <div
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={() => fileInputRef.current?.click()}
        className={`border border-dashed rounded-2xl p-8 text-center flex flex-col items-center justify-center cursor-pointer transition-all duration-200 ${
          isDragOver
            ? "border-indigo-500 bg-indigo-500/5 shadow-md shadow-indigo-500/5"
            : "border-slate-800 bg-slate-900/40 hover:border-slate-700/80 hover:bg-slate-900/60"
        }`}
      >
        <input
          type="file"
          ref={fileInputRef}
          onChange={(e) => e.target.files && handleFiles(e.target.files)}
          multiple
          className="hidden"
          accept=".pdf,.docx,.doc,.txt,.csv,.xls,.xlsx,.pptx,.ppt,.rtf,.md,.markdown,image/*,audio/*,video/*,.zip"
        />
        <div className="h-12 w-12 bg-slate-950/80 border border-slate-850 rounded-xl flex items-center justify-center mb-4 text-slate-400">
          <UploadCloud className="h-6 w-6" />
        </div>
        <p className="text-sm font-semibold text-slate-200">
          Drag and drop files here, or <span className="text-indigo-400 font-bold hover:underline">browse files</span>
        </p>
        <p className="text-xs text-slate-500 mt-2 leading-relaxed">
          Supports Documents (PDF, Word, TXT, MD, RTF), Tables (CSV, Excel), Slides, Images, Audio, Video, & ZIP
        </p>
      </div>

      {filesList.length > 0 && (
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-4 divide-y divide-slate-800/60 max-h-60 overflow-y-auto">
          {filesList.map((item) => (
            <div key={item.id} className="flex items-center justify-between py-3 first:pt-0 last:pb-0 gap-4">
              <div className="flex items-center gap-3 min-w-0 flex-1">
                <div className="h-9 w-9 bg-slate-950/80 border border-slate-850 rounded-lg flex items-center justify-center text-slate-400 shrink-0">
                  <File className="h-4.5 w-4.5" />
                </div>
                <div className="min-w-0 flex-1">
                  <p className="text-sm font-semibold text-slate-300 truncate mb-1">
                    {item.file.name}
                  </p>
                  <div className="flex items-center gap-2">
                    <span className="text-[10px] text-slate-500 font-mono">
                      {(item.file.size / (1024 * 1024)).toFixed(2)} MB
                    </span>
                    {item.status === "uploading" && (
                      <div className="flex items-center gap-1 text-[10px] text-indigo-400 font-medium">
                        <Loader2 className="h-3 w-3 animate-spin shrink-0" />
                        Uploading ({item.progress}%)
                      </div>
                    )}
                    {item.status === "completed" && (
                      <span className="flex items-center gap-1 text-[10px] text-emerald-400 font-medium">
                        <CheckCircle2 className="h-3 w-3 shrink-0" />
                        Completed
                      </span>
                    )}
                    {item.status === "cancelled" && (
                      <span className="flex items-center gap-1 text-[10px] text-slate-400 font-medium">
                        <AlertCircle className="h-3 w-3 shrink-0" />
                        Cancelled
                      </span>
                    )}
                    {item.status === "failed" && (
                      <span className="flex items-center gap-1 text-[10px] text-red-400 font-medium truncate">
                        <AlertCircle className="h-3 w-3 shrink-0 text-red-450" />
                        {item.error}
                      </span>
                    )}
                  </div>
                  {item.status === "uploading" && (
                    <div className="w-full bg-slate-950 rounded-full h-1 mt-2 overflow-hidden">
                      <div
                        className="bg-indigo-650 h-1 rounded-full transition-all duration-300"
                        style={{ width: `${item.progress}%` }}
                      />
                    </div>
                  )}
                </div>
              </div>

              <div className="flex items-center gap-1 shrink-0">
                {(item.status === "failed" || item.status === "cancelled") && (
                  <button
                    onClick={() => handleRetry(item)}
                    className="p-1.5 hover:bg-slate-950 border border-slate-850 hover:border-slate-800 text-slate-400 hover:text-slate-200 rounded-lg transition-colors cursor-pointer"
                    title="Retry upload"
                  >
                    <RefreshCw className="h-3.5 w-3.5" />
                  </button>
                )}
                <button
                  onClick={() => handleRemoveItem(item.id)}
                  className="p-1.5 hover:bg-slate-950 border border-slate-850 hover:border-slate-800 text-slate-400 hover:text-red-450 rounded-lg transition-colors cursor-pointer"
                  title="Cancel / Remove item"
                >
                  <X className="h-3.5 w-3.5" />
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
