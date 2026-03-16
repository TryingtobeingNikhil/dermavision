"use client";

import { motion } from "framer-motion";
import { Brain, Shield, Zap, Activity, Target, Sparkles } from "lucide-react";

export default function FloatingElements() {
  const elements = [
    { Icon: Brain, x: "10%", y: "20%", delay: 0, scale: 1 },
    { Icon: Shield, x: "80%", y: "30%", delay: 0.5, scale: 0.8 },
    { Icon: Zap, x: "15%", y: "70%", delay: 1, scale: 1.2 },
    { Icon: Activity, x: "85%", y: "60%", delay: 1.5, scale: 0.9 },
    { Icon: Target, x: "50%", y: "15%", delay: 2, scale: 1.1 },
    { Icon: Sparkles, x: "50%", y: "85%", delay: 2.5, scale: 0.7 },
  ];

  return (
    <div className="absolute inset-0 pointer-events-none overflow-hidden">
      {elements.map(({ Icon, x, y, delay, scale }, index) => (
        <motion.div
          key={index}
          initial={{ opacity: 0, scale: 0 }}
          animate={{ 
            opacity: [0, 0.3, 0],
            scale: [0, scale, 0],
            rotate: [0, 180, 360],
          }}
          transition={{
            duration: 8,
            repeat: Infinity,
            delay: delay,
            ease: "easeInOut",
          }}
          style={{
            position: "absolute",
            left: x,
            top: y,
          }}
          className="text-primary"
        >
          <Icon className="w-16 h-16" />
        </motion.div>
      ))}

      {/* Floating particles */}
      {Array.from({ length: 20 }).map((_, i) => (
        <motion.div
          key={`particle-${i}`}
          initial={{
            x: `${Math.random() * 100}%`,
            y: `${Math.random() * 100}%`,
            opacity: 0,
          }}
          animate={{
            y: [`${Math.random() * 100}%`, `${Math.random() * 100}%`],
            opacity: [0, Math.random() * 0.5, 0],
          }}
          transition={{
            duration: Math.random() * 10 + 10,
            repeat: Infinity,
            delay: Math.random() * 5,
          }}
          className="absolute w-2 h-2 bg-primary rounded-full"
          style={{
            boxShadow: "0 0 10px rgba(0, 217, 255, 0.8)",
          }}
        />
      ))}

      {/* Orbiting rings */}
      <motion.div
        animate={{ rotate: 360 }}
        transition={{ duration: 30, repeat: Infinity, ease: "linear" }}
        className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-96 h-96 border border-primary/20 rounded-full"
      />
      <motion.div
        animate={{ rotate: -360 }}
        transition={{ duration: 40, repeat: Infinity, ease: "linear" }}
        className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[500px] h-[500px] border border-secondary/20 rounded-full"
      />
    </div>
  );
}

// Individual floating card component
export function FloatingCard({ 
  children, 
  delay = 0,
  amplitude = 20 
}: { 
  children: React.ReactNode; 
  delay?: number;
  amplitude?: number;
}) {
  return (
    <motion.div
      animate={{
        y: [0, -amplitude, 0],
        rotate: [0, 2, 0, -2, 0],
      }}
      transition={{
        duration: 4,
        repeat: Infinity,
        delay,
        ease: "easeInOut",
      }}
    >
      {children}
    </motion.div>
  );
}