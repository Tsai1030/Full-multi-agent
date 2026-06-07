"use client";
import Link from "next/link";
import Image from "next/image";
import { usePathname, useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { useAuth } from "@/contexts/AuthContext";

interface NavItem {
  href: string;
  label: string;
  icon: string;
}

const NAV: NavItem[] = [
  { href: "/reading", label: "排盤分析", icon: "✶" },
  { href: "/profiles", label: "我的命盤", icon: "❖" },
  { href: "/master", label: "與大師對談", icon: "✦" },
  { href: "/career", label: "事業工作算命", icon: "❂" },
  { href: "/love", label: "感情姻緣算命", icon: "❤" },
];

const STORAGE_KEY = "ziwei-sidebar-collapsed";

function isActive(pathname: string, href: string): boolean {
  return pathname === href || pathname.startsWith(href + "/");
}

function SidebarContent({
  collapsed,
  onToggle,
  onNavigate,
}: {
  collapsed: boolean;
  onToggle?: () => void;
  onNavigate?: () => void;
}) {
  const pathname = usePathname();
  const router = useRouter();
  const { user, logout } = useAuth();

  const handleLogout = async () => {
    onNavigate?.();
    await logout();
    router.push("/");
  };

  return (
    <div className="flex flex-col h-full w-full p-3">
      {/* Brand + 收合鈕 */}
      <div className={`flex items-center mb-6 ${collapsed ? "flex-col gap-2" : "justify-between px-1"}`}>
        <Link href="/" onClick={onNavigate} className="flex items-center gap-2.5 group" title="紫微星盤">
          <div className="relative w-8 h-8 shrink-0 transition-transform duration-500 group-hover:rotate-45">
            <Image src="/icon-removebg-preview.png" alt="" fill className="object-contain" />
          </div>
          {!collapsed && (
            <span
              className="font-serif text-base font-semibold tracking-widest whitespace-nowrap"
              style={{
                background: "linear-gradient(135deg, #C9A84C, #F0C040, #C9A84C)",
                WebkitBackgroundClip: "text",
                WebkitTextFillColor: "transparent",
              }}
            >
              紫微星盤
            </span>
          )}
        </Link>
        {onToggle && (
          <button
            onClick={onToggle}
            aria-label={collapsed ? "展開側欄" : "收合側欄"}
            title={collapsed ? "展開" : "收合"}
            className="w-7 h-7 rounded-lg flex items-center justify-center text-gold-500 hover:bg-cosmos-700/50 hover:text-gold-300 transition-colors"
          >
            {collapsed ? "»" : "«"}
          </button>
        )}
      </div>

      {/* Nav */}
      <nav className="flex flex-col gap-1.5">
        {NAV.map((item) => {
          const active = isActive(pathname, item.href);
          return (
            <Link
              key={item.href}
              href={item.href}
              onClick={onNavigate}
              title={item.label}
              className={`flex items-center gap-3 rounded-xl text-sm transition-all duration-300 ${
                collapsed ? "justify-center px-0 py-3" : "px-3 py-2.5"
              } ${
                active
                  ? "bg-gold-500/12 text-gold-300 border border-gold-600/40 shadow-gold-sm"
                  : "text-parchment-dim border border-transparent hover:bg-cosmos-700/40 hover:text-gold-400"
              }`}
            >
              <span className={`text-base ${active ? "text-gold-400" : "text-gold-600"}`}>
                {item.icon}
              </span>
              {!collapsed && <span className="font-medium tracking-wide whitespace-nowrap">{item.label}</span>}
            </Link>
          );
        })}
      </nav>

      <div className="flex-1" />

      {/* User */}
      <div className="border-t border-gold-800/30 pt-4 mt-4">
        <div className={`flex items-center mb-3 ${collapsed ? "justify-center" : "gap-2.5 px-2"}`}>
          <span
            title={user?.display_name}
            className="w-8 h-8 rounded-full bg-gold-gradient flex items-center justify-center text-cosmos-950 text-sm font-bold shrink-0"
          >
            {user?.display_name?.charAt(0).toUpperCase() ?? "?"}
          </span>
          {!collapsed && <span className="text-sm text-parchment truncate">{user?.display_name}</span>}
        </div>
        <button
          onClick={handleLogout}
          title="登出"
          className={`rounded-xl text-sm text-parchment-muted hover:bg-cosmos-700/40 hover:text-red-300 transition-colors ${
            collapsed ? "w-full py-2 flex justify-center" : "w-full text-left px-3 py-2"
          }`}
        >
          {collapsed ? "⎋" : "登出"}
        </button>
      </div>
    </div>
  );
}

export default function Sidebar() {
  const [open, setOpen] = useState(false); // 手機抽屜
  const [collapsed, setCollapsed] = useState(false); // 桌機收合
  const [hydrated, setHydrated] = useState(false);

  useEffect(() => {
    setCollapsed(localStorage.getItem(STORAGE_KEY) === "1");
    setHydrated(true);
  }, []);

  const toggleCollapsed = () => {
    setCollapsed((c) => {
      const next = !c;
      localStorage.setItem(STORAGE_KEY, next ? "1" : "0");
      return next;
    });
  };

  return (
    <>
      {/* 桌機固定欄（可收合） */}
      <aside
        className={`hidden md:flex shrink-0 h-full border-r border-gold-800/30 bg-cosmos-950/50 backdrop-blur-sm transition-[width] duration-300 ${
          hydrated && collapsed ? "w-[76px]" : "w-64"
        }`}
      >
        <SidebarContent collapsed={hydrated && collapsed} onToggle={toggleCollapsed} />
      </aside>

      {/* 手機漢堡鈕 */}
      <button
        onClick={() => setOpen(true)}
        aria-label="開啟選單"
        className="md:hidden fixed top-3 left-3 z-50 w-10 h-10 rounded-xl border border-gold-700/40 bg-cosmos-900/80 backdrop-blur flex items-center justify-center text-gold-400"
      >
        ☰
      </button>

      {/* 手機抽屜（永遠展開） */}
      <AnimatePresence>
        {open && (
          <div className="md:hidden">
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={() => setOpen(false)}
              className="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm"
            />
            <motion.aside
              initial={{ x: -300 }}
              animate={{ x: 0 }}
              exit={{ x: -300 }}
              transition={{ type: "spring", stiffness: 320, damping: 32 }}
              className="fixed left-0 top-0 h-full w-64 z-50 border-r border-gold-800/40 bg-cosmos-950/95 backdrop-blur"
            >
              <SidebarContent collapsed={false} onNavigate={() => setOpen(false)} />
            </motion.aside>
          </div>
        )}
      </AnimatePresence>
    </>
  );
}
