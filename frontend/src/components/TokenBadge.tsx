"use client";
import Link from "next/link";
import { useAuth } from "@/contexts/AuthContext";

export default function TokenBadge({ collapsed }: { collapsed?: boolean }) {
  const { subscription } = useAuth();
  if (!subscription) return null;

  const balance = subscription.token_balance;
  const isUnlimited = subscription.monthly_tokens === -1;
  const isLow = !isUnlimited && balance <= 5;

  return (
    <Link
      href="/pricing"
      className={`flex items-center gap-2 rounded-xl px-3 py-2 transition-all
        ${isLow ? "bg-red-900/30 border border-red-500/40" : "bg-cosmos-800/50 border border-gold-700/30"}
        hover:border-gold-500/50 hover:bg-cosmos-800/70`}
    >
      <span className={`text-sm ${isLow ? "animate-pulse text-red-400" : "text-gold-400"}`}>
        ✦
      </span>
      {!collapsed && (
        <span className={`text-xs font-medium ${isLow ? "text-red-300" : "text-parchment-dim"}`}>
          {isUnlimited ? "無限代幣" : `${balance} 星辰代幣`}
        </span>
      )}
    </Link>
  );
}
