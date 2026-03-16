"use client";

import { useEffect, useRef, useState } from "react";
import {
  Cpu, Target, Eye, Gauge, Database, Zap, Sparkles, Server,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { FEATURES } from "@/lib/constants";

const iconMap: Record<string, React.ReactNode> = {
  Cpu: <Cpu className="w-6 h-6" />,
  Target: <Target className="w-6 h-6" />,
  Eye: <Eye className="w-6 h-6" />,
  Gauge: <Gauge className="w-6 h-6" />,
  Database: <Database className="w-6 h-6" />,
  Zap: <Zap className="w-6 h-6" />,
  Sparkles: <Sparkles className="w-6 h-6" />,
  Server: <Server className="w-6 h-6" />,
};

export function Features() {
  const ref = useRef<HTMLDivElement>(null);
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => { if (entry.isIntersecting) setIsVisible(true); },
      { threshold: 0.1 }
    );
    if (ref.current) observer.observe(ref.current);
    return () => observer.disconnect();
  }, []);

  return (
    <section
      id="features"
      ref={ref}
      className="relative py-24"
      aria-label="Features"
    >
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Section header */}
        <div className="text-center mb-16">
          <span className="text-sm font-medium text-cyan-400 tracking-wider uppercase mb-3 block">
            Technology
          </span>
          <h2 className="text-3xl sm:text-4xl md:text-5xl font-display font-bold mb-4">
            Powered by{" "}
            <span className="gradient-text">Innovation</span>
          </h2>
          <p className="text-slate-400 text-lg max-w-2xl mx-auto">
            Cutting-edge deep learning techniques engineered for clinical-grade accuracy
          </p>
        </div>

        {/* Feature grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
          {FEATURES.map((feature, i) => (
            <div
              key={feature.id}
              className={cn(
                "glass-card p-6 rounded-2xl",
                "hover:scale-[1.04] hover:shadow-glow hover:border-cyan-400/30",
                "transition-all duration-500 group cursor-default",
                "opacity-0 translate-y-8",
                isVisible && "opacity-100 translate-y-0"
              )}
              style={{
                transitionDelay: isVisible ? `${i * 80}ms` : "0ms",
              }}
            >
              {/* Icon with unique gradient bg */}
              <div
                className={cn(
                  "w-12 h-12 rounded-xl flex items-center justify-center mb-5",
                  "bg-gradient-to-br text-cyan-400",
                  "group-hover:shadow-glow transition-all duration-300",
                  feature.gradient
                )}
              >
                {iconMap[feature.icon]}
              </div>

              {/* Title */}
              <h3 className="text-base font-display font-semibold text-slate-100 mb-2">
                {feature.title}
              </h3>

              {/* Description */}
              <p className="text-sm text-slate-400 leading-relaxed">
                {feature.description}
              </p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
