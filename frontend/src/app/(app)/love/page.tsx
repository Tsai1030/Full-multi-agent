"use client";
import { useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { AnimatePresence, motion } from "framer-motion";
import Button from "@/components/ui/Button";
import { GoldSelect } from "@/components/ui/GoldSelect";
import BirthFields from "@/components/BirthFields";
import DivinationLoader from "@/components/DivinationLoader";
import ResultDisplay from "@/components/ResultDisplay";
import UpgradePrompt from "@/components/UpgradePrompt";
import { analyzeChart, fortuneApi, profileApi, ApiError } from "@/lib/api";
import { computeChart } from "@/lib/ziwei";
import { useAuth } from "@/contexts/AuthContext";
import type { AnalysisResponse, ApiErrorDetail, BirthData, ChartProfile } from "@/types";

type Stage = "form" | "loading" | "result";
type Mode = "single" | "compatibility";

const PLACEHOLDERS = [
  "我今年會遇到正緣嗎？",
  "我跟對方合適嗎？",
  "我的桃花什麼時候開？",
  "我的感情課題是什麼？",
];

const DEFAULT_PARTNER: BirthData = {
  gender: "男",
  birth_year: 1995,
  birth_month: 1,
  birth_day: 1,
  birth_hour: "子",
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

export default function LovePage() {
  const router = useRouter();
  const { subscription, refreshSubscription } = useAuth();
  const [profiles, setProfiles] = useState<ChartProfile[] | null>(null);
  const [selectedId, setSelectedId] = useState("");
  const [mode, setMode] = useState<Mode>("single");
  const [partnerData, setPartnerData] = useState<BirthData>(DEFAULT_PARTNER);
  const [customQuestion, setCustomQuestion] = useState("");
  const [stage, setStage] = useState<Stage>("form");
  const [result, setResult] = useState<AnalysisResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [upgradeError, setUpgradeError] = useState<ApiErrorDetail | null>(null);
  const [placeholderIdx, setPlaceholderIdx] = useState(0);

  useEffect(() => {
    const timer = setInterval(() => setPlaceholderIdx((i) => (i + 1) % PLACEHOLDERS.length), 3000);
    return () => clearInterval(timer);
  }, []);

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
    return () => { active = false; };
  }, []);

  const selected = useMemo(
    () => profiles?.find((p) => p.id === selectedId) ?? null,
    [profiles, selectedId],
  );

  const tokenCost = mode === "compatibility" ? 12 : 8;

  const handleAnalyze = async () => {
    if (!selected) return;
    setError(null);
    setStage("loading");

    try {
      if (mode === "compatibility") {
        const partnerChart = computeChart(partnerData);
        const res = await fortuneApi.compatibility({
          birth_data_1: toBirthData(selected),
          birth_data_2: partnerData,
          chart_1: selected.chart,
          chart_2: partnerChart,
          user_question: customQuestion.trim() || undefined,
        });
        if (res.success) {
          setResult(res);
          setStage("result");
          await refreshSubscription();
          if (res.result) {
            sessionStorage.setItem(`love-result-${selected.id}`, res.result);
            sessionStorage.setItem(`love-chart-${selected.id}`, JSON.stringify(selected.chart));
          }
        } else {
          setError(res.error || "分析失敗");
          setStage("form");
        }
      } else {
        const res = await analyzeChart({
          birth_data: toBirthData(selected),
          domain_type: "love",
          user_question: customQuestion.trim() ||
            "請深入分析我的感情與姻緣：夫妻宮格局、桃花與正緣、適合的對象特質、感情發展時機與相處上的課題與建議。",
          chart: selected.chart,
        });
        if (res.success) {
          setResult(res);
          setStage("result");
          await refreshSubscription();
          if (res.result) {
            sessionStorage.setItem(`love-result-${selected.id}`, res.result);
            sessionStorage.setItem(`love-chart-${selected.id}`, JSON.stringify(selected.chart));
          }
        } else {
          setError(res.error || "分析失敗");
          setStage("form");
        }
      }
    } catch (e) {
      if (e instanceof ApiError && (e.isFeatureLocked || e.isInsufficientTokens)) {
        setUpgradeError(e.detail);
      } else {
        setError(e instanceof ApiError ? e.message : "連線失敗，請確認後端服務是否正常");
      }
      setStage("form");
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
      <UpgradePrompt open={!!upgradeError} onClose={() => setUpgradeError(null)} error={upgradeError} />

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
              <p className="text-xs tracking-[0.3em] text-rose-400 uppercase mb-2">想了解更多？</p>
              <h3 className="font-serif text-lg font-bold text-parchment mb-2">向感情顧問追問</h3>
              <p className="text-xs text-parchment-muted mb-4">
                針對這份感情分析結果，你可以進一步追問細節或詢問建議
              </p>
              <Button
                variant="gold"
                size="md"
                onClick={() => router.push(`/love/${selected.id}`)}
                className="font-serif"
              >
                ❤ 開始追問
              </Button>
            </motion.div>
          </>
        ) : (
          <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }}>
            <div className="text-center mb-8">
              <p className="text-xs tracking-[0.4em] text-rose-400 uppercase mb-2">紫微斗數</p>
              <h1 className="font-serif text-3xl font-bold text-parchment">感情姻緣算命</h1>
              <p className="mt-3 text-sm text-parchment-muted max-w-md mx-auto">
                從夫妻宮與桃花星，解析你的感情格局、正緣特質、桃花時機與相處課題。
              </p>
              <div className="divider-gold w-24 mx-auto mt-4" />
            </div>

            {profiles === null ? (
              <div className="flex justify-center py-16 text-parchment-muted text-sm">
                <span className="w-5 h-5 border-2 border-gold-500 border-t-transparent rounded-full animate-spin mr-2" />
                載入命盤中…
              </div>
            ) : profiles.length === 0 ? (
              <div className="card-gold rounded-3xl p-10 text-center flex flex-col items-center gap-4">
                <span className="text-4xl text-rose-400">❤</span>
                <p className="text-parchment font-serif">尚未儲存任何命盤</p>
                <p className="text-parchment-muted text-sm">先去排盤並儲存命盤，才能用此功能分析。</p>
                <Link href="/analyze">
                  <Button variant="gold" size="md">✦ 開始排盤</Button>
                </Link>
              </div>
            ) : (
              <div className="card-gold rounded-3xl p-8 flex flex-col gap-6">
                {/* Mode toggle */}
                <div>
                  <label className="text-xs font-medium tracking-widest text-gold-500 uppercase mb-2 block">
                    分析模式
                  </label>
                  <div className="flex gap-3">
                    {([
                      { key: "single" as Mode, label: "單人分析", icon: "♡" },
                      { key: "compatibility" as Mode, label: "合盤分析（雙人配對）", icon: "♡♡" },
                    ]).map((m) => (
                      <button
                        key={m.key}
                        type="button"
                        onClick={() => setMode(m.key)}
                        className={`flex-1 py-3 rounded-xl border text-sm font-medium transition-all duration-300 ${
                          mode === m.key
                            ? "border-rose-400 bg-rose-500/10 text-rose-300 shadow-sm"
                            : "border-white/10 text-parchment-muted hover:border-rose-700"
                        }`}
                      >
                        {m.icon} {m.label}
                      </button>
                    ))}
                  </div>
                </div>

                {/* My chart */}
                <div>
                  <label className="text-xs font-medium tracking-widest text-gold-500 uppercase mb-2 block">
                    {mode === "compatibility" ? "我的命盤" : "選擇要分析的命盤"}
                  </label>
                  <GoldSelect value={selectedId} onChange={(e) => setSelectedId(e.target.value)}>
                    {profiles.map((p) => (
                      <option key={p.id} value={p.id}>
                        {p.label}（{p.gender}·{p.birth_year}/{p.birth_month}/{p.birth_day} {p.birth_hour}時）
                      </option>
                    ))}
                  </GoldSelect>
                </div>

                {/* Partner birth data (compatibility mode) */}
                <AnimatePresence>
                  {mode === "compatibility" && (
                    <motion.div
                      initial={{ opacity: 0, height: 0 }}
                      animate={{ opacity: 1, height: "auto" }}
                      exit={{ opacity: 0, height: 0 }}
                      className="overflow-hidden"
                    >
                      <div className="border border-rose-500/30 rounded-2xl p-5 bg-rose-500/5">
                        <p className="text-xs font-medium tracking-widest text-rose-400 uppercase mb-3">
                          對方的生辰資料
                        </p>
                        <BirthFields value={partnerData} onChange={setPartnerData} />
                      </div>
                    </motion.div>
                  )}
                </AnimatePresence>

                {/* Custom question */}
                <div>
                  <label className="text-xs font-medium tracking-widest text-gold-500 uppercase mb-2 block">
                    想問什麼？（選填）
                  </label>
                  <textarea
                    value={customQuestion}
                    onChange={(e) => setCustomQuestion(e.target.value)}
                    maxLength={200}
                    rows={3}
                    placeholder={PLACEHOLDERS[placeholderIdx]}
                    className="input-mystic w-full rounded-2xl px-4 py-3 text-sm resize-none"
                  />
                  <p className="text-[11px] text-parchment-muted mt-1 text-right">{customQuestion.length}/200</p>
                </div>

                {error && <p className="text-sm text-red-400 text-center">{error}</p>}

                <div className="flex items-center justify-between">
                  <span className="text-[11px] text-parchment-muted">
                    此分析消耗 <span className="text-rose-400">{tokenCost} 星辰代幣</span>
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
                  {mode === "compatibility" ? "❤ 開始合盤分析" : "❤ 開始感情姻緣算命"}
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
