"use client";

import { motion, useSpring, useTransform } from "framer-motion";
import { useEffect } from "react";

interface StatsWidgetProps {
  icon: React.ReactNode;
  label: string;
  value: number;
  format?: "percentage" | "decimal" | "integer";
  delay?: number;
  color?: "primary" | "secondary" | "accent";
  highlight?: boolean;
}

export default function StatsWidget({
  icon,
  label,
  value,
  format = "percentage",
  delay = 0,
  color = "primary",
  highlight = false,
}: StatsWidgetProps) {
  const spring = useSpring(0, { stiffness: 50, damping: 20 });
  
  const display = useTransform(spring, (val) => {
    if (format === "percentage") return `${(val * 100).toFixed(1)}%`;
    if (format === "decimal") return val.toFixed(3);
    return Math.round(val).toString();
  });

  useEffect(() => {
    setTimeout(() => spring.set(value), delay * 1000);
  }, [value, spring, delay]);

  const colorClasses = {
    primary: "text-primary border-primary/30 glow-primary",
    secondary: "text-secondary border-secondary/30 glow-secondary",
    accent: "text-accent border-accent/30 glow-danger",
  };

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.8 }}
      whileInView={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.5, delay }}
      viewport={{ once: true }}
      whileHover={{ 
        scale: 1.05, 
        y: -5,
      }}
      className={`
        glass-strong p-6 rounded-2xl relative overflow-hidden cursor-pointer
        ${highlight ? `border-2 ${colorClasses[color]}` : "border border-white/10"}
      `}
    >
      {/* Background Gradient */}
      {highlight && (
        <div className="absolute inset-0 holographic opacity-10" />
      )}

      {/* Icon */}
      <motion.div
        initial={{ rotate: 0 }}
        whileHover={{ rotate: 360 }}
        transition={{ duration: 0.6 }}
        className={`mb-3 ${colorClasses[color]}`}
      >
        {icon}
      </motion.div>

      {/* Value */}
      <motion.div className={`text-3xl font-bold mb-2 ${colorClasses[color]}`}>
        {display}
      </motion.div>

      {/* Label */}
      <div className="text-sm text-gray-400">{label}</div>

      {/* Pulse Effect for Highlight */}
      {highlight && (
        <motion.div
          animate={{
            scale: [1, 1.2, 1],
            opacity: [0.5, 0.8, 0.5],
          }}
          transition={{
            duration: 2,
            repeat: Infinity,
          }}
          className="absolute inset-0 border-2 border-accent/50 rounded-2xl"
        />
      )}
    </motion.div>
  );
}