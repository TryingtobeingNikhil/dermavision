"use client";

import { useEffect, useRef, useState } from "react";
import { TrendingUp, ShieldCheck, Database, Zap } from "lucide-react";
import { cn } from "@/lib/utils";
import { STATS } from "@/lib/constants";

const iconMap: Record<string, React.ReactNode> = {
  TrendingUp: <TrendingUp className="w-6 h-6" />,
  ShieldCheck: <ShieldCheck className="w-6 h-6" />,
  Database: <Database className="w-6 h-6" />,
  Zap: <Zap className="w-6 h-6" />,
};

export function Stats() {
  const ref = useRef<HTMLDivElement>(null);
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => { if (entry.isIntersecting) setIsVisible(true); },
      { threshold: 0.2 }
    );
    if (ref.current) observer.observe(ref.current);
    return () => observer.disconnect();
  }, []);

  return (
    <section ref={ref} className="relative py-8" aria-label="Key metrics">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 md:gap-6">
          {STATS.map((stat, i) => (
            <div
              key={stat.id}
              className={cn(
                "glass-card p-6 rounded-2xl text-center",
                "hover:scale-[1.04] hover:shadow-glow hover:border-cyan-400/30",
                "transition-all duration-300 group cursor-default",
                "opacity-0 translate-y-6",
                isVisible && "opacity-100 translate-y-0"
              )}
              style={{
                transitionDelay: isVisible ? `${i * 100}ms` : "0ms",
                transitionDuration: "600ms",
              }}
            >
              {/* Icon */}
              <div className="w-12 h-12 mx-auto mb-4 rounded-xl bg-gradient-to-br from-blue-500/20 to-cyan-400/20 flex items-center justify-center text-cyan-400 group-hover:shadow-glow transition-all duration-300">
                {iconMap[stat.icon]}
              </div>

              {/* Value */}
              <div className="text-3xl md:text-4xl font-display font-bold gradient-text mb-1">
                {stat.value}
              </div>

              {/* Label */}
              <div className="text-sm font-medium text-slate-300 mb-1">
                {stat.label}
              </div>

              {/* Description */}
              <div className="text-xs text-slate-500">
                {stat.description}
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
