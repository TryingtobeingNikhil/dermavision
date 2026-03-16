"use client";

import { Github, Twitter, Linkedin, Activity, ExternalLink } from "lucide-react";
import { FOOTER_LINKS, STATS } from "@/lib/constants";

export function Footer() {
  return (
    <footer id="about" className="relative mt-24 border-t border-white/8">
      {/* Gradient top accent */}
      <div
        className="absolute top-0 inset-x-0 h-px bg-gradient-to-r from-transparent via-cyan-400/50 to-transparent"
        aria-hidden="true"
      />

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-16 pb-8">

        {/* ── Metrics Bar ── */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-16 p-6 glass-card rounded-2xl">
          {STATS.map((stat) => (
            <div key={stat.id} className="text-center">
              <div className="text-2xl font-bold font-display gradient-text">{stat.value}</div>
              <div className="text-xs text-slate-500 mt-1">{stat.label}</div>
            </div>
          ))}
        </div>

        {/* ── Main footer grid ── */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-12 mb-12">

          {/* Brand column */}
          <div className="md:col-span-1">
            <div className="flex items-center gap-2.5 mb-4">
              <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-blue-500 to-cyan-400 flex items-center justify-center shadow-glow">
                <Activity className="w-4 h-4 text-white" />
              </div>
              <span className="font-display font-bold text-lg tracking-tight">
                Derma<span className="gradient-text">Vision</span>
              </span>
            </div>
            <p className="text-sm text-slate-400 leading-relaxed mb-6">
              AI-powered skin lesion classification for research and education. Not a substitute for professional medical advice.
            </p>
            <div className="flex gap-3">
              {[
                { icon: Github, href: "https://github.com", label: "GitHub" },
                { icon: Twitter, href: "https://twitter.com", label: "Twitter" },
                { icon: Linkedin, href: "https://linkedin.com", label: "LinkedIn" },
              ].map(({ icon: Icon, href, label }) => (
                <a
                  key={label}
                  href={href}
                  target="_blank"
                  rel="noopener noreferrer"
                  aria-label={label}
                  className="w-9 h-9 glass-card rounded-lg flex items-center justify-center text-slate-400 hover:text-cyan-400 hover:border-cyan-400/30 transition-all duration-300 focus-ring"
                >
                  <Icon className="w-4 h-4" />
                </a>
              ))}
            </div>
          </div>

          {/* Link columns */}
          {Object.entries(FOOTER_LINKS).map(([section, links]) => (
            <div key={section}>
              <h4 className="text-sm font-semibold text-slate-300 mb-4 font-display">{section}</h4>
              <ul className="space-y-3">
                {links.map((link) => (
                  <li key={link.label}>
                    <a
                      href={link.href}
                      target={link.href.startsWith("http") ? "_blank" : undefined}
                      rel={link.href.startsWith("http") ? "noopener noreferrer" : undefined}
                      className="text-sm text-slate-400 hover:text-cyan-400 transition-colors inline-flex items-center gap-1.5 group focus-ring rounded"
                    >
                      {link.label}
                      {link.href.startsWith("http") && (
                        <ExternalLink className="w-3 h-3 opacity-0 group-hover:opacity-100 transition-opacity" aria-hidden="true" />
                      )}
                    </a>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>

        {/* ── Bottom bar ── */}
        <div className="border-t border-white/8 pt-8 flex flex-col sm:flex-row items-center justify-between gap-4">
          <p className="text-xs text-slate-500">
            © 2026 DermaVision. Built with PyTorch, FastAPI &amp; Next.js 14.
          </p>
          <p
            id="disclaimer"
            className="text-xs text-slate-500 max-w-md text-center sm:text-right"
          >
            ⚕️ For educational and research purposes only. Not FDA approved. Always consult a qualified dermatologist.
          </p>
        </div>
      </div>
    </footer>
  );
}
