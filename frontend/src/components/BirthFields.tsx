"use client";
import { GoldSelect, GoldInput } from "@/components/ui/GoldSelect";
import { BIRTH_HOURS } from "@/lib/constants";
import type { BirthData } from "@/types";

interface BirthFieldsProps {
  value: BirthData;
  onChange: (next: BirthData) => void;
}

const currentYear = new Date().getFullYear();

/** 生辰輸入欄位（性別 / 年 / 月 / 日 / 時辰）— 註冊與補命盤共用 */
export default function BirthFields({ value, onChange }: BirthFieldsProps) {
  const set = (patch: Partial<BirthData>) => onChange({ ...value, ...patch });

  return (
    <div className="flex flex-col gap-5">
      {/* Gender */}
      <div className="flex flex-col gap-1.5">
        <label className="text-xs font-medium tracking-widest text-gold-500 uppercase">性別</label>
        <div className="flex gap-3">
          {(["男", "女"] as const).map((g) => (
            <button
              key={g}
              type="button"
              onClick={() => set({ gender: g })}
              className={`flex-1 py-3 rounded-xl border text-sm font-medium transition-all duration-300 ${
                value.gender === g
                  ? "border-gold-500 bg-gold-500/10 text-gold-400 shadow-gold-sm"
                  : "border-white/10 text-parchment-muted hover:border-gold-700"
              }`}
            >
              {g === "男" ? "♂ 男" : "♀ 女"}
            </button>
          ))}
        </div>
      </div>

      {/* Year / Month / Day */}
      <div className="grid grid-cols-3 gap-3">
        <GoldInput
          label="年"
          type="number"
          min={1900}
          max={currentYear}
          value={value.birth_year}
          onChange={(e) => set({ birth_year: +e.target.value })}
          placeholder="1990"
        />
        <GoldSelect label="月" value={value.birth_month} onChange={(e) => set({ birth_month: +e.target.value })}>
          {Array.from({ length: 12 }, (_, i) => i + 1).map((m) => (
            <option key={m} value={m}>{m} 月</option>
          ))}
        </GoldSelect>
        <GoldSelect label="日" value={value.birth_day} onChange={(e) => set({ birth_day: +e.target.value })}>
          {Array.from({ length: 31 }, (_, i) => i + 1).map((d) => (
            <option key={d} value={d}>{d} 日</option>
          ))}
        </GoldSelect>
      </div>

      {/* Birth hour */}
      <GoldSelect
        label="出生時辰"
        value={value.birth_hour}
        onChange={(e) => set({ birth_hour: e.target.value })}
      >
        {BIRTH_HOURS.map((h) => (
          <option key={h.id} value={h.id}>
            {h.name}（{h.time}）
          </option>
        ))}
      </GoldSelect>
    </div>
  );
}
