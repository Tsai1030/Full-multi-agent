"use client";
import { useState } from "react";
import Image from "next/image";
import { useRouter } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";
import Button from "@/components/ui/Button";
import { useAuth } from "@/contexts/AuthContext";
import { profileApi, ApiError } from "@/lib/api";
import { mdToHtml } from "@/lib/markdown";
import type { AnalysisResponse, AgentOutput, BirthData, ZiweiChart } from "@/types";

interface ResultDisplayProps {
  result: AnalysisResponse;
  chart?: ZiweiChart | null;
  birthData?: BirthData | null;
  /** 已存命盤時帶入：隱藏「儲存命盤」、「與大師詢問」直接進該命盤對談 */
  savedProfileId?: string | null;
  onReset: () => void;
}

/** 各 agent 角色的圖示與色調 */
const AGENT_STYLE: Record<string, { icon: string; accent: string }> = {
  reasoning: { icon: "⚖", accent: "text-sky-300" },
  domain: { icon: "🎯", accent: "text-gold-300" },
  creative: { icon: "✦", accent: "text-mystic-300" },
};

function AgentProcess({ agents }: { agents: AgentOutput[] }) {
  const [open, setOpen] = useState<string | null>(null);

  return (
    <motion.div variants={item} className="card-gold rounded-3xl p-6 sm:p-8 mb-6">
      <div className="text-center mb-5">
        <p className="text-xs tracking-[0.35em] text-gold-500 uppercase mb-1">
          Multi-Agent
        </p>
        <h3 className="font-serif text-lg font-bold text-parchment">
          多代理人分析過程
        </h3>
        <p className="mt-1 text-xs text-parchment-muted">
          {agents.length} 位命理師各自獨立分析，再由首席整合 · 點擊展開
        </p>
      </div>

      <div className="flex flex-col gap-3">
        {agents.map((a) => {
          const style = AGENT_STYLE[a.role] ?? { icon: "✶", accent: "text-parchment" };
          const isOpen = open === a.role;
          return (
            <div
              key={a.role}
              className="border border-gold-800/40 rounded-2xl overflow-hidden bg-cosmos-900/40"
            >
              <button
                type="button"
                onClick={() => setOpen(isOpen ? null : a.role)}
                className="w-full flex items-center justify-between px-4 py-3 text-left
                  hover:bg-cosmos-700/40 transition-colors duration-300"
              >
                <span className="flex items-center gap-2.5">
                  <span className={`text-lg ${style.accent}`}>{style.icon}</span>
                  <span className="font-serif font-semibold text-parchment">{a.label}</span>
                </span>
                <span
                  className={`text-gold-500 transition-transform duration-300 ${
                    isOpen ? "rotate-180" : ""
                  }`}
                >
                  ▾
                </span>
              </button>
              <AnimatePresence initial={false}>
                {isOpen && (
                  <motion.div
                    initial={{ height: 0, opacity: 0 }}
                    animate={{ height: "auto", opacity: 1 }}
                    exit={{ height: 0, opacity: 0 }}
                    transition={{ duration: 0.35, ease: [0.22, 1, 0.36, 1] }}
                    className="overflow-hidden"
                  >
                    <div
                      className="result-content px-4 pb-4 pt-1 text-sm border-t border-gold-800/30"
                      dangerouslySetInnerHTML={{ __html: mdToHtml(a.content) }}
                    />
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
          );
        })}
      </div>
    </motion.div>
  );
}

const container = {
  hidden: {},
  show: { transition: { staggerChildren: 0.12 } },
};
const item = {
  hidden: { opacity: 0, y: 20 },
  show:   { opacity: 1, y: 0, transition: { duration: 0.6, ease: [0.22, 1, 0.36, 1] } },
};

function MasterActions({
  chart,
  birthData,
  savedProfileId,
}: {
  chart: ZiweiChart;
  birthData: BirthData;
  savedProfileId?: string | null;
}) {
  const { user } = useAuth();
  const router = useRouter();
  const [busy, setBusy] = useState<"save" | "ask" | null>(null);
  const [savedId, setSavedId] = useState<string | null>(savedProfileId ?? null);
  const [msg, setMsg] = useState<{ type: "ok" | "err"; text: string } | null>(null);

  const alreadySaved = !!savedProfileId;

  const ensureProfile = async (): Promise<string> => {
    if (savedId) return savedId;
    const label = `命盤 · ${birthData.birth_year}/${birthData.birth_month}/${birthData.birth_day}`;
    const profile = await profileApi.create({
      label,
      relation: "self",
      birth_data: birthData,
      chart,
    });
    setSavedId(profile.id);
    return profile.id;
  };

  const requireLogin = () => {
    router.push("/login?redirect=/analyze");
  };

  const handleSave = async () => {
    if (!user) return requireLogin();
    setBusy("save");
    setMsg(null);
    try {
      await ensureProfile();
      setMsg({ type: "ok", text: "命盤已儲存至「我的命盤」" });
    } catch (e) {
      setMsg({ type: "err", text: e instanceof ApiError ? e.message : "儲存失敗，請稍後再試" });
    } finally {
      setBusy(null);
    }
  };

  const handleAsk = async () => {
    if (!user) return requireLogin();
    setBusy("ask");
    setMsg(null);
    try {
      const id = await ensureProfile();
      router.push(`/master/${id}`);
    } catch (e) {
      setMsg({ type: "err", text: e instanceof ApiError ? e.message : "無法開啟對談，請稍後再試" });
      setBusy(null);
    }
  };

  return (
    <motion.div variants={item} className="card-gold rounded-3xl p-6 sm:p-8 mb-6 text-center">
      <p className="text-xs tracking-[0.35em] text-gold-500 uppercase mb-1">下一步</p>
      <h3 className="font-serif text-lg font-bold text-parchment mb-1">向大師請教</h3>
      <p className="text-xs text-parchment-muted mb-5">
        {!user
          ? "登入後即可儲存命盤、與大師對談"
          : alreadySaved
          ? "針對這份命盤，與大師深入對談"
          : "儲存此命盤，並針對你的疑問與大師深入對談"}
      </p>

      <div className="flex flex-col sm:flex-row gap-3 justify-center">
        {!alreadySaved && (
          <Button variant="ghost" size="md" onClick={handleSave} loading={busy === "save"} disabled={busy !== null}>
            {savedId ? "✓ 已儲存" : "儲存命盤"}
          </Button>
        )}
        <Button variant="gold" size="md" onClick={handleAsk} loading={busy === "ask"} disabled={busy !== null}>
          ✦ 與大師詢問
        </Button>
      </div>

      <AnimatePresence>
        {msg && (
          <motion.p
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: "auto" }}
            exit={{ opacity: 0, height: 0 }}
            className={`mt-4 text-sm ${msg.type === "ok" ? "text-emerald-300" : "text-red-400"}`}
          >
            {msg.text}
          </motion.p>
        )}
      </AnimatePresence>
    </motion.div>
  );
}

