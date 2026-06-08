"use client";
import { useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { AnimatePresence, motion } from "framer-motion";
import Button from "@/components/ui/Button";
import { GoldSelect } from "@/components/ui/GoldSelect";
import DivinationLoader from "@/components/DivinationLoader";
import ResultDisplay from "@/components/ResultDisplay";
import UpgradePrompt from "@/components/UpgradePrompt";
import { analyzeChart, profileApi, ApiError } from "@/lib/api";
import { useAuth } from "@/contexts/AuthContext";
import type { AnalysisResponse, ApiErrorDetail, BirthData, ChartProfile, DomainType } from "@/types";

interface FortuneFeatureProps {
  title: string;
  subtitle: string;
  domain: DomainType;
  question: string;
}

type Stage = "form" | "loading" | "result";

const TOKEN_COSTS: Record<string, number> = {
  career: 8,
  love: 8,
  comprehensive: 10,
};

const QUESTION_PLACEHOLDERS: Record<string, string[]> = {
  career: ["我適合轉職嗎？", "我的事業什麼時候會起飛？", "我適合創業還是上班？", "我的職場貴人在哪？"],
  love: ["我今年會遇到正緣嗎？", "我跟對方合適嗎？", "我的桃花什麼時候開？", "我的感情課題是什麼？"],
};

function toBirthData(p: ChartProfile): BirthData {
  return {
    gender: p.gender as "男" | "女",
    birth_year: p.birth_year,
    birth_month: p.birth_month,
    birth_day: p.birth_day,
    birth_hour: p.birth_hour,
  };
}

export default function FortuneFeature({ title, subtitle, domain, question }: FortuneFeatureProps) {
  const router = useRouter();
  const { subscription, refreshSubscription } = useAuth();
  const [profiles, setProfiles] = useState<ChartProfile[] | null>(null);
  const [selectedId, setSelectedId] = useState<string>("");
  const [customQuestion, setCustomQuestion] = useState("");
  const [stage, setStage] = useState<Stage>("form");
  const [result, setResult] = useState<AnalysisResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [upgradeError, setUpgradeError] = useState<ApiErrorDetail | null>(null);
  const [placeholderIdx, setPlaceholderIdx] = useState(0);

  const placeholders = QUESTION_PLACEHOLDERS[domain] || [];

  useEffect(() => {
    if (placeholders.length === 0) return;
    const timer = setInterval(() => {
      setPlaceholderIdx((i) => (i + 1) % placeholders.length);
    }, 3000);
    return () => clearInterval(timer);
  }, [placeholders.length]);

  useEffect(() => {
    let active = true;
    (async () => {
      try {
        const list = await profileApi.list();
        if (!active) return;
        setProfiles(list);
        if (list[0]) setSelectedId(list[0].id);
      } catch (e) {
        if (active) setError(e instanceof ApiError ? e.message : "載入命盤失敗");
      }
    })();
    return () => {
      active = false;
    };
  }, []);

  const selected = useMemo(
    () => profiles?.find((p) => p.id === selectedId) ?? null,
    [profiles, selectedId],
  );

  const tokenCost = TOKEN_COSTS[domain] ?? 8;

  const handleAnalyze = async () => {
    if (!selected) return;
    setError(null);
    setStage("loading");
    try {
      const res = await analyzeChart({
        birth_data: toBirthData(selected),
        domain_type: domain,
        user_question: customQuestion.trim() || question,
        chart: selected.chart,
      });
      if (res.success) {
        setResult(res);
        setStage("result");
        await refreshSubscription();

        if (selected && res.result) {
          sessionStorage.setItem(`${domain}-result-${selected.id}`, res.result);
          sessionStorage.setItem(`${domain}-chart-${selected.id}`, JSON.stringify(selected.chart));
        }
      } else {
        setError(res.error || "分析失敗，請稍後再試");
        setStage("form");
      }
    } catch (e) {
      if (e instanceof ApiError && (e.isFeatureLocked || e.isInsufficientTokens)) {
        setUpgradeError(e.detail);
        setStage("form");
      } else {
        setError(e instanceof ApiError ? e.message : "連線失敗，請確認後端服務是否正常");
        setStage("form");
      }
    }
  };

  const reset = () => {
    setResult(null);
    setCustomQuestion("");
    setStage("form");
  };

  return (
    <div className="h-full overflow-y-auto">
      <AnimatePresence>{stage === "loading" && <DivinationLoader />}</AnimatePresence>

      <UpgradePrompt
        open={!!upgradeError}
        onClose={() => setUpgradeError(null)}
        error={upgradeError}
      />

      <div className="w-full max-w-2xl mx-auto px-4 pt-16 md:pt-12 pb-16">
        {stage === "result" && result && selected ? (
          <>
            <ResultDisplay
              result={result}
              chart={selected.chart}
              birthData={toBirthData(selected)}
              savedProfileId={selected.id}
              onReset={reset}
            />
            <motion.div
              initial={{ opacity: 0, y: 16 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.5 }}
              className="card-gold rounded-3xl p-6 mb-8 text-center"
            >
              <p className="text-xs tracking-[0.3em] text-gold-500 uppercase mb-2">想了解更多？</p>
              <h3 className="font-serif text-lg font-bold text-parchment mb-2">向顧問追問</h3>
              <p className="text-xs text-parchment-muted mb-4">
                針對這份分析結果，你可以進一步追問細節或詢問具體建議
              </p>
              <Button
                variant="gold"
                size="md"
                onClick={() => router.push(`/${domain}/${selected.id}`)}
                className="font-serif"
              >
                ✦ 開始追問
              </Button>
            </motion.div>
          </>
        ) : (
          <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }}>
            <div className="text-center mb-8">
              <p className="text-xs tracking-[0.4em] text-gold-500 uppercase mb-2">紫微斗數</p>
              <h1 className="font-serif text-3xl font-bold text-parchment">{title}</h1>
              <p className="mt-3 text-sm text-parchment-muted max-w-md mx-auto">{subtitle}</p>
              <div className="divider-gold w-24 mx-auto mt-4" />
            </div>

            {profiles === null ? (
              <div className="flex justify-center py-16 text-parchment-muted text-sm">
                <span className="w-5 h-5 border-2 border-gold-500 border-t-transparent rounded-full animate-spin mr-2" />
                載入命盤中…
              </div>
            ) : profiles.length === 0 ? (
              <div className="card-gold rounded-3xl p-10 text-center flex flex-col items-center gap-4">
                <span className="text-4xl text-gold-500">✦</span>
                <p className="text-parchment font-serif">尚未儲存任何命盤</p>
                <p className="text-parchment-muted text-sm">先去排盤並儲存命盤，才能用此功能分析。</p>
                <Link href="/analyze">
                  <Button variant="gold" size="md">✦ 開始排盤</Button>
                </Link>
              </div>
            ) : (
              <div className="card-gold rounded-3xl p-8 flex flex-col gap-6">
                <div>
                  <label className="text-xs font-medium tracking-widest text-gold-500 uppercase mb-2 block">
                    選擇要分析的命盤
                  </label>
                  <GoldSelect value={selectedId} onChange={(e) => setSelectedId(e.target.value)}>
                    {profiles.map((p) => (
                      <option key={p.id} value={p.id}>
                        {p.label}（{p.gender}·{p.birth_year}/{p.birth_month}/{p.birth_day} {p.birth_hour}時）
                      </option>
                    ))}
                  </GoldSelect>
                </div>

                <div>
                  <label className="text-xs font-medium tracking-widest text-gold-500 uppercase mb-2 block">
                    想問大師什麼？（選填）
                  </label>
                  <textarea
                    value={customQuestion}
                    onChange={(e) => setCustomQuestion(e.target.value)}
                    maxLength={200}
                    rows={3}
                    placeholder={placeholders[placeholderIdx] || "輸入你想問的問題…"}
                    className="input-mystic w-full rounded-2xl px-4 py-3 text-sm resize-none"
                  />
                  <p className="text-[11px] text-parchment-muted mt-1 text-right">
                    {customQuestion.length}/200
                  </p>
                </div>

                {error && <p className="text-sm text-red-400 text-center">{error}</p>}

                <div className="flex items-center justify-between">
                  <span className="text-[11px] text-parchment-muted">
                    此分析消耗 <span className="text-gold-400">{tokenCost} 星辰代幣</span>
                    {subscription && subscription.monthly_tokens !== -1 && (
                      <> · 剩餘 {subscription.token_balance}</>
                    )}
                  </span>
                </div>

                <Button
                  variant="gold"
                  size="lg"
                  onClick={handleAnalyze}
                  disabled={!selected}
                  className="w-full font-serif tracking-widest"
                >
                  ✦ 開始{title}
                </Button>

                <p className="text-[11px] text-parchment-muted text-center">
                  由三位 AI 命理師協同深入分析，約需 30–50 秒
                </p>
              </div>
            )}
          </motion.div>
        )}
      </div>
    </div>
  );
}
