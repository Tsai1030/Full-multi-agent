"use client";
import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import { motion } from "framer-motion";
import { profileApi, ApiError } from "@/lib/api";
import { mdToHtml } from "@/lib/markdown";
import FortuneChat from "@/components/FortuneChat";
import type { ChartProfile } from "@/types";

export default function CareerChatPage() {
  const params = useParams();
  const profileId = String(params.profileId);

  const [profile, setProfile] = useState<ChartProfile | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const analysisResult = typeof window !== "undefined"
    ? sessionStorage.getItem(`career-result-${profileId}`)
    : null;
  const chartText = typeof window !== "undefined"
    ? sessionStorage.getItem(`career-chart-${profileId}`) || ""
    : "";

  useEffect(() => {
    let active = true;
    (async () => {
      try {
        const p = await profileApi.get(profileId);
        if (active) setProfile(p);
      } catch (e) {
        if (active) setError(e instanceof ApiError ? e.message : "載入失敗");
      } finally {
        if (active) setLoading(false);
      }
    })();
    return () => { active = false; };
  }, [profileId]);

  if (loading) {
    return (
      <div className="h-full flex items-center justify-center text-parchment-muted text-sm">
        <span className="w-5 h-5 border-2 border-gold-500 border-t-transparent rounded-full animate-spin mr-2" />
        載入中…
      </div>
    );
  }

  if (error || !analysisResult) {
    return (
      <div className="h-full flex flex-col items-center justify-center gap-4 text-center px-4">
        <p className="text-red-400 text-sm">{error || "找不到分析結果，請重新進行分析"}</p>
        <Link href="/career" className="text-gold-400 text-sm hover:text-gold-300">
          返回事業工作算命
        </Link>
      </div>
    );
  }

  return (
    <div className="h-full flex flex-col">
      {/* Header */}
      <header className="shrink-0 border-b border-gold-800/30 bg-cosmos-950/40 backdrop-blur-sm px-4 md:px-6 pt-16 md:pt-4 pb-3">
        <div className="max-w-3xl mx-auto flex items-center justify-between gap-3">
          <div className="min-w-0">
            <h1 className="font-serif text-lg sm:text-xl font-bold text-parchment leading-tight">
              <span className="text-gold-400">❂</span> 事業工作算命
            </h1>
            {profile && (
              <p className="text-xs text-parchment-muted truncate mt-0.5">
                <span className="text-gold-300">{profile.label}</span>
                <span className="text-parchment-muted/70">
                  {" "}· {profile.gender} {profile.birth_year}/{profile.birth_month}/{profile.birth_day} {profile.birth_hour}時
                </span>
              </p>
            )}
          </div>
          <Link
            href="/career"
            className="shrink-0 text-xs text-gold-400 hover:text-gold-300 border border-gold-700/40 hover:border-gold-500/60 rounded-full px-3 py-1.5 transition-colors"
          >
            重新分析
          </Link>
        </div>
      </header>

      {/* Content: Analysis result (collapsible) + Chat */}
      <div className="flex-1 min-h-0 flex flex-col">
        {/* Analysis result - scrollable summary */}
        <details className="shrink-0 border-b border-gold-800/20" open>
          <summary className="px-4 md:px-6 py-3 cursor-pointer text-sm text-gold-400 hover:text-gold-300 transition-colors">
            ✦ 查看分析報告
          </summary>
          <div className="max-w-3xl mx-auto px-4 md:px-6 pb-4 max-h-[40vh] overflow-y-auto">
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="prose-sm text-parchment-dim chat-md"
              dangerouslySetInnerHTML={{ __html: mdToHtml(analysisResult) }}
            />
          </div>
        </details>

        {/* Ephemeral chat */}
        <div className="flex-1 min-h-0">
          <FortuneChat
            domain="career"
            analysisContext={analysisResult}
            chartText={chartText}
            personaLabel="事業顧問"
            placeholder="針對事業分析追問…（Enter 送出）"
          />
        </div>
      </div>
    </div>
  );
}
