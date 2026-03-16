"use client";

import React from "react";
import { cn } from "@/lib/utils";

export interface SkeletonProps extends React.HTMLAttributes<HTMLDivElement> {
  /** Shape variant */
  variant?: "rect" | "circle";
}

export function Skeleton({ variant = "rect", className, ...props }: SkeletonProps) {
  return (
    <div
      aria-hidden="true"
      className={cn(
        "relative overflow-hidden",
        "bg-slate-700/50",
        variant === "circle" ? "rounded-full" : "rounded-lg",
        // Shimmer effect
        "before:absolute before:inset-0",
        "before:bg-gradient-to-r before:from-transparent before:via-white/5 before:to-transparent",
        "before:animate-shimmer before:bg-[length:200%_100%]",
        className
      )}
      {...props}
    />
  );
}

/** Skeleton for a card-shaped block */
export function SkeletonCard({ className }: { className?: string }) {
  return (
    <div className={cn("glass-card p-6 space-y-4", className)}>
      <Skeleton className="h-4 w-2/3" />
      <Skeleton className="h-3 w-full" />
      <Skeleton className="h-3 w-4/5" />
    </div>
  );
}
