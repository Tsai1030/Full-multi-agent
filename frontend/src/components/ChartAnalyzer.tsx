"use client";
import { AnimatePresence, motion } from "framer-motion";
import BirthDataForm from "@/components/BirthDataForm";
import DivinationLoader from "@/components/DivinationLoader";
import ResultDisplay from "@/components/ResultDisplay";
import ZiweiChart from "@/components/ZiweiChart";
import { useAnalysis } from "@/hooks/useAnalysis";
import type { DomainType } from "@/types";

/**
 * 排盤分析流程（form → loading → 命盤盤面 + multi-agent 報告）。
 * 不含外層背景/導覽，供公開頁與 app 內側欄共用。
 */
export default function ChartAnalyzer({
  initialDomain = "comprehensive",
}: {
  initialDomain?: DomainType;
}) {
  const { stage, result, chart, birthData, error, submit, reset } = useAnalysis();

  return (
    <>
      <AnimatePresence>{stage === "loading" && <DivinationLoader />}</AnimatePresence>

      <AnimatePresence mode="wait">
        {stage === "form" && (
          <motion.div
            key="form"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="w-full flex flex-col items-center"
          >
            <motion.div
              initial={{ opacity: 0, y: -20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6 }}
              className="text-center mb-10"
            >
              <p className="text-xs tracking-[0.4em] text-gold-500 uppercase mb-3">開始推算</p>
              <h1 className="font-serif text-3xl md:text-4xl font-bold text-parchment">
                輸入命盤資料
              </h1>
            </motion.div>

            <BirthDataForm
              initialDomain={initialDomain}
              onSubmit={submit}
              loading={stage === ("loading" as string)}
              error={error}
            />

            <motion.p
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 1, duration: 0.8 }}
              className="mt-8 text-xs text-parchment-muted text-center max-w-xs"
            >
              本系統僅供文化與學習參考，不應作為重大決策的唯一依據。
            </motion.p>
          </motion.div>
        )}

        {stage === "result" && result && (
          <motion.div
            key="result"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="w-full flex flex-col items-center gap-10"
          >
            {chart && <ZiweiChart chart={chart} />}
            <ResultDisplay result={result} chart={chart} birthData={birthData} onReset={reset} />
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
}
