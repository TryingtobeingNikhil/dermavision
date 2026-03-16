import type { Config } from "tailwindcss";

const config: Config = {
  darkMode: ["class"],
  content: [
    "./pages/**/*.{ts,tsx}",
    "./components/**/*.{ts,tsx}",
    "./app/**/*.{ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        border: "hsl(217.2 32.6% 17.5%)",
        background: "hsl(222.2 84% 4.9%)",
        foreground: "hsl(210 40% 98%)",
        // Clinical Futurism palette
        primary: {
          DEFAULT: "#3B82F6",
          dark: "#2563EB",
        },
        cyan: {
          400: "#22D3EE",
          500: "#06B6D4",
        },
        teal: {
          500: "#14B8A6",
        },
        slate: {
          950: "#0F172A",
          900: "#1E293B",
          800: "#1E293B",
          700: "#334155",
          600: "#475569",
          500: "#64748B",
          400: "#94A3B8",
          100: "#F1F5F9",
        },
      },
      fontFamily: {
        display: ["var(--font-display)", "system-ui", "sans-serif"],
        body: ["var(--font-body)", "system-ui", "sans-serif"],
        mono: ["var(--font-mono)", "monospace"],
      },
      animation: {
        "fade-in-up": "fadeInUp 0.6s ease-out forwards",
        "scan-line": "scanLine 2s ease-in-out infinite",
        shimmer: "shimmer 3s linear infinite",
        "glow-pulse": "glowPulse 2s ease-in-out infinite",
        float: "float 4s ease-in-out infinite",
        "rotate-slow": "rotateSlow 20s linear infinite",
        "gradient-shift": "gradientShift 4s ease infinite",
        "scanner-sweep": "scannerSweep 2s ease-in-out infinite",
        "pulse-dot": "pulseDot 1.5s ease-in-out infinite",
      },
      keyframes: {
        fadeInUp: {
          "0%": { opacity: "0", transform: "translateY(24px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
        scanLine: {
          "0%, 100%": { transform: "translateY(-100%)", opacity: "0" },
          "10%, 90%": { opacity: "1" },
          "50%": { opacity: "1" },
        },
        shimmer: {
          "0%": { backgroundPosition: "-200% center" },
          "100%": { backgroundPosition: "200% center" },
        },
        glowPulse: {
          "0%, 100%": { boxShadow: "0 0 20px rgba(34, 211, 238, 0.3)" },
          "50%": { boxShadow: "0 0 40px rgba(34, 211, 238, 0.6)" },
        },
        float: {
          "0%, 100%": { transform: "translateY(0px)" },
          "50%": { transform: "translateY(-16px)" },
        },
        rotateSlow: {
          "0%": { transform: "rotate(0deg)" },
          "100%": { transform: "rotate(360deg)" },
        },
        gradientShift: {
          "0%, 100%": { backgroundPosition: "0% 50%" },
          "50%": { backgroundPosition: "100% 50%" },
        },
        scannerSweep: {
          "0%": { top: "0%", opacity: "0" },
          "10%": { opacity: "1" },
          "90%": { opacity: "1" },
          "100%": { top: "100%", opacity: "0" },
        },
        pulseDot: {
          "0%, 100%": { opacity: "0.4", transform: "scale(0.8)" },
          "50%": { opacity: "1", transform: "scale(1.2)" },
        },
      },
      backgroundImage: {
        "gradient-radial": "radial-gradient(var(--tw-gradient-stops))",
        "gradient-primary": "linear-gradient(135deg, #3B82F6 0%, #22D3EE 100%)",
        "gradient-accent": "linear-gradient(135deg, #22D3EE 0%, #14B8A6 100%)",
        "grid-lines":
          "linear-gradient(rgba(59,130,246,0.04) 1px, transparent 1px), linear-gradient(90deg, rgba(59,130,246,0.04) 1px, transparent 1px)",
      },
      backgroundSize: {
        grid: "60px 60px",
      },
      boxShadow: {
        glow: "0 0 20px rgba(34, 211, 238, 0.3)",
        "glow-strong": "0 0 40px rgba(34, 211, 238, 0.5)",
        "glow-blue": "0 0 24px rgba(59, 130, 246, 0.4)",
        glass: "0 8px 32px rgba(0, 0, 0, 0.4)",
      },
    },
  },
  plugins: [require("tailwindcss-animate")],
};

export default config;