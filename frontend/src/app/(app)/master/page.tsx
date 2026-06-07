"use client";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import Image from "next/image";
import { motion } from "framer-motion";
import Button from "@/components/ui/Button";
import { profileApi, ApiError } from "@/lib/api";
import type { ChartProfile } from "@/types";

export default function MasterSelectPage() {
  const router = useRouter();
  const [profiles, setProfiles] = useState<ChartProfile[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let active = true;
    (async () => {
      try {
        const list = await profileApi.list();
        if (active) setProfiles(list);
      } catch (e) {
        if (active) setError(e instanceof ApiError ? e.message : "載入失敗");
      }
    })();
    return () => {
      active = false;
    };
  }, []);

  return (
    <div className="h-full overflow-y-auto">
      <div className="w-full max-w-2xl mx-auto px-4 pt-16 md:pt-12 pb-16">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="relative w-12 h-12 mx-auto mb-3 opacity-90">
            <Image src="/wizard_icon/crystal-ball.png" alt="" fill className="object-contain" />
          </div>
          <p className="text-xs tracking-[0.4em] text-gold-500 uppercase mb-2">玄機子 · 命理大師</p>
          <h1 className="font-serif text-3xl font-bold text-parchment">與大師對談</h1>
          <p className="mt-3 text-sm text-parchment-muted">
            大師會依你選擇的命盤來解讀回答，請先選一張命盤。
          </p>
          <div className="divider-gold w-24 mx-auto mt-4" />
        </div>

        {error && <p className="text-red-400 text-sm text-center mb-4">{error}</p>}

        {profiles === null ? (
          <div className="flex justify-center py-16 text-parchment-muted text-sm">
            <span className="w-5 h-5 border-2 border-gold-500 border-t-transparent rounded-full animate-spin mr-2" />
            載入命盤中…
          </div>
        ) : profiles.length === 0 ? (
          <div className="card-gold rounded-3xl p-10 text-center flex flex-col items-center gap-4">
            <span className="text-4xl text-gold-500">✦</span>
            <p className="text-parchment font-serif">還沒有命盤可以對談</p>
            <p className="text-parchment-muted text-sm">先去排盤並儲存一張命盤，就能與大師對談。</p>
            <Link href="/analyze">
              <Button variant="gold" size="md">✦ 開始排盤</Button>
            </Link>
          </div>
        ) : (
          <div className="flex flex-col gap-3">
            <p className="text-xs tracking-[0.3em] text-gold-500 uppercase text-center mb-1">
              選擇要請教的命盤
            </p>
            {profiles.map((p) => (
              <motion.button
                key={p.id}
                initial={{ opacity: 0, y: 14 }}
                animate={{ opacity: 1, y: 0 }}
                whileHover={{ scale: 1.01 }}
                whileTap={{ scale: 0.99 }}
                onClick={() => router.push(`/master/${p.id}`)}
                className="card-gold rounded-2xl p-4 sm:p-5 flex items-center justify-between gap-4 text-left group"
              >
                <div className="min-w-0">
                  <h3 className="font-serif text-lg text-parchment group-hover:text-gold-300 transition-colors truncate">
                    {p.label}
                  </h3>
                  <p className="text-xs text-parchment-muted mt-1">
                    {p.gender} · {p.birth_year}/{p.birth_month}/{p.birth_day} {p.birth_hour}時
                    {p.chart?.fiveElementsClass ? ` · ${p.chart.fiveElementsClass}` : ""}
                  </p>
                </div>
                <span className="text-gold-500 group-hover:text-gold-300 group-hover:translate-x-0.5 transition-all shrink-0">
                  開始對談 →
                </span>
              </motion.button>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
