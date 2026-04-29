"use client";
import Link from "next/link";
import Image from "next/image";
import { motion } from "framer-motion";

export default function Navbar() {
  return (
    <motion.nav
      initial={{ opacity: 0, y: -20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6, ease: "easeOut" }}
      className="fixed top-0 left-0 right-0 z-50 flex items-center justify-between px-6 py-4"
      style={{
        background:
          "linear-gradient(180deg, rgba(4,2,15,0.9) 0%, rgba(4,2,15,0) 100%)",
        backdropFilter: "blur(0px)",
      }}
    >
      {/* Logo */}
      <Link href="/" className="flex items-center gap-3 group">
        <div className="relative w-9 h-9 transition-transform duration-500 group-hover:rotate-45">
          <Image
            src="/icon-removebg-preview.png"
            alt="紫微星盤"
            fill
            className="object-contain"
          />
        </div>
        <span
          className="font-serif text-lg font-semibold tracking-widest text-gold-gradient"
          style={{
            background: "linear-gradient(135deg, #C9A84C, #F0C040, #C9A84C)",
            backgroundSize: "200% auto",
            WebkitBackgroundClip: "text",
            WebkitTextFillColor: "transparent",
          }}
        >
          紫微星盤
        </span>
      </Link>

      {/* Nav links */}
      <div className="flex items-center gap-6">
        <Link
          href="/"
          className="text-sm text-parchment-dim hover:text-gold-400 transition-colors duration-300 tracking-wide"
        >
          首頁
        </Link>
        <Link
          href="/analyze"
          className="text-sm btn-ghost-gold px-4 py-2 rounded-full tracking-wide"
        >
          開始推算
        </Link>
      </div>
    </motion.nav>
  );
}
