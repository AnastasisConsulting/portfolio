
import React, { useState, useMemo, useEffect } from 'react';
import { MemoryNode, ContentRegistry, FaceType } from '../types';

interface LatticeVisualizerProps {
  lattice: MemoryNode[]; // The currently viewed lattice (or quantum slice)
  totalLattices: number; // Total count of lattices in memory
  currentViewIndex: number; // Which lattice index we are viewing (ignored in Quantum Mode)
  isQuantumMode: boolean;
  registry: ContentRegistry;
  onNodeClick: (node: MemoryNode) => void;
  onChangeLatticeView: (index: number) => void;
}

export const LatticeVisualizer: React.FC<LatticeVisualizerProps> = ({
  lattice,
  totalLattices,
  currentViewIndex,
  isQuantumMode,
  registry,
  onNodeClick,
  onChangeLatticeView
}) => {
  const [activeZ, setActiveZ] = useState(0);
  const [hoveredNode, setHoveredNode] = useState<string | null>(null);

  // Reset Z when switching lattices (optional, but good UX)
  useEffect(() => {
    setActiveZ(0);
  }, [currentViewIndex]);

  // Construct the 7x7 grid for the current view
  const grid = useMemo(() => {
    const map = new Map<string, MemoryNode>();
    
    lattice.forEach(node => {
      if (isQuantumMode) {
        // In quantum mode, we just fill a 7x7 grid linearly based on relevance rank
        const index = lattice.indexOf(node);
        const qy = Math.floor(index / 7);
        const qx = index % 7;
        map.set(`${qx},${qy}`, node);
      } else {
        // In physical mode, we filter by the active Z layer
        if (node.z === activeZ) {
          map.set(`${node.x},${node.y}`, node);
        }
      }
    });
    return map;
  }, [lattice, isQuantumMode, activeZ]);

  const renderGridCell = (x: number, y: number) => {
    const node = grid.get(`${x},${y}`);
    const isPopulated = !!node;
    const isHovered = hoveredNode === `${x},${y}`;

    // Get Scene Summary for tooltip if populated
    const sceneSummary = node ? registry[node.faces[FaceType.TOP]] : '';

    return (
      <div
        key={`${x}-${y}`}
        onClick={() => node && onNodeClick(node)}
        onMouseEnter={() => setHoveredNode(`${x},${y}`)}
        onMouseLeave={() => setHoveredNode(null)}
        className={`
          relative w-full h-full aspect-square border transition-all duration-300 cursor-pointer
          flex items-center justify-center
          ${isPopulated 
            ? isQuantumMode 
                ? 'bg-purple-900/20 border-purple-500/50 hover:bg-purple-500/30 hover:shadow-[0_0_15px_rgba(168,85,247,0.5)]' 
                : 'bg-cyan-900/20 border-cyan-500/50 hover:bg-cyan-500/30 hover:shadow-[0_0_15px_rgba(6,182,212,0.5)]' 
            : 'border-white/5 bg-transparent'}
        `}
      >
        {isPopulated && (
          <>
            <div className={`w-2 h-2 rounded-full ${isQuantumMode ? 'bg-purple-400' : 'bg-cyan-400'} animate-pulse`} />
            
            {/* Mini Information Overlay on Hover */}
            <div className={`
                absolute bottom-full left-1/2 -translate-x-1/2 mb-2 w-48 p-2 
                bg-black/90 border border-white/20 text-[10px] text-white z-20 pointer-events-none
                transition-opacity duration-200 rounded
                ${isHovered ? 'opacity-100' : 'opacity-0'}
            `}>
                <div className="font-bold mb-1 text-xs text-gray-400">
                    {isQuantumMode ? `RANK: ${(y * 7) + x + 1}` : `POS: [${x},${y},${activeZ}]`}
                    <span className="ml-2 opacity-50">LATTICE:{node.latticeIndex}</span>
                </div>
                <div className="line-clamp-3 text-gray-200">
                    {sceneSummary || "Unindexed"}
                </div>
            </div>
          </>
        )}
        
        {/* Grid Coordinate Label (faint) */}
        {!isPopulated && (
           <span className="text-[8px] text-white/10">{x},{y}</span>
        )}
      </div>
    );
  };

  return (
    <div className="flex flex-col h-full w-full p-4">
      {/* Header / Controls */}
      <div className="flex justify-between items-end mb-4 min-h-[4rem]">
        <div className="flex flex-col">
          <h2 className={`text-2xl font-bold tracking-tighter ${isQuantumMode ? 'text-purple-400 holo-text' : 'text-cyan-400 holo-text'}`}>
            {isQuantumMode ? 'QUANTUM SLICE' : `LATTICE #${currentViewIndex}`}
          </h2>
          <p className="text-xs text-neutral-500 font-mono mt-1">
            {isQuantumMode 
              ? 'Superposition: Top 49 vectors across ALL history' 
              : `Physical Storage Layer Z=${activeZ}`}
          </p>
        </div>

        {/* Navigation Controls */}
        {!isQuantumMode && (
          <div className="flex flex-col items-end gap-2 w-1/3">
             
             {/* Lattice Switcher */}
             <div className="flex items-center gap-2 text-xs font-mono">
                <button 
                    onClick={() => onChangeLatticeView(Math.max(0, currentViewIndex - 1))}
                    disabled={currentViewIndex === 0}
                    className="px-2 py-1 border border-cyan-900 text-cyan-500 hover:border-cyan-500 disabled:opacity-30"
                >
                    &lt; PREV
                </button>
                <span className="text-cyan-700">{currentViewIndex + 1} / {totalLattices}</span>
                <button 
                    onClick={() => onChangeLatticeView(Math.min(totalLattices - 1, currentViewIndex + 1))}
                    disabled={currentViewIndex === totalLattices - 1}
                    className="px-2 py-1 border border-cyan-900 text-cyan-500 hover:border-cyan-500 disabled:opacity-30"
                >
                    NEXT &gt;
                </button>
             </div>

             {/* Z-Axis Slider */}
            <div className="flex flex-col w-full">
                <div className="flex justify-between w-full text-[10px] text-cyan-600 font-mono">
                <span>Z=0</span>
                <span>Z=6</span>
                </div>
                <input
                type="range"
                min="0"
                max="6"
                step="1"
                value={activeZ}
                onChange={(e) => setActiveZ(parseInt(e.target.value))}
                className="w-full h-2 bg-neutral-800 rounded-lg appearance-none cursor-pointer accent-cyan-500"
                />
            </div>
          </div>
        )}
      </div>

      {/* The 7x7 Grid */}
      <div className="flex-1 grid grid-cols-7 grid-rows-7 gap-2 p-4 border border-white/10 rounded-xl bg-black/20 backdrop-blur-sm relative overflow-hidden">
         {/* Decorative background lines */}
         <div className="absolute inset-0 pointer-events-none bg-[linear-gradient(rgba(255,255,255,0.02)_1px,transparent_1px),linear-gradient(90deg,rgba(255,255,255,0.02)_1px,transparent_1px)] bg-[size:14.28%_14.28%]"></div>
         
         {Array.from({ length: 7 }).map((_, y) => (
            Array.from({ length: 7 }).map((_, x) => renderGridCell(x, y))
         ))}
      </div>
      
      {/* Stats Footer */}
      <div className="mt-4 flex justify-between text-[10px] text-neutral-600 font-mono uppercase">
          <span>Active View: {isQuantumMode ? 'GLOBAL' : `LATTICE ${currentViewIndex}`}</span>
          <span>Cap: {Math.round((lattice.length / 343) * 100)}%</span>
          <span>Mode: {isQuantumMode ? 'ASSOCIATIVE' : 'LINEAR'}</span>
      </div>
    </div>
  );
};
