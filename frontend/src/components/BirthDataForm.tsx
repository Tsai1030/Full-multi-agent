"use client";
import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { GoldSelect, GoldInput } from "@/components/ui/GoldSelect";
import Button from "@/components/ui/Button";
import { BIRTH_HOURS, DOMAINS } from "@/lib/constants";
import type { BirthData, DomainType, AnalysisRequest } from "@/types";

interface BirthDataFormProps {
  initialDomain?: DomainType;
  onSubmit: (req: AnalysisRequest) => void;
  loading?: boolean;
  error?: string | null;
}

const currentYear = new Date().getFullYear();

export default function BirthDataForm({
  initialDomain = "comprehensive",
  onSubmit,
  loading = false,
  error,
}: BirthDataFormProps) {
  const [birth, setBirth] = useState<BirthData>({
    gender: "男",
    birth_year: 1990,
    birth_month: 1,
    birth_day: 1,
    birth_hour: "子",
  });
  const [domain, setDomain] = useState<DomainType>(initialDomain);
  const [question, setQuestion] = useState("");
  const [touched, setTouched] = useState(false);

  const validate = () => {
    if (!birth.gender || !birth.birth_year || !birth.birth_month || !birth.birth_day || !birth.birth_hour) {
      return "請填寫完整出生資料";
    }
    if (birth.birth_year < 1900 || birth.birth_year > currentYear) {
      return `出生年份需介於 1900–${currentYear}`;
    }
    return null;
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setTouched(true);
    const err = validate();
    if (err) return;
    onSubmit({ birth_data: birth, domain_type: domain, user_question: question });
  };

  const fieldError = touched ? validate() : null;

  return (
    <motion.div
      initial={{ opacity: 0, y: 40, scale: 0.97 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      transition={{ duration: 0.8, ease: [0.22, 1, 0.36, 1] }}
      className="card-gold p-8 md:p-10 rounded-3xl w-full max-w-lg mx-auto"
    >
      {/* Header */}
      <div className="text-center mb-8">
        <p className="text-xs tracking-[0.4em] text-gold-500 uppercase mb-2">紫微斗數推算</p>
        <h2 className="font-serif text-2xl font-bold text-parchment">
          輸入出生資料
        </h2>
        <div className="divider-gold w-24 mx-auto mt-4" />
      </div>

      <form onSubmit={handleSubmit} className="flex flex-col gap-5">
        {/* Gender */}
        <div className="flex flex-col gap-1.5">
          <label className="text-xs font-medium tracking-widest text-gold-500 uppercase">
            性別
          </label>
          <div className="flex gap-3">
            {(["男", "女"] as const).map((g) => (
              <button
                key={g}
                type="button"
                onClick={() => setBirth((b) => ({ ...b, gender: g }))}
                className={`flex-1 py-3 rounded-xl border text-sm font-medium transition-all duration-300 ${
                  birth.gender === g
                    ? "border-gold-500 bg-gold-500/10 text-gold-400 shadow-gold-sm"
                    : "border-white/10 text-parchment-muted hover:border-gold-700"
                }`}
              >
                {g === "男" ? "♂ 男" : "♀ 女"}
              </button>
            ))}
          </div>
        </div>

        {/* Birth year / month / day row */}
        <div className="grid grid-cols-3 gap-3">
          <GoldInput
            label="年"
            type="number"
            min={1900}
            max={currentYear}
            value={birth.birth_year}
            onChange={(e) => setBirth((b) => ({ ...b, birth_year: +e.target.value }))}
            placeholder="1990"
          />
          <GoldSelect
            label="月"
            value={birth.birth_month}
            onChange={(e) => setBirth((b) => ({ ...b, birth_month: +e.target.value }))}
          >
            {Array.from({ length: 12 }, (_, i) => i + 1).map((m) => (
              <option key={m} value={m}>{m} 月</option>
            ))}
          </GoldSelect>
          <GoldSelect
            label="日"
            value={birth.birth_day}
            onChange={(e) => setBirth((b) => ({ ...b, birth_day: +e.target.value }))}
          >
            {Array.from({ length: 31 }, (_, i) => i + 1).map((d) => (
              <option key={d} value={d}>{d} 日</option>
            ))}
          </GoldSelect>
        </div>

        {/* Birth hour */}
        <GoldSelect
          label="出生時辰"
          value={birth.birth_hour}
          onChange={(e) => setBirth((b) => ({ ...b, birth_hour: e.target.value }))}
        >
          {BIRTH_HOURS.map((h) => (
            <option key={h.id} value={h.id}>
              {h.name}（{h.time}）
            </option>
          ))}
        </GoldSelect>

        {/* Domain selector */}
        <div className="flex flex-col gap-1.5">
          <label className="text-xs font-medium tracking-widest text-gold-500 uppercase">
            分析領域
          </label>
          <div className="grid grid-cols-2 gap-2">
            {DOMAINS.map((d) => (
              <button
                key={d.id}
                type="button"
                onClick={() => setDomain(d.id)}
                className={`px-3 py-2.5 rounded-xl border text-sm font-medium transition-all duration-300 text-left ${
                  domain === d.id
                    ? "border-gold-500 bg-gold-500/10 text-gold-400 shadow-gold-sm"
                    : "border-white/10 text-parchment-muted hover:border-gold-700"
                }`}
              >
                <span className="mr-1.5 opacity-80">{d.icon}</span>
                {d.name}
              </button>
            ))}
          </div>
        </div>

        {/* Optional question */}
        <div className="flex flex-col gap-1.5">
          <label className="text-xs font-medium tracking-widest text-gold-500 uppercase">
            具體問題 <span className="text-parchment-muted normal-case tracking-normal">（選填）</span>
          </label>
          <textarea
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            placeholder="例如：今年的事業運勢如何？有無貴人相助？"
            rows={2}
            className="input-mystic rounded-xl px-4 py-3 text-sm resize-none"
          />
        </div>

        {/* Validation error */}
        <AnimatePresence>
          {(fieldError || error) && (
            <motion.p
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: "auto" }}
              exit={{ opacity: 0, height: 0 }}
              className="text-sm text-red-400 text-center"
            >
              {fieldError || error}
            </motion.p>
          )}
        </AnimatePresence>

        {/* Submit */}
        <Button
          type="submit"
          variant="gold"
          size="lg"
          loading={loading}
          disabled={loading}
          className="mt-2 w-full font-serif tracking-widest"
        >
          {loading ? "推算中…" : "✦ 開始推算命盤"}
        </Button>
      </form>
    </motion.div>
  );
}
