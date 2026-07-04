"use client";

import React, { useState } from 'react';
import { 
  Sparkles, 
  Send, 
  User, 
  Bot, 
  ArrowUpRight,
  Upload,
  Search,
  Building2
} from 'lucide-react';
import { Entity, entities } from '../mockData';
import { sendMessageToAI } from '../services/companyAIService';

interface CompanyAIProps {
  onSelectEntity: (entity: Entity) => void;
}

interface Message {
  id: string;
  sender: 'user' | 'assistant';
  text: string;
  citations?: string[]; // IDs of entities
}

export default function CompanyAI({ onSelectEntity }: CompanyAIProps) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isTyping, setIsTyping] = useState(false);

  const actionCards = [
    { label: 'Upload Document', prompt: 'Upload new documentation to index', icon: Upload },
    { label: 'Search Knowledge', prompt: 'Who is the lead engineer of Payments 2.0?', icon: Search },
    { label: 'Generate Summary', prompt: 'Summarize Project Atlas technologies', icon: Sparkles },
    { label: 'Ask About Company', prompt: 'Where is the onboarding guide stored?', icon: Building2 }
  ];

  const handleSend = async (text: string) => {
    if (!text.trim()) return;

    const userMsg: Message = {
      id: `msg-${Date.now()}`,
      sender: 'user',
      text: text
    };

    setMessages(prev => [...prev, userMsg]);
    setInput('');
    setIsTyping(true);

    try {
      const response = await sendMessageToAI(text);
      setMessages(prev => [...prev, {
        id: `reply-${Date.now()}`,
        sender: 'assistant',
        text: response.text,
        citations: response.citations
      }]);
    } catch (err) {
      console.error(err);
    } finally {
      setIsTyping(false);
    }
  };

  const getCitations = (ids: string[]) => {
    return ids.map(id => entities.find(e => e.id === id)).filter(Boolean) as Entity[];
  };

  return (
    <div className="flex-1 max-w-3xl mx-auto flex flex-col h-[calc(100vh-140px)] justify-between">
      {/* Messages Feed or Initial Center Console */}
      {messages.length === 0 ? (
        <div className="flex-1 flex flex-col items-center justify-center space-y-8">
          {/* Centered Headers */}
          <div className="text-center space-y-2">
            <h2 className="text-3xl font-bold tracking-tight text-white font-sans">
              Ask BrainOS
            </h2>
            <p className="text-sm text-zinc-500 font-sans">
              &ldquo;What do you need?&rdquo;
            </p>
          </div>

          {/* Centered Input box */}
          <div className="w-full max-w-xl relative">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter') handleSend(input);
              }}
              placeholder="Ask anything..."
              className="w-full bg-zinc-900/40 border border-zinc-800/85 focus:border-indigo-500/80 focus:ring-1 focus:ring-indigo-500/20 rounded-xl pl-4 pr-12 py-3 text-xs text-white placeholder-zinc-500 outline-none transition-all duration-300 shadow-md"
            />
            <button
              onClick={() => handleSend(input)}
              className="absolute right-2 top-1/2 -translate-y-1/2 w-8 h-8 rounded-lg bg-indigo-600 hover:bg-indigo-500 transition flex items-center justify-center text-white cursor-pointer"
            >
              <Send className="w-3.5 h-3.5" />
            </button>
          </div>

          {/* Action cards row */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3 w-full max-w-2xl">
            {actionCards.map((card, idx) => {
              const Icon = card.icon;
              return (
                <button
                  key={idx}
                  onClick={() => handleSend(card.prompt)}
                  className="p-4 rounded-xl border border-zinc-900 bg-zinc-900/10 hover:bg-zinc-900/40 hover:border-zinc-800 transition flex flex-col items-center justify-center text-center gap-2 cursor-pointer group"
                >
                  <Icon className="w-4 h-4 text-zinc-500 group-hover:text-indigo-400 transition" />
                  <span className="text-[10px] font-semibold text-zinc-400 group-hover:text-zinc-200 transition">
                    {card.label}
                  </span>
                </button>
              );
            })}
          </div>
        </div>
      ) : (
        /* Conversation Feed View */
        <div className="flex-1 flex flex-col justify-between">
          <div className="flex-1 overflow-y-auto pr-2 space-y-6 mb-6">
            {messages.map((msg) => (
              <div key={msg.id} className={`flex gap-4 ${msg.sender === 'user' ? 'justify-end' : ''}`}>
                {msg.sender === 'assistant' && (
                  <div className="w-8 h-8 rounded-lg bg-indigo-950/40 border border-indigo-900/40 flex items-center justify-center shrink-0">
                    <Bot className="w-4.5 h-4.5 text-indigo-400" />
                  </div>
                )}
                
                <div className="max-w-[80%] space-y-3">
                  <div className={`p-4 rounded-2xl border text-xs leading-relaxed ${
                    msg.sender === 'user'
                      ? 'bg-indigo-600/10 border-indigo-500/20 text-white'
                      : 'bg-zinc-900/40 border-zinc-800/80 text-zinc-300'
                  }`}>
                    {msg.text}
                  </div>

                  {/* Citations block */}
                  {msg.citations && msg.citations.length > 0 && (
                    <div className="space-y-1.5 pl-1">
                      <span className="text-[10px] text-zinc-500 uppercase tracking-wider font-semibold">Connections & Sources</span>
                      <div className="flex flex-wrap gap-2">
                        {getCitations(msg.citations).map((ent) => (
                          <button
                            key={ent.id}
                            onClick={() => onSelectEntity(ent)}
                            className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-zinc-900/60 border border-zinc-800 hover:border-indigo-500/50 hover:bg-zinc-900 transition text-[11px] font-medium text-zinc-300 hover:text-white cursor-pointer"
                          >
                            <span className="w-1.5 h-1.5 rounded-full bg-indigo-500"></span>
                            {ent.name}
                            <ArrowUpRight className="w-3 h-3 text-zinc-500" />
                          </button>
                        ))}
                      </div>
                    </div>
                  )}
                </div>

                {msg.sender === 'user' && (
                  <div className="w-8 h-8 rounded-lg bg-zinc-800 border border-zinc-700 flex items-center justify-center shrink-0">
                    <User className="w-4.5 h-4.5 text-zinc-300" />
                  </div>
                )}
              </div>
            ))}

            {isTyping && (
              <div className="flex gap-4">
                <div className="w-8 h-8 rounded-lg bg-indigo-950/40 border border-indigo-900/40 flex items-center justify-center shrink-0">
                  <Bot className="w-4.5 h-4.5 text-indigo-400" />
                </div>
                <div className="p-4 rounded-2xl border bg-zinc-900/40 border-zinc-800/80 flex items-center gap-1.5">
                  <span className="w-2 h-2 rounded-full bg-indigo-500 animate-bounce" style={{ animationDelay: '0ms' }}></span>
                  <span className="w-2 h-2 rounded-full bg-indigo-500 animate-bounce" style={{ animationDelay: '150ms' }}></span>
                  <span className="w-2 h-2 rounded-full bg-indigo-500 animate-bounce" style={{ animationDelay: '300ms' }}></span>
                </div>
              </div>
            )}
          </div>

          {/* Persistent Input Bar */}
          <div className="relative">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter') handleSend(input);
              }}
              placeholder="Ask anything from the enterprise brain..."
              className="w-full bg-zinc-900/60 border border-zinc-800 focus:border-indigo-500/80 focus:ring-1 focus:ring-indigo-500/30 rounded-2xl pl-4 pr-12 py-4 text-xs text-white placeholder-zinc-500 outline-none transition-all duration-300"
            />
            <button
              onClick={() => handleSend(input)}
              className="absolute right-3 top-1/2 -translate-y-1/2 w-8 h-8 rounded-lg bg-indigo-600 hover:bg-indigo-500 transition flex items-center justify-center text-white cursor-pointer"
            >
              <Send className="w-4 h-4" />
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
