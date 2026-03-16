"use client";

import React, { createContext, useCallback, useContext, useEffect, useReducer } from "react";
import { CheckCircle, AlertTriangle, XCircle, Info, X } from "lucide-react";
import { cn } from "@/lib/utils";

// ── Types ──────────────────────────────────────────────────────

export type ToastType = "success" | "error" | "warning" | "info";

export interface Toast {
  id: string;
  type: ToastType;
  message: string;
  duration?: number;
}

type ToastAction =
  | { type: "ADD"; toast: Toast }
  | { type: "REMOVE"; id: string };

// ── Context ────────────────────────────────────────────────────

interface ToastContextValue {
  showToast: (type: ToastType, message: string, duration?: number) => void;
}

const ToastContext = createContext<ToastContextValue | null>(null);

export function useToast() {
  const ctx = useContext(ToastContext);
  if (!ctx) throw new Error("useToast must be used within <ToastProvider>");
  return ctx;
}

// ── Reducer ────────────────────────────────────────────────────

function toastReducer(state: Toast[], action: ToastAction): Toast[] {
  switch (action.type) {
    case "ADD":
      return [...state, action.toast];
    case "REMOVE":
      return state.filter((t) => t.id !== action.id);
    default:
      return state;
  }
}

// ── Provider ───────────────────────────────────────────────────

export function ToastProvider({ children }: { children: React.ReactNode }) {
  const [toasts, dispatch] = useReducer(toastReducer, []);

  const showToast = useCallback(
    (type: ToastType, message: string, duration = 5000) => {
      const id = `toast-${Date.now()}-${Math.random().toString(36).slice(2)}`;
      const toast: Toast = { id, type, message, duration };
      dispatch({ type: "ADD", toast });
    },
    []
  );

  return (
    <ToastContext.Provider value={{ showToast }}>
      {children}
      <ToastContainer toasts={toasts} onRemove={(id) => dispatch({ type: "REMOVE", id })} />
    </ToastContext.Provider>
  );
}

// ── Toast Container ────────────────────────────────────────────

function ToastContainer({
  toasts,
  onRemove,
}: {
  toasts: Toast[];
  onRemove: (id: string) => void;
}) {
  return (
    <div
      aria-live="polite"
      aria-atomic="false"
      className="fixed bottom-6 right-6 z-[9999] flex flex-col gap-3 max-w-sm w-full pointer-events-none"
    >
      {toasts.map((toast) => (
        <ToastItem key={toast.id} toast={toast} onRemove={onRemove} />
      ))}
    </div>
  );
}

// ── Toast Item ─────────────────────────────────────────────────

const toastConfig: Record<ToastType, { icon: React.ReactNode; classes: string }> = {
  success: {
    icon: <CheckCircle className="w-5 h-5 text-emerald-400 shrink-0" />,
    classes: "border-emerald-500/30 bg-emerald-500/10",
  },
  error: {
    icon: <XCircle className="w-5 h-5 text-red-400 shrink-0" />,
    classes: "border-red-500/30 bg-red-500/10",
  },
  warning: {
    icon: <AlertTriangle className="w-5 h-5 text-amber-400 shrink-0" />,
    classes: "border-amber-500/30 bg-amber-500/10",
  },
  info: {
    icon: <Info className="w-5 h-5 text-blue-400 shrink-0" />,
    classes: "border-blue-500/30 bg-blue-500/10",
  },
};

function ToastItem({ toast, onRemove }: { toast: Toast; onRemove: (id: string) => void }) {
  useEffect(() => {
    const timer = setTimeout(() => onRemove(toast.id), toast.duration ?? 5000);
    return () => clearTimeout(timer);
  }, [toast, onRemove]);

  const { icon, classes } = toastConfig[toast.type];

  return (
    <div
      role="alert"
      className={cn(
        "pointer-events-auto",
        "flex items-start gap-3 p-4 rounded-xl",
        "backdrop-blur-xl border",
        "shadow-glass",
        "toast-enter",
        classes
      )}
    >
      {icon}
      <p className="text-sm text-slate-200 flex-1 leading-snug">{toast.message}</p>
      <button
        onClick={() => onRemove(toast.id)}
        aria-label="Dismiss notification"
        className="shrink-0 text-slate-400 hover:text-slate-200 transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-cyan-400 rounded"
      >
        <X className="w-4 h-4" />
      </button>
    </div>
  );
}
