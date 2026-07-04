"use client";

import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { 
  User, 
  FolderGit2, 
  FileText, 
  Cpu, 
  Calendar, 
  Layers3, 
  Network,
  Share2
} from 'lucide-react';
import { Entity, Relationship } from '../mockData';
import { getGraphData } from '../services/graphService';

interface GraphProps {
  onSelectEntity: (entity: Entity) => void;
  selectedEntity: Entity | null;
}

export default function Graph({ onSelectEntity, selectedEntity }: GraphProps) {
  // Simple circular distribution configuration for mock graph nodes
  const width = 1000;
  const height = 650;
  const cx = width / 2;
  const cy = height / 2;
  const r = 240;

  const [nodes, setNodes] = useState<(Entity & { x: number; y: number })[]>([]);
  const [relationships, setRelationships] = useState<Relationship[]>([]);

  useEffect(() => {
    getGraphData().then(data => {
      // Lay out nodes in a circle
      const formatted = data.nodes.map((entity, i) => {
        const angle = (i / data.nodes.length) * 2 * Math.PI;
        const x = cx + r * Math.cos(angle);
        const y = cy + r * Math.sin(angle);
        return { ...entity, x, y };
      });
      setNodes(formatted);
      setRelationships(data.edges);
    });
  }, [cx, cy, r]);

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

  const getAccentColor = (type: string) => {
    switch (type) {
      case 'person': return 'stroke-sky-500 fill-sky-950 text-sky-400';
      case 'project': return 'stroke-indigo-500 fill-indigo-950 text-indigo-400';
      case 'document': return 'stroke-amber-500 fill-amber-950 text-amber-400';
      case 'technology': return 'stroke-emerald-500 fill-emerald-950 text-emerald-400';
      case 'meeting': return 'stroke-purple-500 fill-purple-950 text-purple-400';
      case 'department': return 'stroke-pink-500 fill-pink-950 text-pink-400';
      case 'integration': return 'stroke-rose-500 fill-rose-950 text-rose-400';
      default: return 'stroke-zinc-500 fill-zinc-950 text-zinc-400';
    }
  };

  return (
    <div className="flex-1 bg-zinc-950/40 rounded-2xl border border-zinc-900 flex flex-col relative overflow-hidden h-[calc(100vh-190px)] w-full">
      <div className="absolute top-4 left-4 z-10">
        <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-zinc-900/80 border border-zinc-800 backdrop-blur-md">
          <Share2 className="w-3.5 h-3.5 text-indigo-400" />
          <span className="text-xs font-semibold text-zinc-300">Semantic Connection Map</span>
        </div>
      </div>

      <div className="absolute top-4 right-4 z-10 flex gap-2">
        <span className="text-[10px] text-zinc-500 font-mono">Interactive canvas: click nodes to traverse relations</span>
      </div>

      <div className="flex-1 flex items-center justify-center p-4">
        <svg viewBox={`0 0 ${width} ${height}`} className="w-full h-full max-w-4xl select-none">
          {/* Render Connections/Edges */}
          <g>
            {relationships.map((rel, idx) => {
              const sourceNode = nodes.find(n => n.id === rel.source);
              const targetNode = nodes.find(n => n.id === rel.target);
              if (!sourceNode || !targetNode) return null;

              const isHighlighted = selectedEntity && (selectedEntity.id === rel.source || selectedEntity.id === rel.target);

              return (
                <g key={`edge-${idx}`}>
                  <line
                    x1={sourceNode.x}
                    y1={sourceNode.y}
                    x2={targetNode.x}
                    y2={targetNode.y}
                    className={`transition-all duration-300 ${
                      isHighlighted 
                        ? 'stroke-indigo-500/60 stroke-2' 
                        : 'stroke-zinc-800/40 stroke-1'
                    }`}
                  />
                  {isHighlighted && (
                    <text
                      x={(sourceNode.x + targetNode.x) / 2}
                      y={(sourceNode.y + targetNode.y) / 2 - 4}
                      className="fill-indigo-300 text-[8px] font-mono text-center"
                      textAnchor="middle"
                    >
                      {rel.type}
                    </text>
                  )}
                </g>
              );
            })}
          </g>

          {/* Render Nodes */}
          <g>
            {nodes.map((node) => {
              const IconComp = getIcon(node.type);
              const classes = getAccentColor(node.type);
              const isSelected = selectedEntity?.id === node.id;

              return (
                <g 
                  key={node.id} 
                  transform={`translate(${node.x}, ${node.y})`}
                  onClick={() => onSelectEntity(node)}
                  className="cursor-pointer group"
                >
                  <circle
                    r={isSelected ? 22 : 18}
                    className={`transition-all duration-300 ${classes} ${
                      isSelected 
                        ? 'stroke-2 shadow-2xl drop-shadow-[0_0_10px_rgba(99,102,241,0.5)]' 
                        : 'stroke-1 group-hover:stroke-2 group-hover:scale-110'
                    }`}
                  />
                  <g transform="translate(-8, -8)" className="pointer-events-none">
                    <IconComp className={`w-4 h-4 text-zinc-300 ${isSelected ? 'text-white' : ''}`} />
                  </g>
                  <text
                    y={32}
                    textAnchor="middle"
                    className={`text-[9px] font-medium transition-colors ${
                      isSelected ? 'fill-indigo-300 font-bold' : 'fill-zinc-400 group-hover:fill-zinc-200'
                    }`}
                  >
                    {node.name}
                  </text>
                </g>
              );
            })}
          </g>
        </svg>
      </div>
    </div>
  );
}
