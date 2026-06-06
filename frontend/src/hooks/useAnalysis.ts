"use client";
import { useState, useRef, useCallback } from "react";
import { analyzeChart } from "@/lib/api";
import { computeChart } from "@/lib/ziwei";
import type {
  AnalysisRequest,
  AnalysisResponse,
  AnalysisStage,
  ZiweiChart,
} from "@/types";

interface UseAnalysisReturn {
  stage: AnalysisStage;
  result: AnalysisResponse | null;
  chart: ZiweiChart | null;
  error: string | null;
  submit: (req: AnalysisRequest) => Promise<void>;
  reset: () => void;
}

export function useAnalysis(): UseAnalysisReturn {
  const [stage, setStage] = useState<AnalysisStage>("form");
  const [result, setResult] = useState<AnalysisResponse | null>(null);
  const [chart, setChart] = useState<ZiweiChart | null>(null);
  const [error, setError] = useState<string | null>(null);
  const abortRef = useRef<AbortController | null>(null);

  const submit = useCallback(async (req: AnalysisRequest) => {
    abortRef.current?.abort();
    abortRef.current = new AbortController();

    setError(null);
    setResult(null);

    // 1) 先用 iztro 在前端精準排盤（保證正確、不編造）
    let computed: ZiweiChart;
    try {
      computed = computeChart(req.birth_data);
      setChart(computed);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "命盤計算失敗，請確認出生日期是否有效";
      setError(`命盤計算失敗：${msg}`);
      setStage("form");
      return;
    }

    setStage("loading");

    // 2) 連同命盤送後端 multi-agent 解析
    try {
      const res = await analyzeChart(
        { ...req, chart: computed },
        abortRef.current.signal,
      );
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
    setChart(null);
    setError(null);
  }, []);

  return { stage, result, chart, error, submit, reset };
}
