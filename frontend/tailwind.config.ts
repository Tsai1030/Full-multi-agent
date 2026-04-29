import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        // Deep space palette
        cosmos: {
          950: "#04020F",
          900: "#080618",
          800: "#0D0B2B",
          700: "#140F38",
          600: "#1E1645",
        },
        // Gold palette
        gold: {
          DEFAULT: "#C9A84C",
          50:  "#FDF8EC",
          100: "#F9EDCA",
          200: "#F5E0A0",
          300: "#F0CE6E",
          400: "#E8B83A",
          500: "#C9A84C",
          600: "#A8822A",
          700: "#836219",
          800: "#60470F",
          900: "#3E2D08",
        },
        // Purple/violet accents
        mystic: {
          300: "#C4B5FD",
          400: "#A78BFA",
          500: "#8B5CF6",
          600: "#7C3AED",
          700: "#6D28D9",
        },
        // Text colors
        parchment: {
          DEFAULT: "#F5F0E8",
          dim: "#C8BFA8",
          muted: "#8B7EAA",
        },
      },
      fontFamily: {
        serif: ["Noto Serif TC", "Georgia", "serif"],
        sans:  ["Noto Sans TC", "system-ui", "sans-serif"],
      },
      backgroundImage: {
        "cosmic-bg": "url('/background.png')",
        "gold-gradient": "linear-gradient(135deg, #C9A84C 0%, #F0C040 50%, #A8822A 100%)",
        "gold-shine": "linear-gradient(90deg, transparent 0%, rgba(201,168,76,0.4) 50%, transparent 100%)",
        "card-glass": "linear-gradient(135deg, rgba(20,15,56,0.85) 0%, rgba(13,11,43,0.92) 100%)",
        "glow-radial": "radial-gradient(circle, rgba(201,168,76,0.15) 0%, transparent 70%)",
      },
      boxShadow: {
        "gold-sm":  "0 0 8px rgba(201,168,76,0.3)",
        "gold-md":  "0 0 20px rgba(201,168,76,0.4), 0 0 40px rgba(201,168,76,0.1)",
        "gold-lg":  "0 0 40px rgba(201,168,76,0.5), 0 0 80px rgba(201,168,76,0.2)",
        "purple-glow": "0 0 30px rgba(139,92,246,0.3)",
        "card":     "0 8px 32px rgba(0,0,0,0.5), inset 0 1px 0 rgba(201,168,76,0.1)",
      },
      animation: {
        "spin-slow":      "spin 30s linear infinite",
        "spin-medium":    "spin 15s linear infinite",
        "spin-reverse":   "spin-reverse 20s linear infinite",
        "float":          "float 6s ease-in-out infinite",
        "float-slow":     "float 10s ease-in-out infinite",
        "pulse-gold":     "pulse-gold 3s ease-in-out infinite",
        "twinkle":        "twinkle 4s ease-in-out infinite",
        "shimmer":        "shimmer 2.5s linear infinite",
        "fade-up":        "fade-up 0.7s ease-out forwards",
        "fade-in":        "fade-in 0.5s ease-out forwards",
        "slide-up":       "slide-up 0.6s cubic-bezier(0.34,1.56,0.64,1) forwards",
        "glow-pulse":     "glow-pulse 4s ease-in-out infinite",
        "ring-expand":    "ring-expand 2s ease-out infinite",
      },
      keyframes: {
        "spin-reverse": {
          from: { transform: "rotate(360deg)" },
          to:   { transform: "rotate(0deg)" },
        },
        float: {
          "0%, 100%": { transform: "translateY(0px)" },
          "50%":      { transform: "translateY(-16px)" },
        },
        "pulse-gold": {
          "0%, 100%": { boxShadow: "0 0 20px rgba(201,168,76,0.3)" },
          "50%":      { boxShadow: "0 0 50px rgba(201,168,76,0.7), 0 0 100px rgba(201,168,76,0.3)" },
        },
        twinkle: {
          "0%, 100%": { opacity: "0.3", transform: "scale(0.8)" },
          "50%":      { opacity: "1",   transform: "scale(1.2)" },
        },
        shimmer: {
          "0%":   { backgroundPosition: "-200% center" },
          "100%": { backgroundPosition: "200% center" },
        },
        "fade-up": {
          "0%":   { opacity: "0", transform: "translateY(24px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
        "fade-in": {
          "0%":   { opacity: "0" },
          "100%": { opacity: "1" },
        },
        "slide-up": {
          "0%":   { opacity: "0", transform: "translateY(40px) scale(0.97)" },
          "100%": { opacity: "1", transform: "translateY(0) scale(1)" },
        },
        "glow-pulse": {
          "0%, 100%": { opacity: "0.4" },
          "50%":      { opacity: "1" },
        },
        "ring-expand": {
          "0%":   { transform: "scale(0.8)", opacity: "0.8" },
          "100%": { transform: "scale(1.8)", opacity: "0" },
        },
      },
      backdropBlur: {
        xs: "2px",
      },
    },
  },
  plugins: [],
};

export default config;
