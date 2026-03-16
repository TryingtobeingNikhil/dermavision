"use client";

import { useEffect, useState } from "react";
import { Menu, X, Activity } from "lucide-react";
import { cn } from "@/lib/utils";
import { NAV_LINKS } from "@/lib/constants";

export function Navigation() {
  const [isScrolled, setIsScrolled] = useState(false);
  const [mobileOpen, setMobileOpen] = useState(false);
  const [activeSection, setActiveSection] = useState<string>("");

  // ── Scroll tracking ────────────────────────────────────────

  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 20);

      // Update active section on scroll
      const sections = NAV_LINKS.map((l) => l.href.replace("#", ""));
      for (const id of [...sections].reverse()) {
        const el = document.getElementById(id);
        if (el && el.getBoundingClientRect().top <= 120) {
          setActiveSection(id);
          break;
        }
      }
    };

    window.addEventListener("scroll", handleScroll, { passive: true });
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  // Lock body scroll when mobile menu is open
  useEffect(() => {
    document.body.style.overflow = mobileOpen ? "hidden" : "";
    return () => { document.body.style.overflow = ""; };
  }, [mobileOpen]);

  const handleNavClick = (href: string) => {
    setMobileOpen(false);
    const id = href.replace("#", "");
    document.getElementById(id)?.scrollIntoView({ behavior: "smooth" });
  };

  return (
    <>
      {/* ── Header ── */}
      <header
        className={cn(
          "fixed top-0 inset-x-0 z-50 transition-all duration-500",
          isScrolled ? "glass-nav-scrolled shadow-glass" : "glass-nav"
        )}
        role="banner"
      >
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">

            {/* Logo */}
            <a
              href="#"
              onClick={(e) => { e.preventDefault(); window.scrollTo({ top: 0, behavior: "smooth" }); }}
              className="flex items-center gap-2.5 focus-ring group"
              aria-label="DermaVision home"
            >
              <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-blue-500 to-cyan-400 flex items-center justify-center shadow-glow group-hover:shadow-glow-strong transition-all duration-300">
                <Activity className="w-4 h-4 text-white" />
              </div>
              <span className="font-display font-bold text-lg tracking-tight">
                Derma<span className="gradient-text">Vision</span>
              </span>
            </a>

            {/* Desktop nav */}
            <nav aria-label="Main navigation" className="hidden md:flex items-center gap-1">
              {NAV_LINKS.map((link) => {
                const sectionId = link.href.replace("#", "");
                const isActive = activeSection === sectionId;
                return (
                  <a
                    key={link.href}
                    href={link.href}
                    onClick={(e) => { e.preventDefault(); handleNavClick(link.href); }}
                    className={cn(
                      "relative px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200 focus-ring",
                      isActive
                        ? "text-cyan-400"
                        : "text-slate-400 hover:text-slate-100 hover:bg-white/5"
                    )}
                    aria-current={isActive ? "page" : undefined}
                  >
                    {link.label}
                    {isActive && (
                      <span
                        className="absolute bottom-0.5 left-1/2 -translate-x-1/2 w-1 h-1 rounded-full bg-cyan-400"
                        aria-hidden="true"
                      />
                    )}
                  </a>
                );
              })}
            </nav>

            {/* CTA + Hamburger */}
            <div className="flex items-center gap-3">
              <a
                href="#scanner"
                onClick={(e) => { e.preventDefault(); handleNavClick("#scanner"); }}
                className={cn(
                  "hidden md:inline-flex items-center gap-2",
                  "px-4 py-2 rounded-xl text-sm font-semibold",
                  "bg-gradient-to-r from-blue-500 to-cyan-400 text-white",
                  "shadow-glow hover:shadow-glow-strong hover:scale-105 active:scale-95",
                  "transition-all duration-300 focus-ring"
                )}
              >
                Try Demo
              </a>

              <button
                onClick={() => setMobileOpen(!mobileOpen)}
                className="md:hidden p-2 rounded-lg text-slate-400 hover:text-slate-100 hover:bg-white/5 transition-colors focus-ring"
                aria-label={mobileOpen ? "Close menu" : "Open menu"}
                aria-expanded={mobileOpen}
                aria-controls="mobile-nav"
              >
                {mobileOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* ── Mobile drawer ── */}
      <div
        id="mobile-nav"
        className={cn(
          "fixed inset-0 z-40 md:hidden transition-all duration-300",
          mobileOpen ? "opacity-100 pointer-events-auto" : "opacity-0 pointer-events-none"
        )}
        aria-hidden={!mobileOpen}
      >
        {/* Backdrop */}
        <div
          className="absolute inset-0 bg-slate-950/80 backdrop-blur-sm"
          onClick={() => setMobileOpen(false)}
          aria-hidden="true"
        />

        {/* Panel */}
        <nav
          aria-label="Mobile navigation"
          className={cn(
            "absolute top-0 right-0 h-full w-72 max-w-full",
            "bg-slate-900 border-l border-white/10",
            "flex flex-col pt-20 p-6",
            "transition-transform duration-300 ease-out",
            mobileOpen ? "translate-x-0" : "translate-x-full"
          )}
        >
          <div className="flex flex-col gap-1">
            {NAV_LINKS.map((link) => (
              <a
                key={link.href}
                href={link.href}
                onClick={(e) => { e.preventDefault(); handleNavClick(link.href); }}
                className="px-4 py-3 rounded-xl text-slate-300 hover:text-cyan-400 hover:bg-white/5 font-medium transition-all duration-200 focus-ring"
              >
                {link.label}
              </a>
            ))}
          </div>

          <div className="mt-auto">
            <a
              href="#scanner"
              onClick={(e) => { e.preventDefault(); handleNavClick("#scanner"); }}
              className="flex items-center justify-center w-full px-6 py-3 rounded-xl font-semibold bg-gradient-to-r from-blue-500 to-cyan-400 text-white shadow-glow transition-all duration-300 focus-ring"
            >
              Try Demo
            </a>
          </div>
        </nav>
      </div>
    </>
  );
}
