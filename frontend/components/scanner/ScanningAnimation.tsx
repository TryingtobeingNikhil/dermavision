"use client";

import { motion } from "framer-motion";

export default function ScanningAnimation() {
  return (
    <div className="absolute inset-0 pointer-events-none">
      {/* Scanning Line */}
      <motion.div
        animate={{
          y: ["-100%", "100%"],
        }}
        transition={{
          duration: 2,
          repeat: Infinity,
          ease: "linear",
        }}
        className="absolute inset-x-0 h-1 bg-gradient-to-r from-transparent via-primary to-transparent"
        style={{
          boxShadow: "0 0 20px rgba(0, 217, 255, 0.8), 0 0 40px rgba(0, 217, 255, 0.5)",
        }}
      />

      {/* Grid Overlay */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: [0, 0.6, 0] }}
        transition={{
          duration: 2,
          repeat: Infinity,
        }}
        className="absolute inset-0"
        style={{
          backgroundImage: `
            linear-gradient(rgba(0, 217, 255, 0.3) 1px, transparent 1px),
            linear-gradient(90deg, rgba(0, 217, 255, 0.3) 1px, transparent 1px)
          `,
          backgroundSize: "20px 20px",
        }}
      />

      {/* Corner Brackets */}
      <div className="absolute inset-0">
        {/* Top Left */}
        <motion.div
          initial={{ opacity: 0, scale: 1.2 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.2 }}
          className="absolute top-4 left-4 w-12 h-12 border-t-2 border-l-2 border-primary"
        />
        
        {/* Top Right */}
        <motion.div
          initial={{ opacity: 0, scale: 1.2 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.4 }}
          className="absolute top-4 right-4 w-12 h-12 border-t-2 border-r-2 border-primary"
        />
        
        {/* Bottom Left */}
        <motion.div
          initial={{ opacity: 0, scale: 1.2 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.6 }}
          className="absolute bottom-4 left-4 w-12 h-12 border-b-2 border-l-2 border-primary"
        />
        
        {/* Bottom Right */}
        <motion.div
          initial={{ opacity: 0, scale: 1.2 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.8 }}
          className="absolute bottom-4 right-4 w-12 h-12 border-b-2 border-r-2 border-primary"
        />
      </div>

      {/* Pulse Rings */}
      <motion.div
        animate={{
          scale: [1, 1.5],
          opacity: [0.5, 0],
        }}
        transition={{
          duration: 2,
          repeat: Infinity,
        }}
        className="absolute inset-0 border-2 border-primary rounded-2xl"
      />
      
      <motion.div
        animate={{
          scale: [1, 1.5],
          opacity: [0.5, 0],
        }}
        transition={{
          duration: 2,
          repeat: Infinity,
          delay: 0.5,
        }}
        className="absolute inset-0 border-2 border-secondary rounded-2xl"
      />

      {/* Status Text */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: [0, 1, 0] }}
        transition={{
          duration: 2,
          repeat: Infinity,
        }}
        className="absolute top-6 left-6 glass px-4 py-2 rounded-full text-xs font-mono"
      >
        <span className="text-primary">● SCANNING</span>
      </motion.div>
    </div>
  );
}