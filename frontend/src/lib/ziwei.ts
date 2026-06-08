import { astro } from "iztro";
import { BIRTH_HOURS } from "@/lib/constants";
import type { BirthData, ZiweiChart, ZiweiPalace, ZiweiStar } from "@/types";

function toStar(star: { name: string; type?: string; scope?: string; brightness?: string; mutagen?: string }): ZiweiStar {
  return {
    name: star.name,
    type: star.type,
    scope: star.scope,
    brightness: star.brightness || undefined,
    mutagen: star.mutagen || undefined,
  };
}

function toPalace(palace: any): ZiweiPalace {
  return {
    index: palace.index,
    name: palace.name,
    isBodyPalace: palace.isBodyPalace,
    isOriginalPalace: palace.isOriginalPalace,
    heavenlyStem: palace.heavenlyStem,
    earthlyBranch: palace.earthlyBranch,
    majorStars: palace.majorStars.map(toStar),
    minorStars: palace.minorStars.map(toStar),
    adjectiveStars: palace.adjectiveStars.map(toStar),
    decadal: palace.decadal
      ? {
          range: palace.decadal.range,
          heavenlyStem: palace.decadal.heavenlyStem,
          earthlyBranch: palace.decadal.earthlyBranch,
        }
      : undefined,
    ages: palace.ages,
  };
}

/** 依生辰資料用 iztro 排出紫微斗數命盤（陽曆排盤） */
export function computeChart(birth: BirthData): ZiweiChart {
  const timeIndex = BIRTH_HOURS.findIndex((h) => h.id === birth.birth_hour);
  const solarDate = `${birth.birth_year}-${birth.birth_month}-${birth.birth_day}`;
  const astrolabe = astro.bySolar(solarDate, timeIndex < 0 ? 0 : timeIndex, birth.gender, true, "zh-TW");

  return {
    gender: astrolabe.gender,
    solarDate: astrolabe.solarDate,
    lunarDate: astrolabe.lunarDate,
    chineseDate: astrolabe.chineseDate,
    time: astrolabe.time,
    timeRange: astrolabe.timeRange,
    sign: astrolabe.sign,
    zodiac: astrolabe.zodiac,
    soul: astrolabe.soul,
    body: astrolabe.body,
    fiveElementsClass: astrolabe.fiveElementsClass,
    earthlyBranchOfSoulPalace: astrolabe.earthlyBranchOfSoulPalace,
    earthlyBranchOfBodyPalace: astrolabe.earthlyBranchOfBodyPalace,
    palaces: astrolabe.palaces.map(toPalace),
  };
}
