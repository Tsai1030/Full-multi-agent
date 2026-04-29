"use client";
import { useState, useRef, useCallback } from "react";
import { analyzeChart } from "@/lib/api";
import type { AnalysisRequest, AnalysisResponse, AnalysisStage } from "@/types";

interface UseAnalysisReturn {
  stage: AnalysisStage;
  result: AnalysisResponse | null;
  error: string | null;
  submit: (req: AnalysisRequest) => Promise<void>;
  reset: () => void;
}

export function useAnalysis(): UseAnalysisReturn {
  const [stage, setStage] = useState<AnalysisStage>("form");
  const [result, setResult] = useState<AnalysisResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const abortRef = useRef<AbortController | null>(null);

  const submit = useCallback(async (req: AnalysisRequest) => {
    abortRef.current?.abort();
    abortRef.current = new AbortController();

    setStage("loading");
    setError(null);
    setResult(null);

    try {
      const res = await analyzeChart(req, abortRef.current.signal);
      if (res.success) {
        setResult(res);
        setStage("result");
      } else {
        setError(res.error || "分析失敗，請稍後再試");
        setStage("form");
      }
    } catch (err: unknown) {
      if (err instanceof Error && err.name === "AbortError") return;
      const msg = err instanceof Error ? err.message : "連線失敗，請確認後端服務是否正常";
      setError(msg);
      setStage("form");
    }
  }, []);

  const reset = useCallback(() => {
    abortRef.current?.abort();
    setStage("form");
    setResult(null);
    setError(null);
  }, []);

  return { stage, result, error, submit, reset };
}
