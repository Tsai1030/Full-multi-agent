"use client";
import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import { motion } from "framer-motion";
import ZiweiChart from "@/components/ZiweiChart";
import Button from "@/components/ui/Button";
import { profileApi, ApiError } from "@/lib/api";
import type { ChartProfile } from "@/types";

export default function ProfileChartPage() {
  const params = useParams();
  const id = String(params.id);

  const [profile, setProfile] = useState<ChartProfile | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let active = true;
    (async () => {
      try {
        const p = await profileApi.get(id);
        if (active) setProfile(p);
      } catch (e) {
        if (active) setError(e instanceof ApiError ? e.message : "載入失敗");
      }
    })();
    return () => {
      active = false;
    };
  }, [id]);

  return (
    <div className="h-full overflow-y-auto">
      <div className="w-full max-w-3xl mx-auto px-4 pt-16 md:pt-12 pb-16 flex flex-col items-center">
        {error ? (
          <div className="card-gold rounded-3xl p-10 text-center mt-10">
            <p className="text-red-400 text-sm mb-4">{error}</p>
            <Link href="/profiles">
              <Button variant="ghost" size="md">返回我的命盤</Button>
            </Link>
          </div>
        ) : !profile ? (
          <div className="flex justify-center py-20 text-parchment-muted text-sm">
            <span className="w-5 h-5 border-2 border-gold-500 border-t-transparent rounded-full animate-spin mr-2" />
            載入命盤中…
          </div>
        ) : (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="w-full flex flex-col items-center gap-8"
          >
            <div className="text-center">
              <p className="text-xs tracking-[0.4em] text-gold-500 uppercase mb-2">{profile.label}</p>
              <h1 className="font-serif text-2xl md:text-3xl font-bold text-parchment">命盤盤面</h1>
            </div>

            <ZiweiChart chart={profile.chart} />

            <div className="flex flex-col sm:flex-row gap-3 justify-center pb-4">
              <Link href={`/master/${profile.id}`}>
                <Button variant="gold" size="lg" className="font-serif tracking-widest">
                  ✦ 與大師詢問
                </Button>
              </Link>
              <Link href="/profiles">
                <Button variant="ghost" size="lg">我的命盤典藏</Button>
              </Link>
            </div>
          </motion.div>
        )}
      </div>
    </div>
  );
}
