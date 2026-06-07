"use client";
import Link from "next/link";
import Image from "next/image";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { useAuth } from "@/contexts/AuthContext";

export default function Navbar() {
  const { user, loading, logout } = useAuth();
  const router = useRouter();
  const [menuOpen, setMenuOpen] = useState(false);

  const handleLogout = async () => {
    setMenuOpen(false);
    await logout();
    router.push("/");
  };

  return (
    <motion.nav
      initial={{ opacity: 0, y: -20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6, ease: "easeOut" }}
      className="fixed top-0 left-0 right-0 z-50 flex items-center justify-between px-6 py-4"
      style={{
        background:
          "linear-gradient(180deg, rgba(4,2,15,0.9) 0%, rgba(4,2,15,0) 100%)",
      }}
    >
      {/* Logo */}
      <Link href="/" className="flex items-center gap-3 group">
        <div className="relative w-9 h-9 transition-transform duration-500 group-hover:rotate-45">
          <Image src="/icon-removebg-preview.png" alt="紫微星盤" fill className="object-contain" />
        </div>
        <span
          className="font-serif text-lg font-semibold tracking-widest"
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
      <div className="flex items-center gap-5">
        <Link
          href="/"
          className="text-sm text-parchment-dim hover:text-gold-400 transition-colors duration-300 tracking-wide"
        >
          首頁
        </Link>
        <Link
          href="/analyze"
          className="text-sm text-parchment-dim hover:text-gold-400 transition-colors duration-300 tracking-wide"
        >
          開始推算
        </Link>

        {loading ? null : user ? (
          <div className="relative">
            <button
              onClick={() => setMenuOpen((o) => !o)}
              className="flex items-center gap-2 text-sm btn-ghost-gold px-4 py-2 rounded-full tracking-wide"
            >
              <span className="w-6 h-6 rounded-full bg-gold-gradient flex items-center justify-center text-cosmos-950 text-xs font-bold">
                {user.display_name.charAt(0).toUpperCase()}
              </span>
              <span className="max-w-[8rem] truncate">{user.display_name}</span>
              <span className="text-xs">▾</span>
            </button>
            <AnimatePresence>
              {menuOpen && (
                <motion.div
                  initial={{ opacity: 0, y: -8 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -8 }}
                  className="absolute right-0 mt-2 w-44 card-gold rounded-2xl p-2 z-50"
                >
                  <Link
                    href="/profiles"
                    onClick={() => setMenuOpen(false)}
                    className="block px-4 py-2.5 rounded-xl text-sm text-parchment-dim hover:bg-cosmos-700/50 hover:text-gold-400 transition-colors"
                  >
                    我的命盤
                  </Link>
                  <button
                    onClick={handleLogout}
                    className="block w-full text-left px-4 py-2.5 rounded-xl text-sm text-parchment-dim hover:bg-cosmos-700/50 hover:text-red-300 transition-colors"
                  >
                    登出
                  </button>
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        ) : (
          <Link
            href="/login"
            className="text-sm btn-ghost-gold px-4 py-2 rounded-full tracking-wide"
          >
            登入
          </Link>
        )}
      </div>
    </motion.nav>
  );
}
