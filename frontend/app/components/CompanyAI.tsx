"use client";

import React, { useState, useEffect, useRef } from "react";
import { useAuth } from "../providers/AuthProvider";
import { ChatService, type Conversation, type ChatMessage } from "../services/ChatService";
import { DocumentService } from "../services/DocumentService";
import { 
  Sparkles, 
  Send, 
  User, 
  Bot, 
  ArrowUpRight,
  Plus,
  Trash2,
  ChevronRight,
  MessageSquare,
  StopCircle,
  Copy,
  CheckCircle,
  X,
  FileText,
  AlertCircle,
  Clock,
  Loader2
} from "lucide-react";

interface CompanyAIProps {
  onSelectEntity?: (entity: any) => void;
}

export default function CompanyAI({ onSelectEntity }: CompanyAIProps) {
  const { activeOrg, activeWorkspace } = useAuth();
  
  // Conversations and active thread state
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [activeConvoId, setActiveConvoId] = useState<string | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [loadingHistory, setLoadingHistory] = useState(false);

  // Input states
  const [input, setInput] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const abortControllerRef = useRef<AbortController | null>(null);

  // Split screen citation previewer
  const [citationDoc, setCitationDoc] = useState<any | null>(null);
  const [citationChunkText, setCitationChunkText] = useState<string | null>(null);
  const [loadingDocPreview, setLoadingDocPreview] = useState(false);

  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Suggested questions
  const suggestedPrompts = [
    "Summarize the employee onboarding requirements.",
    "Explain the technical deployment architecture.",
    "List the critical deadlines and action items."
  ];

  // 1. Fetch conversations list for workspace on mount
  useEffect(() => {
    if (!activeWorkspace) return;
    loadConversations();
  }, [activeWorkspace]);

  const loadConversations = async () => {
    if (!activeWorkspace) return;
    try {
      const history = await ChatService.listConversations(activeWorkspace.id);
      setConversations(history);
      if (history.length > 0 && !activeConvoId) {
        // Auto-select latest thread
        handleSelectConversation(history[0].id);
      }
    } catch (err) {
      console.error("Failed to load threads:", err);
    }
  };

  // 2. Fetch messages when active conversation changes
  const handleSelectConversation = async (id: string) => {
    setActiveConvoId(id);
    setLoadingHistory(true);
    try {
      const list = await ChatService.getMessages(id);
      setMessages(list);
    } catch (err) {
      console.error("Failed to load message history:", err);
    } finally {
      setLoadingHistory(false);
    }
  };

  // 3. Create new conversation thread
  const handleNewConversation = async () => {
    if (!activeOrg || !activeWorkspace) return;
    try {
      const convo = await ChatService.createConversation(
        activeOrg.id,
        activeWorkspace.id,
        `Chat Thread ${new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}`
      );
      setConversations(prev => [convo, ...prev]);
      setActiveConvoId(convo.id);
      setMessages([]);
    } catch (err) {
      console.error("Failed to create conversation:", err);
    }
  };

  const handleDeleteConversation = async (id: string, e: React.MouseEvent) => {
    e.stopPropagation();
    if (!window.confirm("Delete this conversation thread?")) return;
    try {
      await ChatService.deleteConversation(id);
      setConversations(prev => prev.filter(c => c.id !== id));
      if (activeConvoId === id) {
        setActiveConvoId(null);
        setMessages([]);
      }
    } catch (err) {
      console.error("Failed to delete thread:", err);
    }
  };

  // 4. Send Message via SSE Streaming API
  const handleSend = async (text: string) => {
    if (!text.trim() || isTyping) return;

    let currentConvoId = activeConvoId;

    // JIT-create thread if missing
    if (!currentConvoId) {
      if (!activeOrg || !activeWorkspace) return;
      try {
        const convo = await ChatService.createConversation(activeOrg.id, activeWorkspace.id, text.substring(0, 30) + "...");
        currentConvoId = convo.id;
        setActiveConvoId(convo.id);
        setConversations(prev => [convo, ...prev]);
      } catch (err) {
        console.error("Failed to create JIT thread:", err);
        return;
      }
    }

    // Append user message immediately
    const userMsg: ChatMessage = {
      id: `user-${Date.now()}`,
      conversation_id: currentConvoId,
      role: "user",
      content: text,
      token_count: text.length // estimate
    } as any;

    setMessages(prev => [...prev, userMsg]);
    setInput("");
    setIsTyping(true);

    // Placeholder message for assistant streaming
    const assistantMsgId = `assistant-${Date.now()}`;
    const assistantPlaceholder: ChatMessage = {
      id: assistantMsgId,
      conversation_id: currentConvoId,
      role: "assistant",
      content: "",
      token_count: 0,
      message_metadata: { sources: [] }
    } as any;

    setMessages(prev => [...prev, assistantPlaceholder]);

    const controller = new AbortController();
    abortControllerRef.current = controller;

    let streamedText = "";
    let metadata: any = null;

    try {
      await ChatService.askStream(
        currentConvoId,
        text,
        null, // all files in workspace
        (chunk) => {
          streamedText += chunk;
          setMessages(prev =>
            prev.map(m =>
              m.id === assistantMsgId
                ? { ...m, content: streamedText }
                : m
            )
          );
        },
        (metaPayload) => {
          metadata = metaPayload;
          setMessages(prev =>
            prev.map(m =>
              m.id === assistantMsgId
                ? { ...m, message_metadata: metaPayload.meta || { sources: metaPayload.sources } }
                : m
            )
          );
        },
        controller.signal
      );
    } catch (err: any) {
      if (err.name === "AbortError") {
        console.log("Chat stream aborted by user.");
      } else {
        console.error("Stream failed:", err);
        setMessages(prev =>
          prev.map(m =>
            m.id === assistantMsgId
              ? { ...m, content: m.content + "\n\n⚠️ Error: Failed to generate response." }
              : m
          )
        );
      }
    } finally {
      setIsTyping(false);
      abortControllerRef.current = null;
      loadConversations(); // refresh list to update title if changed
    }
  };

  const handleStopGeneration = () => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }
  };

  // Scroll to bottom helper
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isTyping]);

  // Copy response helper
  const handleCopy = (text: string) => {
    navigator.clipboard.writeText(text);
    alert("Response copied to clipboard!");
  };

  // Trigger preview for citation source (Split-screen PDF Inspector)
  const handleSelectCitation = async (source: any) => {
    setLoadingDocPreview(true);
    setCitationChunkText(null);
    try {
      const doc = await DocumentService.getById(source.document_id);
      setCitationDoc(doc);
      
      // Load chunks to fetch matching text context
      const chunks = await DocumentService.listChunks(source.document_id);
      const match = chunks.find((c: any) => c.chunk_index === source.chunk_index);
      if (match) {
        setCitationChunkText(match.content);
      }
    } catch (err) {
      console.error("Failed to load preview document:", err);
      setCitationDoc(null);
    } finally {
      setLoadingDocPreview(false);
    }
  };

  return (
    <div className="flex gap-4 w-full h-[calc(100vh-8rem)] text-slate-200">
      
      {/* 1. Conversations Sidebar */}
      <div className="w-64 bg-slate-900/40 border border-slate-800 rounded-2xl flex flex-col justify-between shrink-0 overflow-hidden">
        <div className="p-4 flex flex-col gap-4 overflow-hidden h-full">
          <button
            onClick={handleNewConversation}
            className="flex items-center justify-center gap-2 w-full py-2.5 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl text-xs font-semibold shadow-lg shadow-indigo-600/10 cursor-pointer transition-all active:translate-y-[1px]"
          >
            <Plus className="w-4 h-4" /> New Chat
          </button>
          
          <div className="flex-1 overflow-y-auto space-y-2 pr-1">
            {conversations.map((convo) => (
              <div
                key={convo.id}
                onClick={() => handleSelectConversation(convo.id)}
                className={`group flex items-center justify-between p-3 rounded-xl cursor-pointer transition ${
                  activeConvoId === convo.id
                    ? "bg-indigo-950/20 border border-indigo-500/30 text-white"
                    : "bg-slate-950/20 border border-transparent hover:bg-slate-900/30 hover:border-slate-850 text-slate-400"
                }`}
              >
                <div className="flex items-center gap-2 min-w-0">
                  <MessageSquare className="w-4 h-4 text-indigo-400 shrink-0" />
                  <span className="text-xs truncate font-medium">{convo.title}</span>
                </div>
                <button
                  onClick={(e) => handleDeleteConversation(convo.id, e)}
                  className="opacity-0 group-hover:opacity-100 p-1 hover:bg-slate-950 rounded-lg text-slate-500 hover:text-red-400 transition cursor-pointer"
                >
                  <Trash2 className="w-3.5 h-3.5" />
                </button>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* 2. Chat Conversation Frame */}
      <div className="flex-1 bg-slate-900/20 border border-slate-900 rounded-2xl flex flex-col justify-between overflow-hidden">
        
        {/* Messages Feed */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6">
          {messages.length === 0 ? (
            <div className="h-full flex flex-col items-center justify-center space-y-8 max-w-lg mx-auto text-center">
              <div className="h-14 w-14 bg-indigo-950/30 border border-indigo-900/50 rounded-2xl flex items-center justify-center text-indigo-400">
                <Sparkles className="w-7 h-7" />
              </div>
              <div className="space-y-2.5">
                <h2 className="text-xl font-bold tracking-tight text-white">Enterprise RAG Assistant</h2>
                <p className="text-xs text-slate-500 leading-relaxed">
                  Query all documents indexed inside the active workspace. Responses are grounded, containing direct source page links.
                </p>
              </div>

              {/* Action Cards / Suggested prompts */}
              <div className="grid grid-cols-1 gap-2.5 w-full">
                {suggestedPrompts.map((p, idx) => (
                  <button
                    key={idx}
                    onClick={() => handleSend(p)}
                    className="p-3 text-left bg-slate-950/40 border border-slate-850 hover:border-slate-800 hover:bg-slate-900/40 rounded-xl text-[11px] text-slate-400 hover:text-slate-200 transition cursor-pointer flex items-center justify-between"
                  >
                    <span>{p}</span>
                    <ChevronRight className="w-3.5 h-3.5 text-slate-600 shrink-0" />
                  </button>
                ))}
              </div>
            </div>
          ) : (
            <div className="space-y-6">
              {messages.map((msg) => (
                <div key={msg.id} className={`flex gap-4 ${msg.role === 'user' ? 'justify-end' : ''}`}>
                  {msg.role === 'assistant' && (
                    <div className="w-8 h-8 rounded-lg bg-indigo-950/40 border border-indigo-900/40 flex items-center justify-center shrink-0">
                      <Bot className="w-4.5 h-4.5 text-indigo-400" />
                    </div>
                  )}
                  
                  <div className="max-w-[85%] space-y-2.5 min-w-0">
                    <div className={`p-4 rounded-2xl border text-xs leading-relaxed ${
                      msg.role === 'user'
                        ? 'bg-indigo-650/15 border-indigo-600/20 text-white'
                        : 'bg-slate-900/40 border-slate-850/80 text-slate-300 font-sans'
                    }`}>
                      {/* Standard text output (support simple code and lists) */}
                      <p className="whitespace-pre-wrap">{msg.content}</p>
                    </div>

                    {/* Citations block */}
                    {msg.role === 'assistant' && msg.message_metadata?.sources && msg.message_metadata.sources.length > 0 && (
                      <div className="space-y-1.5 pl-1">
                        <span className="text-[9px] text-slate-500 uppercase tracking-wider font-bold">Supplied Context Sources</span>
                        <div className="flex flex-wrap gap-2">
                          {msg.message_metadata.sources.map((src, sIdx) => (
                            <button
                              key={sIdx}
                              onClick={() => handleSelectCitation(src)}
                              className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-slate-950/60 border border-slate-850 hover:border-indigo-500/50 hover:bg-slate-900 transition text-[10px] font-mono text-slate-400 hover:text-slate-200 cursor-pointer"
                            >
                              <span className="w-1.5 h-1.5 rounded-full bg-emerald-500"></span>
                              <span className="truncate max-w-[120px]">{src.filename}</span>
                              <span>[{src.page ? `Page ${src.page}` : `Chunk ${src.chunk_index + 1}`}]</span>
                              <span className="text-[9px] text-slate-500 font-semibold">{src.confidence}%</span>
                            </button>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Action row at bottom of assistant messages */}
                    {msg.role === 'assistant' && msg.content && (
                      <div className="flex items-center gap-2 pl-1">
                        <button
                          onClick={() => handleCopy(msg.content)}
                          className="flex items-center gap-1 px-2 py-1 bg-slate-950/20 hover:bg-slate-950/60 border border-slate-900 rounded-lg text-[10px] text-slate-500 hover:text-slate-350 transition cursor-pointer"
                        >
                          <Copy className="w-3 h-3" /> Copy
                        </button>
                        {msg.message_metadata?.suggested_followups && (
                          <div className="flex gap-2">
                            {msg.message_metadata.suggested_followups.slice(0, 1).map((fUp, fIdx) => (
                              <button
                                key={fIdx}
                                onClick={() => handleSend(fUp)}
                                className="px-2 py-1 bg-indigo-950/10 hover:bg-indigo-950/30 border border-indigo-900/30 rounded-lg text-[10px] text-indigo-400 cursor-pointer transition"
                              >
                                Follow-up: &ldquo;{fUp.substring(0, 30)}...&rdquo;
                              </button>
                            ))}
                          </div>
                        )}
                      </div>
                    )}
                  </div>

                  {msg.role === 'user' && (
                    <div className="w-8 h-8 rounded-lg bg-slate-800 border border-slate-750 flex items-center justify-center shrink-0">
                      <User className="w-4.5 h-4.5 text-zinc-300" />
                    </div>
                  )}
                </div>
              ))}
              <div ref={messagesEndRef} />
            </div>
          )}
        </div>

        {/* Input Controls */}
        <div className="p-4 border-t border-slate-900 bg-slate-950/20">
          <div className="relative flex items-center gap-3">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter') handleSend(input);
              }}
              placeholder="Query your workspace knowledge base..."
              className="w-full bg-slate-950/60 border border-slate-850 focus:border-indigo-500/80 focus:ring-1 focus:ring-indigo-500/30 rounded-xl pl-4 pr-12 py-3.5 text-xs text-white placeholder-slate-500 outline-none transition-all duration-300"
            />
            <div className="absolute right-3 top-1/2 -translate-y-1/2 flex items-center gap-2">
              {isTyping ? (
                <button
                  onClick={handleStopGeneration}
                  className="w-7 h-7 rounded-lg bg-red-950/40 border border-red-900/40 hover:bg-red-900/25 transition flex items-center justify-center text-red-400 cursor-pointer"
                  title="Stop generating"
                >
                  <StopCircle className="w-4.5 h-4.5" />
                </button>
              ) : (
                <button
                  onClick={() => handleSend(input)}
                  className="w-7 h-7 rounded-lg bg-indigo-650 hover:bg-indigo-600 transition flex items-center justify-center text-white cursor-pointer"
                >
                  <Send className="w-3.5 h-3.5" />
                </button>
              )}
            </div>
          </div>
        </div>

      </div>

      {/* 3. Split-screen Document Preview Side-panel */}
      {citationDoc && (
        <div className="w-[30rem] bg-slate-900/60 border border-slate-800 rounded-2xl p-6 flex flex-col justify-between max-h-[calc(100vh-8rem)] sticky top-24 overflow-y-auto animate-in slide-in-from-right-4 duration-200 shrink-0">
          <div className="space-y-6">
            <div className="flex items-start justify-between pb-4 border-b border-slate-800">
              <div className="flex items-center gap-3 min-w-0">
                <FileText className="w-5 h-5 text-indigo-400 shrink-0" />
                <div className="min-w-0">
                  <h3 className="text-sm font-bold text-slate-200 truncate">{citationDoc.original_filename}</h3>
                  <span className="text-[10px] font-mono text-slate-500">Document Grounding Viewer</span>
                </div>
              </div>
              <button 
                onClick={() => setCitationDoc(null)}
                className="p-1 hover:bg-slate-950 border border-slate-850 rounded-lg text-slate-500 hover:text-slate-350 cursor-pointer"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            {/* Document Abstract */}
            <div className="space-y-3">
              <h4 className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Document Summary</h4>
              <div className="p-4 bg-slate-950 border border-slate-850 rounded-xl text-xs text-slate-300 leading-relaxed">
                {citationDoc.summary || "Summary generation is in-progress."}
              </div>
            </div>

            {/* Highlighted Chunk Selection Context */}
            <div className="space-y-3">
              <h4 className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Referenced Grounded Segment</h4>
              {loadingDocPreview ? (
                <div className="flex items-center justify-center p-12">
                  <Loader2 className="w-6 h-6 animate-spin text-indigo-400" />
                </div>
              ) : citationChunkText ? (
                <div className="p-4 bg-indigo-950/10 border border-indigo-500/25 rounded-xl text-xs text-slate-200 leading-relaxed font-sans shadow-md border-l-4 border-l-emerald-500">
                  <p className="whitespace-pre-wrap">{citationChunkText}</p>
                </div>
              ) : (
                <div className="text-center py-6 text-xs text-slate-500 italic">Failed to resolve matching text segment.</div>
              )}
            </div>

            {/* Ingestion Profile Summary */}
            <div className="space-y-3">
              <h4 className="text-xs font-semibold text-slate-400 uppercase tracking-wider">File Metadata</h4>
              <div className="bg-slate-950 border border-slate-850 rounded-xl p-4 space-y-2 text-[11px] font-mono text-slate-400">
                <div className="flex justify-between"><span className="text-slate-600">MIME Type:</span><span>{citationDoc.mime_type}</span></div>
                <div className="flex justify-between"><span className="text-slate-600">Size:</span><span>{(citationDoc.file_size / (1024 * 1024)).toFixed(3)} MB</span></div>
                <div className="flex justify-between"><span className="text-slate-600">Language:</span><span className="uppercase">{citationDoc.language || "en"}</span></div>
                <div className="flex justify-between"><span className="text-slate-600">Uploaded At:</span><span>{new Date(citationDoc.created_at).toLocaleString()}</span></div>
              </div>
            </div>

          </div>
        </div>
      )}

    </div>
  );
}
