"use client";

import React from "react";
import { cn } from "@/lib/utils";

// ── Types ──────────────────────────────────────────────────────

export interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  /** Enable hover scale + glow effect */
  hoverable?: boolean;
  /** Apply glow-pulse animation */
  glowing?: boolean;
  padding?: "none" | "sm" | "md" | "lg";
}

const paddingStyles = {
  none: "",
  sm: "p-4",
  md: "p-6",
  lg: "p-8",
};

// ── Component ──────────────────────────────────────────────────

export function Card({
  children,
  hoverable = false,
  glowing = false,
  padding = "md",
  className,
  ...props
}: CardProps) {
  return (
    <div
      className={cn(
        "glass-card",
        paddingStyles[padding],
        hoverable && [
          "cursor-pointer",
          "hover:scale-[1.03] hover:shadow-glow hover:border-cyan-400/30",
          "transition-all duration-300",
        ],
        glowing && "animate-glow-pulse",
        className
      )}
      {...props}
    >
      {children}
    </div>
  );
}

// ── Sub-components ─────────────────────────────────────────────

export function CardHeader({ children, className, ...props }: React.HTMLAttributes<HTMLDivElement>) {
  return (
    <div className={cn("mb-4", className)} {...props}>
      {children}
    </div>
  );
}

export function CardTitle({ children, className, ...props }: React.HTMLAttributes<HTMLHeadingElement>) {
  return (
    <h3 className={cn("text-lg font-semibold font-display text-slate-100", className)} {...props}>
      {children}
    </h3>
  );
}

export function CardBody({ children, className, ...props }: React.HTMLAttributes<HTMLDivElement>) {
  return (
    <div className={cn("text-slate-300", className)} {...props}>
      {children}
    </div>
  );
}