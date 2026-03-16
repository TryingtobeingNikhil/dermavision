"use client";

import { motion, AnimatePresence } from "framer-motion";
import { useState } from "react";

interface Ripple {
  id: number;
  x: number;
  y: number;
}

interface RippleEffectProps {
  children: React.ReactNode;
  color?: string;
  duration?: number;
}

export default function RippleEffect({ 
  children, 
  color = "rgba(0, 217, 255, 0.4)",
  duration = 0.6 
}: RippleEffectProps) {
  const [ripples, setRipples] = useState<Ripple[]>([]);

  const handleClick = (e: React.MouseEvent<HTMLDivElement>) => {
    const rect = e.currentTarget.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;

    const newRipple: Ripple = {
      id: Date.now(),
      x,
      y,
    };

    setRipples((prev) => [...prev, newRipple]);

    // Remove ripple after animation
    setTimeout(() => {
      setRipples((prev) => prev.filter((r) => r.id !== newRipple.id));
    }, duration * 1000);
  };

  return (
    <div 
      className="relative overflow-hidden cursor-pointer"
      onClick={handleClick}
    >
      {children}
      
      <AnimatePresence>
        {ripples.map((ripple) => (
          <motion.span
            key={ripple.id}
            initial={{
              scale: 0,
              opacity: 1,
            }}
            animate={{
              scale: 4,
              opacity: 0,
            }}
            exit={{
              opacity: 0,
            }}
            transition={{
              duration: duration,
              ease: "easeOut",
            }}
            style={{
              position: "absolute",
              left: ripple.x,
              top: ripple.y,
              width: 20,
              height: 20,
              borderRadius: "50%",
              backgroundColor: color,
              transform: "translate(-50%, -50%)",
              pointerEvents: "none",
            }}
          />
        ))}
      </AnimatePresence>
    </div>
  );
}

// Pre-configured ripple buttons
export function RippleButton({ 
  children, 
  onClick,
  className = "",
  variant = "primary"
}: { 
  children: React.ReactNode; 
  onClick?: () => void;
  className?: string;
  variant?: "primary" | "secondary" | "accent";
}) {
  const colors = {
    primary: "rgba(0, 217, 255, 0.4)",
    secondary: "rgba(184, 48, 255, 0.4)",
    accent: "rgba(255, 0, 110, 0.4)",
  };

  return (
    <RippleEffect color={colors[variant]}>
      <motion.button
        whileHover={{ scale: 1.05 }}
        whileTap={{ scale: 0.95 }}
        onClick={onClick}
        className={`glass-strong px-8 py-4 rounded-2xl font-semibold transition-all ${className}`}
      >
        {children}
      </motion.button>
    </RippleEffect>
  );
}