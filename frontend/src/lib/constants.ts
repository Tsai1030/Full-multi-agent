import type { Domain } from "@/types";

export const BIRTH_HOURS = [
  { id: "子", name: "子時", time: "23:00–01:00" },
  { id: "丑", name: "丑時", time: "01:00–03:00" },
  { id: "寅", name: "寅時", time: "03:00–05:00" },
  { id: "卯", name: "卯時", time: "05:00–07:00" },
  { id: "辰", name: "辰時", time: "07:00–09:00" },
  { id: "巳", name: "巳時", time: "09:00–11:00" },
  { id: "午", name: "午時", time: "11:00–13:00" },
  { id: "未", name: "未時", time: "13:00–15:00" },
  { id: "申", name: "申時", time: "15:00–17:00" },
  { id: "酉", name: "酉時", time: "17:00–19:00" },
  { id: "戌", name: "戌時", time: "19:00–21:00" },
  { id: "亥", name: "亥時", time: "21:00–23:00" },
] as const;

export const DOMAINS: Domain[] = [
  {
    id: "comprehensive",
    name: "完整命盤",
    description: "全方位解析命盤格局與人生走向",
    icon: "✦",
    color: "from-gold-600/20 to-gold-500/5",
  },
  {
    id: "love",
    name: "感情姻緣",
    description: "桃花運勢、夫妻緣分、感情走向",
    icon: "◎",
    color: "from-rose-900/20 to-rose-800/5",
  },
  {
    id: "wealth",
    name: "財富事業",
    description: "財帛宮解析、事業格局、投資時機",
    icon: "◇",
    color: "from-amber-900/20 to-amber-800/5",
  },
  {
    id: "future",
    name: "流年運勢",
    description: "大限流年、近期趨勢、注意事項",
    icon: "◈",
    color: "from-violet-900/20 to-violet-800/5",
  },
];

export const LOADING_MESSAGES = [
  "正在推算命盤格局…",
  "連結星象宇宙能量…",
  "解讀十二宮位星曜…",
  "分析四化飛星方位…",
  "整合三方四正資訊…",
  "撰寫命理解析報告…",
];

export const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
