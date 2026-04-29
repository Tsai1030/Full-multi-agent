"use client";
import { Suspense } from "react";
import { useSearchParams } from "next/navigation";
import { AnimatePresence, motion } from "framer-motion";
import CosmicBackground from "@/components/CosmicBackground";
import Navbar from "@/components/Navbar";
import BirthDataForm from "@/components/BirthDataForm";
import DivinationLoader from "@/components/DivinationLoader";
import ResultDisplay from "@/components/ResultDisplay";
import { useAnalysis } from "@/hooks/useAnalysis";
import type { DomainType } from "@/types";

function AnalyzePage() {
  const params = useSearchParams();
  const initialDomain = (params.get("domain") as DomainType) || "comprehensive";
  const { stage, result, error, submit, reset } = useAnalysis();

  return (
    <main className="relative min-h-screen">
      <CosmicBackground dimOverlay />
      <Navbar />

      {/* Fullscreen loader overlay */}
      <AnimatePresence>{stage === "loading" && <DivinationLoader />}</AnimatePresence>

      {/* Page content */}
      <div className="relative z-10 min-h-screen flex flex-col items-center justify-start pt-28 pb-16 px-4">
        <AnimatePresence mode="wait">
          {stage === "form" && (
            <motion.div
              key="form"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="w-full flex flex-col items-center"
            >
              {/* Page header */}
              <motion.div
                initial={{ opacity: 0, y: -20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6 }}
                className="text-center mb-10"
              >
                <p className="text-xs tracking-[0.4em] text-gold-500 uppercase mb-3">
                  開始推算
                </p>
                <h1 className="font-serif text-3xl md:text-4xl font-bold text-parchment">
                  輸入您的命盤資料
                </h1>
              </motion.div>

              <BirthDataForm
                initialDomain={initialDomain}
                onSubmit={submit}
                loading={stage === ("loading" as string)}
                error={error}
              />

              {/* Small disclaimer */}
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
              className="w-full flex flex-col items-center"
            >
              <ResultDisplay result={result} onReset={reset} />
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </main>
  );
}

export default function AnalyzePageWrapper() {
  return (
    <Suspense>
      <AnalyzePage />
    </Suspense>
  );
}