export default function ResultDisplay({
  result,
  chart,
  birthData,
  savedProfileId,
  onReset,
}: ResultDisplayProps) {
  const html = mdToHtml(result.result || "（無結果）");
  const elapsed = result.metadata?.elapsed_ms
    ? `${(result.metadata.elapsed_ms / 1000).toFixed(1)}s`
    : null;

  return (
    <motion.div
      variants={container}
      initial="hidden"
      animate="show"
      className="w-full max-w-2xl mx-auto"
    >
      {/* Header card */}
      <motion.div variants={item} className="card-gold rounded-3xl p-8 mb-6 text-center">
        <div className="flex justify-center mb-4">
          <div
            className="relative w-16 h-16"
            style={{ filter: "drop-shadow(0 0 16px rgba(201,168,76,0.6))" }}
          >
            <Image src="/icon-removebg-preview.png" alt="" fill className="object-contain" />
          </div>
        </div>
        <p className="text-xs tracking-[0.4em] text-gold-500 uppercase mb-2">命盤解析完成</p>
        <h2 className="font-serif text-2xl font-bold text-parchment">
          星象已顯
        </h2>
        {elapsed && (
          <p className="mt-2 text-xs text-parchment-muted">
            推算耗時 {elapsed} · AI Multi-Agent
          </p>
        )}
        <div className="divider-gold w-24 mx-auto mt-4" />
      </motion.div>

      {/* Integrated report card */}
      <motion.div variants={item} className="card-gold rounded-3xl p-8 mb-6">
        <p className="text-xs tracking-[0.3em] text-gold-500 uppercase mb-3 text-center">
          ✦ 首席整合報告
        </p>
        <div className="result-content" dangerouslySetInnerHTML={{ __html: html }} />
      </motion.div>

      {/* Master CTA：儲存命盤 / 與大師詢問 */}
      {chart && birthData && (
        <MasterActions chart={chart} birthData={birthData} savedProfileId={savedProfileId} />
      )}

      {/* Per-agent process (collapsible) */}
      {result.agents && result.agents.length > 0 && (
        <AgentProcess agents={result.agents} />
      )}

      {/* Metadata badge */}
      {result.metadata && (
        <motion.div variants={item} className="flex gap-3 justify-center mb-8 flex-wrap">
          {[
            { label: "分析領域", value: result.metadata.domain_type },
            {
              label: "參與代理人",
              value: `${result.metadata.agents_used ?? result.agents?.length ?? 0} 位`,
            },
          ].map((m) => (
            <div
              key={m.label}
              className="px-4 py-2 rounded-full border border-gold-800/40 bg-cosmos-800/50
                text-xs text-parchment-muted flex items-center gap-2"
            >
              <span className="text-gold-600">{m.label}</span>
              <span className="text-parchment">{m.value}</span>
            </div>
          ))}
        </motion.div>
      )}

      {/* Actions */}
      <motion.div variants={item} className="flex flex-col sm:flex-row gap-4 justify-center pb-16">
        <Button variant="gold" size="md" onClick={onReset}>
          ✦ 再次推算
        </Button>
        <Button
          variant="ghost"
          size="md"
          onClick={() => {
            const text = result.result || "";
            navigator.clipboard.writeText(text).catch(() => {});
          }}
        >
          複製結果
        </Button>
      </motion.div>
    </motion.div>
  );
}
