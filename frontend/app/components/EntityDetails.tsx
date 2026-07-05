"use client";

import React from 'react';
import { motion } from 'framer-motion';
import { 
  User, 
  FolderGit2, 
  FileText, 
  Cpu, 
  Calendar, 
  Network, 
  Layers3
} from 'lucide-react';
import { Entity, getConnectedEntities } from '../mockData';

interface EntityDetailsProps {
  entity: Entity | null;
  onClose: () => void;
  onSelectEntity: (entity: Entity) => void;
}

export default function EntityDetails({ entity, onClose, onSelectEntity }: EntityDetailsProps) {
  if (!entity) return null;

  const connected = getConnectedEntities(entity.id);

  const renderContextualProperties = () => {
    if (entity.type === 'document') {
      const relatedDocs = connected.filter(c => c.entity.type === 'document').map(c => c.entity.name).join(', ') || 'None';
      return (
        <div className="p-4 rounded-xl bg-zinc-900/50 border border-zinc-900 space-y-3 mb-6">
          <h3 className="text-[10px] uppercase font-bold tracking-wider text-zinc-500">Document Info</h3>
          <div className="grid grid-cols-2 gap-y-3 gap-x-2 text-xs">
            <div>
              <span className="text-zinc-600 block text-[10px] capitalize font-mono">Uploaded</span>
              <span className="text-zinc-300 font-medium">{entity.meta.lastUpdated || '2026-07-01'}</span>
            </div>
            <div>
              <span className="text-zinc-600 block text-[10px] capitalize font-mono">Department</span>
              <span className="text-zinc-300 font-medium">Engineering</span>
            </div>
            <div className="col-span-2">
              <span className="text-zinc-600 block text-[10px] capitalize font-mono">Summary</span>
              <span className="text-zinc-300 font-medium">{entity.details}</span>
            </div>
            <div className="col-span-2">
              <span className="text-zinc-600 block text-[10px] capitalize font-mono">Tags</span>
              <span className="text-zinc-300 font-medium">Specs, Authentication, Vector Sync</span>
            </div>
            <div className="col-span-2">
              <span className="text-zinc-600 block text-[10px] capitalize font-mono">Related Docs</span>
              <span className="text-zinc-300 font-medium font-sans">{relatedDocs}</span>
            </div>
          </div>
        </div>
      );
    }

    if (entity.type === 'person') {
      const projectsList = connected.filter(c => c.entity.type === 'project').map(c => c.entity.name).join(', ') || 'General';
      const relatedDocs = connected.filter(c => c.entity.type === 'document').map(c => c.entity.name).join(', ') || 'None';
      return (
        <div className="p-4 rounded-xl bg-zinc-900/50 border border-zinc-900 space-y-3 mb-6">
          <h3 className="text-[10px] uppercase font-bold tracking-wider text-zinc-500">Employee</h3>
          <div className="grid grid-cols-2 gap-y-3 gap-x-2 text-xs">
            <div>
              <span className="text-zinc-600 block text-[10px] capitalize font-mono">Role</span>
              <span className="text-zinc-300 font-medium">{entity.meta.role || 'Staff Engineer'}</span>
            </div>
            <div>
              <span className="text-zinc-600 block text-[10px] capitalize font-mono">Department</span>
              <span className="text-zinc-300 font-medium">{entity.meta.department || 'Engineering'}</span>
            </div>
            <div className="col-span-2">
              <span className="text-zinc-600 block text-[10px] capitalize font-mono">Projects</span>
              <span className="text-zinc-300 font-medium">{projectsList}</span>
            </div>
            <div className="col-span-2">
              <span className="text-zinc-600 block text-[10px] capitalize font-mono">Skills</span>
              <span className="text-zinc-300 font-medium">Semantic Mapping, Vector Embeddings, APIs</span>
            </div>
            <div className="col-span-2">
              <span className="text-zinc-600 block text-[10px] capitalize font-mono">Related Documents</span>
              <span className="text-zinc-300 font-medium font-sans">{relatedDocs}</span>
            </div>
          </div>
        </div>
      );
    }

    // Default/Chatting/Other sources representation
    return (
      <div className="p-4 rounded-xl bg-zinc-900/50 border border-zinc-900 space-y-3 mb-6">
        <h3 className="text-[10px] uppercase font-bold tracking-wider text-zinc-500">Sources Used</h3>
        <div className="grid grid-cols-2 gap-y-3 gap-x-2 text-xs">
          <div>
            <span className="text-zinc-600 block text-[10px] capitalize font-mono">Confidence Match</span>
            <span className="text-emerald-400 font-mono font-semibold">98.4% Match</span>
          </div>
          <div>
            <span className="text-zinc-600 block text-[10px] capitalize font-mono">Indexed Node ID</span>
            <span className="text-zinc-300 font-mono">{entity.id}</span>
          </div>
          <div className="col-span-2">
            <span className="text-zinc-600 block text-[10px] capitalize font-mono">Related Questions</span>
            <span className="text-zinc-300 block font-sans">
              - Explain semantic linkages for {entity.name}<br/>
              - What external platform syncs {entity.name}?
            </span>
          </div>
        </div>
      </div>
    );
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

  return (
    <motion.div 
      initial={{ x: '100%', opacity: 0 }}
      animate={{ x: 0, opacity: 1 }}
      exit={{ x: '100%', opacity: 0 }}
      transition={{ type: 'spring', damping: 25, stiffness: 200 }}
      className="fixed top-0 right-0 z-50 w-96 border-l border-zinc-800 bg-zinc-950/95 backdrop-blur-md p-6 flex flex-col h-screen overflow-y-auto shadow-[0_0_50px_rgba(0,0,0,0.8)]"
    >
      {/* Header */}
      <div className="flex items-center justify-between pb-4 border-b border-zinc-900 mb-6">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-lg bg-zinc-900 border border-zinc-800 flex items-center justify-center">
            {React.createElement(getIcon(entity.type), { className: "w-4 h-4 text-indigo-400" })}
          </div>
          <div>
            <span className="text-[9px] uppercase tracking-wider text-indigo-400 font-mono font-bold">
              {entity.type}
            </span>
            <h2 className="text-sm font-semibold text-white tracking-tight">{entity.name}</h2>
          </div>
        </div>
        <button 
          onClick={onClose}
          className="text-xs text-zinc-500 hover:text-zinc-300 font-mono tracking-tight cursor-pointer"
        >
          ESC
        </button>
      </div>

      {/* Description */}
      <div className="space-y-4 mb-6">
        <p className="text-xs leading-relaxed text-zinc-400">{entity.details}</p>
      </div>

      {/* Contextual Properties Panel */}
      {renderContextualProperties()}

      {/* Connections List */}
      <div className="space-y-3">
        <h3 className="text-[10px] uppercase font-bold tracking-wider text-zinc-500">Related Documents</h3>
        <div className="space-y-2">
          {connected.length === 0 ? (
            <p className="text-xs text-zinc-600 italic">No semantic connections detected.</p>
          ) : (
            connected.map(({ entity: connectedEntity, type }) => {
              const ConnIcon = getIcon(connectedEntity.type);
              return (
                <button
                  key={connectedEntity.id}
                  onClick={() => onSelectEntity(connectedEntity)}
                  className="w-full text-left p-2.5 rounded-lg border border-zinc-900 bg-zinc-900/20 hover:bg-zinc-900/60 hover:border-zinc-800 transition flex items-center justify-between group cursor-pointer"
                >
                  <div className="flex items-center gap-2">
                    <ConnIcon className="w-3.5 h-3.5 text-zinc-500 group-hover:text-indigo-400 transition" />
                    <div>
                      <p className="text-xs font-medium text-zinc-300 group-hover:text-white transition">
                        {connectedEntity.name}
                      </p>
                      <p className="text-[10px] text-zinc-500 capitalize">{connectedEntity.type}</p>
                    </div>
                  </div>
                  <span className="text-[9px] font-mono px-2 py-0.5 rounded-full bg-zinc-900 text-zinc-400 group-hover:bg-indigo-950 group-hover:text-indigo-300 transition">
                    {type}
                  </span>
                </button>
              );
            })
          )}
        </div>
      </div>
    </motion.div>
  );
}
