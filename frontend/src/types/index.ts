export interface BirthData {
  gender: "男" | "女";
  birth_year: number;
  birth_month: number;
  birth_day: number;
  birth_hour: string;
}

export interface AnalysisRequest {
  birth_data: BirthData;
  domain_type: DomainType;
  user_question?: string;
}

export interface AnalysisResponse {
  success: boolean;
  result?: string;
  error?: string;
  metadata?: {
    domain_type: string;
    iterations: number;
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
