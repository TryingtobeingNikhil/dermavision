"use client";

import React from "react";
import { cn } from "@/lib/utils";

// ── Types ──────────────────────────────────────────────────────

export type ButtonVariant = "primary" | "secondary" | "ghost" | "danger";
export type ButtonSize = "sm" | "md" | "lg";

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: ButtonVariant;
  size?: ButtonSize;
  isLoading?: boolean;
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
  children: React.ReactNode;
}

// ── Variant styles ─────────────────────────────────────────────

const variantStyles: Record<ButtonVariant, string> = {
  primary: [
    "relative overflow-hidden",
    "bg-gradient-to-r from-blue-500 to-cyan-400",
    "text-white font-semibold",
    "shadow-glow hover:shadow-glow-strong",
    "hover:scale-[1.03] active:scale-[0.97]",
    "before:absolute before:inset-0 before:bg-white/0 before:transition-all before:duration-300",
    "hover:before:bg-white/10",
  ].join(" "),

  secondary: [
    "glass-card",
    "text-slate-100 font-semibold",
    "border border-white/10 hover:border-cyan-400/40",
    "hover:scale-[1.03] active:scale-[0.97]",
    "hover:shadow-glow",
  ].join(" "),

  ghost: [
    "bg-transparent",
    "text-slate-300 font-medium",
    "hover:text-cyan-400 hover:bg-white/5",
    "active:bg-white/10",
  ].join(" "),

  danger: [
    "relative overflow-hidden",
    "bg-gradient-to-r from-red-600 to-rose-500",
    "text-white font-semibold",
    "hover:scale-[1.03] active:scale-[0.97]",
    "before:absolute before:inset-0 before:bg-white/0 before:transition-all before:duration-300",
    "hover:before:bg-white/10",
  ].join(" "),
};

const sizeStyles: Record<ButtonSize, string> = {
  sm: "px-4 py-2 text-sm rounded-lg gap-1.5",
  md: "px-6 py-3 text-base rounded-xl gap-2",
  lg: "px-8 py-4 text-lg rounded-xl gap-2.5",
};

// ── Component ──────────────────────────────────────────────────

export function Button({
  variant = "primary",
  size = "md",
  isLoading = false,
  leftIcon,
  rightIcon,
  children,
  className,
  disabled,
  ...props
}: ButtonProps) {
  const isDisabled = disabled || isLoading;

  return (
    <button
      className={cn(
        "inline-flex items-center justify-center",
        "transition-all duration-300",
        "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-cyan-400 focus-visible:ring-offset-2 focus-visible:ring-offset-slate-950",
        "disabled:opacity-50 disabled:cursor-not-allowed disabled:pointer-events-none",
        variantStyles[variant],
        sizeStyles[size],
        className
      )}
      disabled={isDisabled}
      aria-busy={isLoading}
      {...props}
    >
      {isLoading ? (
        <svg
          className="animate-spin h-4 w-4 text-current"
          xmlns="http://www.w3.org/2000/svg"
          fill="none"
          viewBox="0 0 24 24"
          aria-hidden="true"
        >
          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
        </svg>
      ) : (
        leftIcon && <span aria-hidden="true">{leftIcon}</span>
      )}
      {children}
      {!isLoading && rightIcon && <span aria-hidden="true">{rightIcon}</span>}
    </button>
  );
}