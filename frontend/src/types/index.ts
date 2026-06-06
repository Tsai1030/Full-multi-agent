export interface BirthData {
  gender: "男" | "女";
  birth_year: number;
  birth_month: number;
  birth_day: number;
  birth_hour: string;
}

/** 單一星曜（iztro） */
export interface ZiweiStar {
  name: string;
  type?: string;        // major / soft / tough / lucun / tianma / adjective …
  scope?: string;       // origin / decadal / yearly …
  brightness?: string;  // 廟 / 旺 / 得 / 利 / 平 / 不 / 陷
  mutagen?: string;     // 祿 / 權 / 科 / 忌（生年四化）
}

/** 單一宮位（iztro） */
export interface ZiweiPalace {
  index: number;
  name: string;             // 命宮 / 兄弟 / 夫妻 …
  isBodyPalace: boolean;
  isOriginalPalace?: boolean;
  heavenlyStem: string;     // 天干
  earthlyBranch: string;    // 地支
  majorStars: ZiweiStar[];
  minorStars: ZiweiStar[];
  adjectiveStars: ZiweiStar[];
  decadal?: {
    range: [number, number];
    heavenlyStem: string;
    earthlyBranch: string;
  };
  ages?: number[];
}

/** 完整命盤（iztro 計算結果，序列化後） */
export interface ZiweiChart {
  gender: string;
  solarDate: string;
  lunarDate: string;
  chineseDate: string;
  time: string;
  timeRange: string;
  sign: string;                       // 星座
  zodiac: string;                     // 生肖
  soul: string;                       // 命主
  body: string;                       // 身主
  fiveElementsClass: string;          // 五行局
  earthlyBranchOfSoulPalace: string;  // 命宮地支
  earthlyBranchOfBodyPalace: string;  // 身宮地支
  palaces: ZiweiPalace[];
}

export interface AnalysisRequest {
  birth_data: BirthData;
  domain_type: DomainType;
  user_question?: string;
  chart?: ZiweiChart;
}

/** 單一 agent 的個別分析輸出 */
export interface AgentOutput {
  role: string;   // reasoning / domain / creative
  label: string;  // 顯示名稱，如「推理分析師」
  content: string;
}

export interface AnalysisResponse {
  success: boolean;
  result?: string;
  error?: string;
  agents?: AgentOutput[];
  metadata?: {
    domain_type: string;
    agents_used?: number;
    iterations?: number;
    elapsed_ms: number;
  };
}

export type DomainType = "love" | "wealth" | "future" | "comprehensive";

export interface Domain {
  id: DomainType;
  name: string;
  description: string;
  icon: string;
  color: string;
}

export type AnalysisStage = "form" | "loading" | "result";
