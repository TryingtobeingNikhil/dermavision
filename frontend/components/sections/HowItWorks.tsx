"use client";

import { useEffect, useRef, useState } from "react";
import { Upload, Brain, ScanSearch, CheckCircle, ArrowRight } from "lucide-react";
import { cn } from "@/lib/utils";
import { HOW_IT_WORKS_STEPS } from "@/lib/constants";

const iconMap: Record<string, React.ReactNode> = {
  Upload: <Upload className="w-6 h-6" />,
  Brain: <Brain className="w-6 h-6" />,
  ScanSearch: <ScanSearch className="w-6 h-6" />,
  CheckCircle: <CheckCircle className="w-6 h-6" />,
};

export function HowItWorks() {
  const ref = useRef<HTMLDivElement>(null);
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => { if (entry.isIntersecting) setIsVisible(true); },
      { threshold: 0.15 }
    );
    if (ref.current) observer.observe(ref.current);
    return () => observer.disconnect();
  }, []);

  return (
    <section
      id="how-it-works"
      ref={ref}
      className="relative py-24"
      aria-label="How it works"
    >
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Section header */}
        <div className="text-center mb-16">
          <span className="text-sm font-medium text-cyan-400 tracking-wider uppercase mb-3 block">
            Process
          </span>
          <h2 className="text-3xl sm:text-4xl md:text-5xl font-display font-bold mb-4">
            How It{" "}
            <span className="gradient-text">Works</span>
          </h2>
          <p className="text-slate-400 text-lg max-w-2xl mx-auto">
            From image upload to AI-powered diagnosis in four simple steps
          </p>
        </div>

        {/* Steps */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 lg:gap-4">
          {HOW_IT_WORKS_STEPS.map((step, i) => (
            <div key={step.number} className="relative flex flex-col items-center">
              {/* Connector arrow (hidden on last item and on mobile) */}
              {i < HOW_IT_WORKS_STEPS.length - 1 && (
                <div className="hidden lg:flex absolute top-12 -right-2 z-10 text-slate-600" aria-hidden="true">
                  <ArrowRight className="w-4 h-4" />
                </div>
              )}

              {/* Card */}
              <div
                className={cn(
                  "glass-card p-8 rounded-2xl text-center w-full",
                  "hover:scale-[1.04] hover:shadow-glow hover:border-cyan-400/30",
                  "transition-all duration-500 group",
                  "opacity-0 translate-y-8",
                  isVisible && "opacity-100 translate-y-0"
                )}
                style={{
                  transitionDelay: isVisible ? `${i * 120}ms` : "0ms",
                }}
              >
                {/* Number badge */}
                <div className="text-xs font-mono font-bold text-cyan-400/50 mb-4 tracking-widest">
                  {step.number}
                </div>

                {/* Icon */}
                <div className="w-14 h-14 mx-auto mb-5 rounded-2xl bg-gradient-to-br from-blue-500/20 to-cyan-400/20 flex items-center justify-center text-cyan-400 group-hover:shadow-glow transition-all duration-300">
                  {iconMap[step.icon]}
                </div>

                {/* Title */}
                <h3 className="text-lg font-display font-semibold text-slate-100 mb-3">
                  {step.title}
                </h3>

                {/* Description */}
                <p className="text-sm text-slate-400 leading-relaxed">
                  {step.description}
                </p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
