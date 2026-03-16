"use client";

import { motion, useSpring, useTransform } from "framer-motion";
import { useEffect } from "react";

interface ConfidenceCounterProps {
  confidence: number;
  uncertain: boolean;
}

export default function ConfidenceCounter({ confidence, uncertain }: ConfidenceCounterProps) {
  const spring = useSpring(0, { stiffness: 50, damping: 20 });
  const display = useTransform(spring, (value) => 
    `${(value * 100).toFixed(1)}%`
  );

  useEffect(() => {
    spring.set(confidence);
  }, [confidence, spring]);

  const getColor = () => {
    if (confidence >= 0.8) return "text-green-400";
    if (confidence >= 0.6) return "text-yellow-400";
    return "text-red-400";
  };

  const getGlowColor = () => {
    if (confidence >= 0.8) return "glow-primary";
    if (confidence >= 0.6) return "glow-danger";
    return "glow-danger";
  };

  return (
    <div className="text-center">
      <p className="text-sm text-gray-400 mb-3 uppercase tracking-wider">
        Confidence Level
      </p>
      
      {/* Animated Counter */}
      <motion.div
        initial={{ scale: 0 }}
        animate={{ scale: 1 }}
        transition={{ type: "spring", stiffness: 200, delay: 1 }}
        className={`text-7xl font-bold mb-4 ${getColor()}`}
      >
        <motion.span className={getGlowColor()}>
          {display}
        </motion.span>
      </motion.div>

      {/* Progress Bar */}
      <div className="relative h-3 bg-white/10 rounded-full overflow-hidden">
        <motion.div
          initial={{ width: 0 }}
          animate={{ width: `${confidence * 100}%` }}
          transition={{ duration: 1.5, ease: "easeOut", delay: 1 }}
          className={`
            absolute inset-y-0 left-0 rounded-full
            ${confidence >= 0.8 
              ? "bg-gradient-to-r from-green-500 to-green-400" 
              : confidence >= 0.6
              ? "bg-gradient-to-r from-yellow-500 to-yellow-400"
              : "bg-gradient-to-r from-red-500 to-red-400"
            }
          `}
          style={{
            boxShadow: confidence >= 0.8
              ? "0 0 20px rgba(34, 197, 94, 0.6)"
              : confidence >= 0.6
              ? "0 0 20px rgba(234, 179, 8, 0.6)"
              : "0 0 20px rgba(239, 68, 68, 0.6)",
          }}
        />

        {/* Threshold Marker */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 1.5 }}
          className="absolute top-0 bottom-0 border-l-2 border-white/50"
          style={{ left: "60%" }}
        >
          <div className="absolute -top-8 left-1/2 -translate-x-1/2 glass px-2 py-1 rounded text-xs whitespace-nowrap">
            60% threshold
          </div>
        </motion.div>
      </div>

      {/* Status Badge */}
      <motion.div
        initial={{ opacity: 0, scale: 0.8 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ delay: 1.8 }}
        className="mt-4"
      >
        <div className={`
          inline-block px-4 py-2 rounded-full text-sm font-semibold
          ${uncertain 
            ? "bg-yellow-500/20 text-yellow-400 border border-yellow-500/50" 
            : "bg-green-500/20 text-green-400 border border-green-500/50"
          }
        `}>
          {uncertain ? "Below Threshold" : "Above Threshold"}
        </div>
      </motion.div>
    </div>
  );
}