"use client";
import { useEffect, useState } from "react";
import Link from "next/link";
import { motion } from "framer-motion";
import Button from "@/components/ui/Button";
import { profileApi, ApiError } from "@/lib/api";
import type { ChartProfile } from "@/types";

export default function ProfilesPage() {
  const [profiles, setProfiles] = useState<ChartProfile[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [deletingId, setDeletingId] = useState<string | null>(null);

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

  const handleDelete = async (id: string) => {
    setDeletingId(id);
    setError(null);
    try {
      await profileApi.remove(id);
      setProfiles((ps) => (ps ? ps.filter((p) => p.id !== id) : ps));
    } catch (e) {
      setError(e instanceof ApiError ? e.message : "刪除失敗");
    } finally {
      setDeletingId(null);
    }
  };

  return (
    <div className="h-full overflow-y-auto">
      <div className="w-full max-w-2xl mx-auto px-4 pt-16 md:pt-12 pb-16">
        <div className="text-center mb-8">
          <p className="text-xs tracking-[0.4em] text-gold-500 uppercase mb-2">我的命盤</p>
          <h1 className="font-serif text-3xl font-bold text-parchment">命盤典藏</h1>
          <div className="divider-gold w-24 mx-auto mt-4" />
        </div>

        {error && <p className="text-red-400 text-sm text-center mb-4">{error}</p>}

        {profiles === null ? (
          <div className="flex justify-center py-16 text-parchment-muted text-sm">
            <span className="w-5 h-5 border-2 border-gold-500 border-t-transparent rounded-full animate-spin mr-2" />
            載入中…
          </div>
        ) : profiles.length === 0 ? (
          <div className="card-gold rounded-3xl p-10 text-center flex flex-col items-center gap-4">
            <span className="text-4xl text-gold-500">✦</span>
            <p className="text-parchment font-serif">尚未儲存任何命盤</p>
            <p className="text-parchment-muted text-sm">先去排盤，分析後即可儲存命盤並與大師對談。</p>
            <Link href="/analyze">
              <Button variant="gold" size="md">✦ 開始排盤</Button>
            </Link>
          </div>
        ) : (
          <div className="flex flex-col gap-4">
            {profiles.map((p) => (
              <motion.div
                key={p.id}
                initial={{ opacity: 0, y: 16 }}
                animate={{ opacity: 1, y: 0 }}
                className="card-gold rounded-2xl p-4 sm:p-5 flex flex-col sm:flex-row sm:items-center justify-between gap-3 sm:gap-4"
              >
                <Link href={`/profiles/${p.id}`} className="group flex-1 min-w-0">
                  <h3 className="font-serif text-lg text-parchment group-hover:text-gold-300 transition-colors truncate">
                    {p.label}
                  </h3>
                  <p className="text-xs text-parchment-muted mt-1">
                    {p.gender} · {p.birth_year}/{p.birth_month}/{p.birth_day} {p.birth_hour}時
                    {p.chart?.fiveElementsClass ? ` · ${p.chart.fiveElementsClass}` : ""}
                  </p>
                  <span className="inline-block mt-1.5 text-[11px] text-gold-600/90 group-hover:text-gold-400 transition-colors">
                    查看完整命盤 →
                  </span>
                </Link>
                <div className="flex items-center gap-2 shrink-0">
                  <Link href={`/master/${p.id}`} className="flex-1 sm:flex-none">
                    <Button variant="gold" size="sm" className="w-full">與大師對談</Button>
                  </Link>
                  <Button
                    variant="danger"
                    size="sm"
                    onClick={() => handleDelete(p.id)}
                    loading={deletingId === p.id}
                    disabled={deletingId !== null}
                  >
                    刪除
                  </Button>
                </div>
              </motion.div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
