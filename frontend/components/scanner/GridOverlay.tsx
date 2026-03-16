"use client";

import { motion } from "framer-motion";

interface GridOverlayProps {
  cellSize?: number;
  color?: string;
  opacity?: number;
  animated?: boolean;
}

export default function GridOverlay({ 
  cellSize = 20, 
  color = "rgba(0, 217, 255, 0.3)",
  opacity = 0.6,
  animated = true
}: GridOverlayProps) {
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: animated ? [0, opacity, 0] : opacity }}
      transition={
        animated
          ? {
              duration: 2,
              repeat: Infinity,
            }
          : {}
      }
      className="absolute inset-0 pointer-events-none"
      style={{
        backgroundImage: `
          linear-gradient(${color} 1px, transparent 1px),
          linear-gradient(90deg, ${color} 1px, transparent 1px)
        `,
        backgroundSize: `${cellSize}px ${cellSize}px`,
      }}
    />
  );
}

// Animated scanning grid
export function ScanningGrid() {
  return (
    <div className="absolute inset-0 pointer-events-none overflow-hidden">
      {/* Vertical scanning line */}
      <motion.div
        animate={{
          x: ["-100%", "100%"],
        }}
        transition={{
          duration: 3,
          repeat: Infinity,
          ease: "linear",
        }}
        className="absolute inset-y-0 w-1 bg-gradient-to-b from-transparent via-primary to-transparent"
        style={{
          boxShadow: "0 0 20px rgba(0, 217, 255, 0.8)",
        }}
      />

      {/* Horizontal scanning line */}
      <motion.div
        animate={{
          y: ["-100%", "100%"],
        }}
        transition={{
          duration: 2,
          repeat: Infinity,
          ease: "linear",
        }}
        className="absolute inset-x-0 h-1 bg-gradient-to-r from-transparent via-secondary to-transparent"
        style={{
          boxShadow: "0 0 20px rgba(184, 48, 255, 0.8)",
        }}
      />

      {/* Grid cells */}
      <GridOverlay cellSize={30} />

      {/* Radial pulse from center */}
      <motion.div
        animate={{
          scale: [0, 2],
          opacity: [0.5, 0],
        }}
        transition={{
          duration: 2,
          repeat: Infinity,
        }}
        className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-40 h-40 border-2 border-primary rounded-full"
      />
    </div>
  );
}