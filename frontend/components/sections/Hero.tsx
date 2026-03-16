"use client";

import { useEffect, useState } from "react";
import { ArrowRight, ChevronDown } from "lucide-react";
import { cn } from "@/lib/utils";

export function Hero() {
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    const timer = setTimeout(() => setIsVisible(true), 100);
    return () => clearTimeout(timer);
  }, []);

  const scrollTo = (id: string) => {
    document.getElementById(id)?.scrollIntoView({ behavior: "smooth" });
  };

  return (
    <section
      className="relative min-h-screen flex items-center justify-center overflow-hidden"
      aria-label="Hero"
    >
      {/* ── Animated Background ── */}
      <div className="absolute inset-0 pointer-events-none" aria-hidden="true">
        {/* Grid overlay */}
        <div className="absolute inset-0 bg-grid opacity-30" />

        {/* Gradient orbs */}
        <div
          className="absolute top-1/4 left-1/4 w-[500px] h-[500px] rounded-full bg-blue-500/15 blur-[120px]"
          style={{ animation: "orbFloat1 8s ease-in-out infinite" }}
        />
        <div
          className="absolute bottom-1/4 right-1/4 w-[400px] h-[400px] rounded-full bg-cyan-400/10 blur-[100px]"
          style={{ animation: "orbFloat2 10s ease-in-out infinite" }}
        />
        <div
          className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[300px] h-[300px] rounded-full bg-teal-500/8 blur-[80px]"
          style={{ animation: "orbFloat1 12s ease-in-out infinite reverse" }}
        />

        {/* Radial fade at bottom */}
        <div className="absolute bottom-0 inset-x-0 h-40 bg-gradient-to-t from-slate-950 to-transparent" />
      </div>

      {/* ── Content ── */}
      <div className="relative z-10 max-w-5xl mx-auto px-4 sm:px-6 text-center pt-24 pb-16">
        {/* Overline */}
        <div
          className={cn(
            "inline-flex items-center gap-2 px-4 py-1.5 glass-card rounded-full text-sm text-cyan-400 font-medium mb-8",
            "opacity-0 translate-y-6 transition-all duration-700 ease-out",
            isVisible && "opacity-100 translate-y-0"
          )}
        >
          <span className="w-1.5 h-1.5 rounded-full bg-cyan-400 animate-pulse-dot" />
          AI-Powered Dermatology
        </div>

        {/* Headline */}
        <h1
          className={cn(
            "font-display font-bold tracking-tight leading-[1.1]",
            "text-4xl sm:text-5xl md:text-6xl lg:text-7xl",
            "mb-6",
            "opacity-0 translate-y-6 transition-all duration-700 ease-out delay-100",
            isVisible && "opacity-100 translate-y-0"
          )}
        >
          Detect Skin Lesions{" "}
          <br className="hidden sm:block" />
          with{" "}
          <span className="gradient-text-animated">
            Confidence
          </span>
        </h1>

        {/* Subheadline */}
        <p
          className={cn(
            "text-lg sm:text-xl text-slate-400 max-w-2xl mx-auto mb-10 leading-relaxed",
            "opacity-0 translate-y-6 transition-all duration-700 ease-out delay-200",
            isVisible && "opacity-100 translate-y-0"
          )}
        >
          Upload a dermatoscopic image and get instant, explainable AI
          classification across 7 skin conditions — powered by EfficientNet-B3 and
          the HAM10000 dataset.
        </p>

        {/* CTAs */}
        <div
          className={cn(
            "flex flex-col sm:flex-row items-center justify-center gap-4 mb-14",
            "opacity-0 translate-y-6 transition-all duration-700 ease-out delay-300",
            isVisible && "opacity-100 translate-y-0"
          )}
        >
          <button
            onClick={() => scrollTo("scanner")}
            className={cn(
              "group relative overflow-hidden",
              "inline-flex items-center gap-2.5",
              "px-8 py-4 rounded-xl",
              "bg-gradient-to-r from-blue-500 to-cyan-400",
              "text-white font-semibold text-lg",
              "shadow-glow hover:shadow-glow-strong",
              "hover:scale-105 active:scale-95",
              "transition-all duration-300 focus-ring"
            )}
          >
            <span
              className="absolute inset-0 bg-white/0 group-hover:bg-white/10 transition-all duration-300"
              aria-hidden="true"
            />
            Try Demo
            <ArrowRight className="w-5 h-5 group-hover:translate-x-0.5 transition-transform" />
          </button>

          <button
            onClick={() => scrollTo("how-it-works")}
            className={cn(
              "inline-flex items-center gap-2",
              "px-8 py-4 rounded-xl",
              "glass-card text-slate-300 font-semibold text-lg",
              "hover:text-cyan-400 hover:border-cyan-400/30 hover:shadow-glow",
              "hover:scale-105 active:scale-95",
              "transition-all duration-300 focus-ring"
            )}
          >
            Learn More
          </button>
        </div>

        {/* Trust Indicators */}
        <div
          className={cn(
            "flex flex-wrap items-center justify-center gap-3",
            "opacity-0 translate-y-6 transition-all duration-700 ease-out delay-[400ms]",
            isVisible && "opacity-100 translate-y-0"
          )}
        >
          {[
            { label: "85.6% Accuracy", dot: "bg-emerald-400" },
            { label: "10K+ Images", dot: "bg-blue-400" },
            { label: "Medical-Grade AI", dot: "bg-cyan-400" },
          ].map((pill) => (
            <span
              key={pill.label}
              className="inline-flex items-center gap-2 px-4 py-2 glass-card rounded-full text-sm text-slate-300 font-medium"
            >
              <span
                className={cn("w-1.5 h-1.5 rounded-full", pill.dot)}
                aria-hidden="true"
              />
              {pill.label}
            </span>
          ))}
        </div>
      </div>

      {/* Scroll indicator */}
      <div
        className={cn(
          "absolute bottom-8 left-1/2 -translate-x-1/2",
          "opacity-0 transition-all duration-700 delay-[600ms]",
          isVisible && "opacity-100"
        )}
      >
        <button
          onClick={() => scrollTo("scanner")}
          className="text-slate-500 hover:text-cyan-400 transition-colors animate-float focus-ring rounded-full p-2"
          aria-label="Scroll to scanner section"
        >
          <ChevronDown className="w-6 h-6" />
        </button>
      </div>
    </section>
  );
}
