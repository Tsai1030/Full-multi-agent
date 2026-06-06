"use client";
import { motion } from "framer-motion";
import type { ZiweiChart as ZiweiChartType, ZiweiPalace, ZiweiStar } from "@/types";

interface ZiweiChartProps {
  chart: ZiweiChartType;
}

/** 地支 → 4×4 盤面格位（CSS grid，1-indexed） */
const BRANCH_POS: Record<string, { r: number; c: number }> = {
  巳: { r: 1, c: 1 }, 午: { r: 1, c: 2 }, 未: { r: 1, c: 3 }, 申: { r: 1, c: 4 },
  辰: { r: 2, c: 1 },                                         酉: { r: 2, c: 4 },
  卯: { r: 3, c: 1 },                                         戌: { r: 3, c: 4 },
  寅: { r: 4, c: 1 }, 丑: { r: 4, c: 2 }, 子: { r: 4, c: 3 }, 亥: { r: 4, c: 4 },
};

/** 生年四化顏色 */
const MUTAGEN_STYLE: Record<string, string> = {
  祿: "bg-emerald-500/20 text-emerald-300 border-emerald-400/40",
  權: "bg-sky-500/20 text-sky-300 border-sky-400/40",
  科: "bg-gold-400/20 text-gold-300 border-gold-400/40",
  忌: "bg-rose-500/20 text-rose-300 border-rose-400/40",
};

function StarBadge({ star, kind }: { star: ZiweiStar; kind: "major" | "minor" | "adj" }) {
  const color =
    kind === "major"
      ? "text-gold-200 font-semibold"
      : kind === "minor"
      ? "text-parchment-dim"
      : "text-parchment-muted";
  const size = kind === "major" ? "text-[13px]" : "text-[11px]";
  return (
    <span className={`inline-flex items-baseline gap-px leading-tight ${color} ${size}`}>
      <span>{star.name}</span>
      {star.brightness && (
        <span className="text-[9px] text-parchment-muted/80">{star.brightness}</span>
      )}
      {star.mutagen && (
        <span
          className={`ml-0.5 px-1 rounded-sm border text-[9px] leading-none py-px ${
            MUTAGEN_STYLE[star.mutagen] ?? "bg-white/10 text-parchment border-white/20"
          }`}
        >
          {star.mutagen}
        </span>
      )}
    </span>
  );
}

function PalaceCell({ palace }: { palace: ZiweiPalace }) {
  const pos = BRANCH_POS[palace.earthlyBranch];
  if (!pos) return null;

  return (
    <div
      style={{ gridRow: pos.r, gridColumn: pos.c }}
      className="relative flex flex-col justify-between p-1.5 sm:p-2 border border-gold-800/40
                 bg-cosmos-900/40 hover:bg-cosmos-700/40 transition-colors duration-300 overflow-hidden"
    >
      {/* 身宮標記 */}
      {palace.isBodyPalace && (
        <span className="absolute top-1 right-1 text-[9px] px-1 rounded-sm bg-mystic-500/25
                         text-mystic-300 border border-mystic-400/40">
          身
        </span>
      )}

      {/* 星曜 */}
      <div className="flex flex-col gap-0.5 min-h-0">
        <div className="flex flex-wrap gap-x-1.5 gap-y-0.5">
          {palace.majorStars.map((s) => (
            <StarBadge key={s.name} star={s} kind="major" />
          ))}
        </div>
        <div className="flex flex-wrap gap-x-1.5 gap-y-0.5">
          {palace.minorStars.map((s) => (
            <StarBadge key={s.name} star={s} kind="minor" />
          ))}
        </div>
        <div className="flex flex-wrap gap-x-1 gap-y-0.5">
          {palace.adjectiveStars.map((s) => (
            <StarBadge key={s.name} star={s} kind="adj" />
          ))}
        </div>
      </div>

      {/* 底部：大限 / 宮名 / 干支 */}
      <div className="flex items-end justify-between mt-1 pt-1 border-t border-gold-800/25">
        <div className="flex flex-col gap-0.5">
          {palace.decadal?.range && (
            <span className="text-[9px] text-parchment-muted">
              {palace.decadal.range[0]}–{palace.decadal.range[1]}
            </span>
          )}
          <span className="text-[10px] text-parchment-muted/70">
            {palace.heavenlyStem}
            {palace.earthlyBranch}
          </span>
        </div>
        <span className="text-[12px] font-serif font-semibold text-gold-400 tracking-wide">
          {palace.name}
        </span>
      </div>
    </div>
  );
}

function CenterInfo({ chart }: { chart: ZiweiChartType }) {
  const rows: [string, string][] = [
    ["性別", chart.gender],
    ["陽曆", chart.solarDate],
    ["農曆", chart.lunarDate],
    ["四柱", chart.chineseDate],
    ["時辰", `${chart.time}（${chart.timeRange}）`],
    ["生肖", chart.zodiac],
    ["星座", chart.sign],
    ["命主", chart.soul],
    ["身主", chart.body],
  ];

  return (
    <div
      style={{ gridRow: "2 / span 2", gridColumn: "2 / span 2" }}
      className="flex flex-col items-center justify-center p-3 text-center
                 bg-cosmos-950/60 border border-gold-700/30"
    >
      <p className="text-[10px] tracking-[0.3em] text-gold-500 uppercase mb-1">命盤</p>
      <h3 className="font-serif text-lg sm:text-xl font-bold text-gold-gradient mb-0.5">
        {chart.fiveElementsClass}
      </h3>
      <div className="divider-gold w-16 my-2" />
      <dl className="grid grid-cols-[auto_1fr] gap-x-2 gap-y-1 text-left text-[11px] leading-snug">
        {rows.map(([k, v]) => (
          <div key={k} className="contents">
            <dt className="text-gold-600 whitespace-nowrap">{k}</dt>
            <dd className="text-parchment-dim">{v}</dd>
          </div>
        ))}
      </dl>
    </div>
  );
}

export default function ZiweiChart({ chart }: ZiweiChartProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.7, ease: [0.22, 1, 0.36, 1] }}
      className="w-full max-w-3xl mx-auto"
    >
      <div className="text-center mb-4">
        <p className="text-xs tracking-[0.4em] text-gold-500 uppercase mb-1">紫微斗數命盤</p>
        <h2 className="font-serif text-xl font-bold text-parchment">星曜十二宮</h2>
      </div>

      {/* 盤面（小螢幕可橫向捲動） */}
      <div className="overflow-x-auto pb-2">
        <div
          className="grid grid-cols-4 grid-rows-4 gap-px mx-auto rounded-xl overflow-hidden
                     border border-gold-700/40 bg-gold-800/20 shadow-card"
          style={{ width: "min(100%, 720px)", minWidth: 560, aspectRatio: "1 / 1" }}
        >
          {chart.palaces.map((p) => (
            <PalaceCell key={p.index} palace={p} />
          ))}
          <CenterInfo chart={chart} />
        </div>
      </div>

      <p className="mt-3 text-[11px] text-parchment-muted text-center">
        命盤由 iztro 排盤引擎精準計算 · 紅字為生年四化（祿權科忌）
      </p>
    </motion.div>
  );
}
