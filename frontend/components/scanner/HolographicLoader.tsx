"use client";

import { motion } from "framer-motion";

export default function HolographicLoader() {
  return (
    <div className="relative w-32 h-32 mx-auto mb-8">
      {/* Outer Ring */}
      <motion.div
        animate={{ rotate: 360 }}
        transition={{ duration: 3, repeat: Infinity, ease: "linear" }}
        className="absolute inset-0 border-4 border-primary/30 border-t-primary rounded-full"
      />

      {/* Middle Ring */}
      <motion.div
        animate={{ rotate: -360 }}
        transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
        className="absolute inset-2 border-4 border-secondary/30 border-t-secondary rounded-full"
      />

      {/* Inner Ring */}
      <motion.div
        animate={{ rotate: 360 }}
        transition={{ duration: 1.5, repeat: Infinity, ease: "linear" }}
        className="absolute inset-4 border-4 border-accent/30 border-t-accent rounded-full"
      />

      {/* Center Dot */}
      <motion.div
        animate={{
          scale: [1, 1.2, 1],
          opacity: [0.5, 1, 0.5],
        }}
        transition={{
          duration: 1.5,
          repeat: Infinity,
        }}
        className="absolute inset-0 flex items-center justify-center"
      >
        <div className="w-8 h-8 bg-primary rounded-full glow-primary" />
      </motion.div>

      {/* Orbiting Particles */}
      {[...Array(6)].map((_, i) => (
        <motion.div
          key={i}
          animate={{
            rotate: 360,
          }}
          transition={{
            duration: 4,
            repeat: Infinity,
            ease: "linear",
            delay: i * 0.2,
          }}
          className="absolute inset-0"
        >
          <div
            className="absolute w-2 h-2 bg-primary rounded-full"
            style={{
              top: "50%",
              left: "100%",
              transform: "translate(-50%, -50%)",
            }}
          />
        </motion.div>
      ))}
    </div>
  );
}