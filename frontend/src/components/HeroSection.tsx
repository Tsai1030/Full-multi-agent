"use client";
import Image from "next/image";
import Link from "next/link";
import { motion } from "framer-motion";

const fadeUp = (delay = 0) => ({
  initial: { opacity: 0, y: 30 },
  animate: { opacity: 1, y: 0 },
  transition: { duration: 0.8, delay, ease: [0.22, 1, 0.36, 1] },
});

export default function HeroSection() {
  return (
    <section className="relative min-h-screen flex flex-col items-center justify-center text-center z-10 px-4 pt-20">
      {/* Rotating mandala (background decoration) */}
      <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
        {/* Outer ring - slow rotate */}
        <motion.div
          initial={{ opacity: 0, scale: 0.6 }}
          animate={{ opacity: 0.18, scale: 1 }}
          transition={{ duration: 2.5, ease: "easeOut" }}
          className="absolute w-[70vmin] h-[70vmin] animate-rotate-slow"
        >
          <Image src="/icon2.png" alt="" fill className="object-contain" />
        </motion.div>
        {/* Inner ring - reverse rotate */}
        <motion.div
          initial={{ opacity: 0, scale: 0.4 }}
          animate={{ opacity: 0.25, scale: 1 }}
          transition={{ duration: 2.5, delay: 0.3, ease: "easeOut" }}
          className="absolute w-[45vmin] h-[45vmin] animate-reverse"
        >
          <Image src="/icon.png" alt="" fill className="object-contain" />
        </motion.div>
        {/* Expanding ring animations */}
        {[0, 1.2, 2.4].map((delay) => (
          <div
            key={delay}
            className="absolute w-[35vmin] h-[35vmin] rounded-full border border-gold-500/20"
            style={{
              animation: `ring-expand 4s ease-out ${delay}s infinite`,
              top: "50%",
              left: "50%",
            }}
          />
        ))}
        {/* Center glow */}
        <div
          className="absolute w-40 h-40 rounded-full"
          style={{
            background: "radial-gradient(circle, rgba(201,168,76,0.15) 0%, transparent 70%)",
            filter: "blur(20px)",
            animation: "pulse-glow 4s ease-in-out infinite",
          }}
        />
      </div>

      {/* Tagline */}
      <motion.p
        {...fadeUp(0.2)}
        className="text-xs tracking-[0.4em] text-gold-500 uppercase mb-6 font-sans"
      >
        AI · Multi-Agent · 紫微斗數
      </motion.p>

      {/* Main headline */}
      <motion.h1
        {...fadeUp(0.4)}
        className="font-serif text-5xl md:text-7xl font-bold leading-tight mb-6"
        style={{ textWrap: "balance" } as React.CSSProperties}
      >
        <span className="text-gold-gradient">探索命盤</span>
        <br />
        <span className="text-parchment">星象之謎</span>
      </motion.h1>

      {/* Sub headline */}
      <motion.p
        {...fadeUp(0.55)}
        className="max-w-xl text-parchment-dim text-lg leading-relaxed mb-10"
      >
        結合 AI 多智能體推理、RAG 知識庫與即時星象資料，
        <br className="hidden sm:block" />
        為您解析紫微斗數命盤的深層命理玄機
      </motion.p>

      {/* CTA */}
      <motion.div {...fadeUp(0.7)} className="flex flex-col sm:flex-row gap-4 items-center">
        <Link href="/analyze">
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.97 }}
            className="btn-gold px-10 py-4 rounded-full text-cosmos-950 font-bold text-lg tracking-wide"
            style={{
              animation: "pulse-glow 4s ease-in-out 1s infinite",
            }}
          >
            ✦ 立即推算命盤
          </motion.button>
        </Link>
        <button
          onClick={() =>
            document.getElementById("domains")?.scrollIntoView({ behavior: "smooth" })
          }
          className="btn-ghost-gold px-8 py-4 rounded-full text-sm tracking-widest"
        >
          了解更多 ↓
        </button>
      </motion.div>

      {/* Scroll indicator */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 1.5, duration: 1 }}
        className="absolute bottom-8 left-1/2 -translate-x-1/2 flex flex-col items-center gap-2"
      >
        <div className="w-px h-12 bg-gradient-to-b from-transparent via-gold-500/50 to-transparent animate-pulse" />
      </motion.div>
    </section>
  );
}
