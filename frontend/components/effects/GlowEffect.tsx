"use client";

import { motion } from "framer-motion";
import { useEffect, useState } from "react";

interface GlowEffectProps {
  children: React.ReactNode;
  color?: "primary" | "secondary" | "accent";
  intensity?: "low" | "medium" | "high";
  pulse?: boolean;
}

export default function GlowEffect({ 
  children, 
  color = "primary", 
  intensity = "medium",
  pulse = false 
}: GlowEffectProps) {
  const glowColors = {
    primary: "rgba(0, 217, 255, 0.6)",
    secondary: "rgba(184, 48, 255, 0.6)",
    accent: "rgba(255, 0, 110, 0.6)",
  };

  const intensityValues = {
    low: { blur: 10, spread: 20 },
    medium: { blur: 20, spread: 40 },
    high: { blur: 30, spread: 60 },
  };

  const { blur, spread } = intensityValues[intensity];
  const glowColor = glowColors[color];

  const glowStyle = {
    filter: `drop-shadow(0 0 ${blur}px ${glowColor}) drop-shadow(0 0 ${spread}px ${glowColor})`,
  };

  return (
    <motion.div
      style={glowStyle}
      animate={
        pulse
          ? {
              filter: [
                `drop-shadow(0 0 ${blur}px ${glowColor}) drop-shadow(0 0 ${spread}px ${glowColor})`,
                `drop-shadow(0 0 ${blur * 1.5}px ${glowColor}) drop-shadow(0 0 ${spread * 1.5}px ${glowColor})`,
                `drop-shadow(0 0 ${blur}px ${glowColor}) drop-shadow(0 0 ${spread}px ${glowColor})`,
              ],
            }
          : {}
      }
      transition={
        pulse
          ? {
              duration: 2,
              repeat: Infinity,
              ease: "easeInOut",
            }
          : {}
      }
    >
      {children}
    </motion.div>
  );
}

// Ambient Glow Background Component
export function AmbientGlow({ position = "top-left" }: { position?: "top-left" | "top-right" | "bottom-left" | "bottom-right" | "center" }) {
  const positions = {
    "top-left": "top-0 left-0",
    "top-right": "top-0 right-0",
    "bottom-left": "bottom-0 left-0",
    "bottom-right": "bottom-0 right-0",
    "center": "top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2",
  };

  return (
    <motion.div
      animate={{
        scale: [1, 1.2, 1],
        opacity: [0.3, 0.5, 0.3],
      }}
      transition={{
        duration: 8,
        repeat: Infinity,
        ease: "easeInOut",
      }}
      className={`absolute ${positions[position]} w-96 h-96 bg-primary/30 rounded-full blur-3xl pointer-events-none`}
    />
  );
}