"use client";

import { useRef } from "react";
import { Canvas, useFrame } from "@react-three/fiber";
import { OrbitControls, Sphere } from "@react-three/drei";
import * as THREE from "three";

function NeuralNetwork() {
  const groupRef = useRef<THREE.Group>(null);
  
  // Create neural network nodes
  const nodes = Array.from({ length: 50 }, () => ({
    position: [
      (Math.random() - 0.5) * 8,
      (Math.random() - 0.5) * 8,
      (Math.random() - 0.5) * 8,
    ] as [number, number, number],
  }));

  useFrame((state) => {
    if (groupRef.current) {
      groupRef.current.rotation.x = state.clock.elapsedTime * 0.05;
      groupRef.current.rotation.y = state.clock.elapsedTime * 0.08;
    }
  });

  return (
    <group ref={groupRef}>
      {nodes.map((node, i) => (
        <Sphere key={i} args={[0.05, 16, 16]} position={node.position}>
          <meshStandardMaterial 
            color="#00d9ff" 
            emissive="#00d9ff" 
            emissiveIntensity={0.5}
            transparent
            opacity={0.6}
          />
        </Sphere>
      ))}
      
      {/* Connection lines */}
      {nodes.slice(0, 20).map((node, i) => {
        const nextNode = nodes[(i + 1) % nodes.length];
        const points = [
          new THREE.Vector3(...node.position),
          new THREE.Vector3(...nextNode.position),
        ];
        const geometry = new THREE.BufferGeometry().setFromPoints(points);
        
        return (
          <line key={`line-${i}`} geometry={geometry}>
            <lineBasicMaterial color="#00d9ff" transparent opacity={0.2} />
          </line>
        );
      })}
    </group>
  );
}

export default function NeuralBackground() {
  return (
    <Canvas camera={{ position: [0, 0, 10], fov: 60 }}>
      <ambientLight intensity={0.5} />
      <pointLight position={[10, 10, 10]} intensity={1} />
      <NeuralNetwork />
      <OrbitControls enableZoom={false} enablePan={false} autoRotate autoRotateSpeed={0.5} />
    </Canvas>
  );
}