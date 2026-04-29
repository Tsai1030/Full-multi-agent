"use client";
import { useEffect, useState } from "react";
import Image from "next/image";
import { motion, AnimatePresence } from "framer-motion";
import { LOADING_MESSAGES } from "@/lib/constants";

export default function DivinationLoader() {
  const [msgIndex, setMsgIndex] = useState(0);
  const [progress, setProgress] = useState(0);

  useEffect(() => {
    const msgTimer = setInterval(() => {
      setMsgIndex((i) => (i + 1) % LOADING_MESSAGES.length);
    }, 2800);

    const progressTimer = setInterval(() => {
      setProgress((p) => Math.min(p + Math.random() * 4, 92));
    }, 400);

    return () => {
      clearInterval(msgTimer);
      clearInterval(progressTimer);
    };
  }, []);

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      transition={{ duration: 0.5 }}
      className="fixed inset-0 z-40 flex flex-col items-center justify-center"
      style={{ background: "rgba(4,2,15,0.85)", backdropFilter: "blur(12px)" }}
    >
      {/* Particle rings */}
      {[0, 1, 2].map((i) => (
        <div
          key={i}
          className="absolute rounded-full border border-gold-500/20"
          style={{
            width: `${28 + i * 14}vmin`,
            height: `${28 + i * 14}vmin`,
            top: "50%",
            left: "50%",
            animation: `ring-expand ${3 + i * 0.8}s ease-out ${i * 1.2}s infinite`,
          }}
        />
      ))}

      {/* Outer ring - slow */}
      <motion.div
        animate={{ rotate: 360 }}
        transition={{ duration: 30, repeat: Infinity, ease: "linear" }}
        className="absolute w-72 h-72 opacity-20"
      >
        <Image src="/icon2.png" alt="" fill className="object-contain" />
      </motion.div>

      {/* Middle ring - medium reverse */}
      <motion.div
        animate={{ rotate: -360 }}
        transition={{ duration: 18, repeat: Infinity, ease: "linear" }}
        className="absolute w-52 h-52 opacity-30"
      >
        <Image src="/icon.png" alt="" fill className="object-contain" />
      </motion.div>

      {/* Inner glow orb */}
      <motion.div
        animate={{ scale: [1, 1.15, 1], opacity: [0.6, 1, 0.6] }}
        transition={{ duration: 3, repeat: Infinity, ease: "easeInOut" }}
        className="absolute w-28 h-28 rounded-full"
        style={{
          background:
            "radial-gradient(circle, rgba(240,192,64,0.35) 0%, rgba(201,168,76,0.1) 60%, transparent 100%)",
          boxShadow: "0 0 60px rgba(201,168,76,0.4), 0 0 120px rgba(201,168,76,0.15)",
        }}
      />

      {/* Center icon (removebg - transparent) */}
      <div className="relative w-20 h-20 z-10">
        <Image
          src="/icon-removebg-preview.png"
          alt="推算中"
          fill
          className="object-contain"
          style={{ filter: "drop-shadow(0 0 20px rgba(201,168,76,0.8))" }}
        />
      </div>

      {/* Status message */}
      <div className="relative z-10 mt-16 text-center">
        <AnimatePresence mode="wait">
          <motion.p
            key={msgIndex}
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -12 }}
            transition={{ duration: 0.5, ease: "easeOut" }}
            className="font-serif text-xl text-parchment tracking-wider"
          >
            {LOADING_MESSAGES[msgIndex]}
          </motion.p>
        </AnimatePresence>

        {/* Progress bar */}
        <div className="mt-6 w-56 mx-auto h-px bg-white/10 rounded-full overflow-hidden">
          <motion.div
            className="h-full rounded-full"
            style={{
              background: "linear-gradient(90deg, #8A6B2A, #C9A84C, #F0C040)",
              width: `${progress}%`,
            }}
            animate={{ width: `${progress}%` }}
            transition={{ ease: "easeOut" }}
          />
        </div>

        <p className="mt-3 text-xs text-parchment-muted tracking-widest">
          AI Multi-Agent 正在分析…
        </p>
      </div>

      {/* Corner decorations */}
      {["top-8 left-8", "top-8 right-8", "bottom-8 left-8", "bottom-8 right-8"].map((pos) => (
        <div
          key={pos}
          className={`absolute ${pos} w-6 h-6 opacity-30`}
          style={{
            background:
              "radial-gradient(circle, rgba(201,168,76,0.6) 0%, transparent 70%)",
            borderRadius: "50%",
            animation: "twinkle 3s ease-in-out infinite",
          }}
        />
      ))}
    </motion.div>
  );
}
