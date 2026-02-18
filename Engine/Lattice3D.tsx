import React, { useMemo } from 'react';
import { Canvas } from '@react-three/fiber';
import { OrbitControls, Environment, PerspectiveCamera, Stars } from '@react-three/drei';
import { MemoryNode } from './MemoryNode';
import { generateLatticeData } from '../services/mockDataService';
import { MemoryNodeData, ArcType } from '../types';

interface Lattice3DProps {
  onNodeSelect: (node: MemoryNodeData | null) => void;
  selectedNodeId: string | null;
  activeArc: ArcType | null;
  visibleLayer: number; // 0 = All, 1..7 = Specific Layers
}

export const Lattice3D: React.FC<Lattice3DProps> = ({ 
  onNodeSelect, 
  selectedNodeId, 
  activeArc,
  visibleLayer 
}) => {
  // Memoize raw data
  const allNodes = useMemo(() => generateLatticeData(), []);

  // Filter visible nodes based on layer selector
  const visibleNodes = useMemo(() => {
    if (visibleLayer === 0) return allNodes;

    // visibleLayer 1 corresponds to Y = -3 (Bottom)
    // visibleLayer 7 corresponds to Y = +3 (Top)
    // Formula: targetY = visibleLayer - 4
    const targetY = visibleLayer - 4;
    
    return allNodes.filter(node => node.coordinate.y === targetY);
  }, [allNodes, visibleLayer]);

  return (
    <Canvas className="w-full h-full bg-slate-950">
      <PerspectiveCamera makeDefault position={[12, 10, 12]} fov={50} />
      <OrbitControls 
        enablePan={true} 
        enableZoom={true} 
        enableRotate={true}
        autoRotate={!selectedNodeId}
        autoRotateSpeed={0.5}
        dampingFactor={0.05}
      />
      
      <ambientLight intensity={0.4} />
      <pointLight position={[10, 10, 10]} intensity={1} color="#ffffff" />
      <pointLight position={[-10, -10, -10]} intensity={0.5} color="#38bdf8" />
      
      <Stars radius={100} depth={50} count={5000} factor={4} saturation={0} fade speed={1} />
      <Environment preset="city" />

      <group 
        onPointerMissed={(e) => {
           if (e.type === 'click') {
             onNodeSelect(null);
           }
        }}
      >
        {visibleNodes.map((node) => (
          <MemoryNode
            key={node.id}
            data={node}
            isSelected={node.id === selectedNodeId}
            activeArc={activeArc}
            onSelect={onNodeSelect}
          />
        ))}
        
        {/* Helper plane to visualize the active layer level if in single-layer mode */}
        {visibleLayer !== 0 && (
          <gridHelper 
            args={[15, 15, 0x1e293b, 0x0f172a]} 
            position={[0, (visibleLayer - 4) * 1.5 - 0.5, 0]} 
          />
        )}

        {/* Central Axis visualizer for orientation */}
        <axesHelper args={[5]} />
      </group>
    </Canvas>
  );
};