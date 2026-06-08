"use client";
import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import Button from "@/components/ui/Button";
import { subscriptionApi, ApiError } from "@/lib/api";
import { useAuth } from "@/contexts/AuthContext";
import type { SubscriptionPlan } from "@/types";

const PLAN_ICONS: Record<string, string> = {
  free: "☆",
  basic: "✦",
  premium: "✧",
};

const FEATURE_LABELS: Record<string, string> = {
  career: "事業工作算命",
  love: "感情姻緣算命",
  compatibility: "合盤分析（雙人配對）",
};

const TOKEN_COSTS = [
  { action: "與大師對話", cost: "1 代幣 / 則" },
  { action: "事業工作分析", cost: "8 代幣" },
  { action: "感情姻緣分析", cost: "8 代幣" },
  { action: "綜合命盤分析", cost: "10 代幣" },
  { action: "合盤分析", cost: "12 代幣" },
  { action: "建立新命盤", cost: "3 代幣" },
];

export default function PricingPage() {
  const { subscription, refreshSubscription } = useAuth();
  const [plans, setPlans] = useState<SubscriptionPlan[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    (async () => {
      try {
        const data = await subscriptionApi.plans();
        setPlans(data);
      } catch {
        /* ignore */
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  const handleSubscribe = async (planName: string) => {
    try {
      const result = await subscriptionApi.subscribe(planName);
      alert(result.message || "付款功能整合中");
    } catch (e) {
      alert(e instanceof ApiError ? e.message : "操作失敗");
    }
  };

  const currentPlan = subscription?.plan_name || "free";

  return (
    <div className="h-full overflow-y-auto">
      <div className="max-w-4xl mx-auto px-4 pt-16 md:pt-12 pb-16">
        <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }}>
          <div className="text-center mb-10">
            <p className="text-xs tracking-[0.4em] text-gold-500 uppercase mb-2">星辰代幣</p>
            <h1 className="font-serif text-3xl font-bold text-parchment">方案與定價</h1>
            <p className="mt-3 text-sm text-parchment-muted max-w-md mx-auto">
              選擇適合你的方案，解鎖更多命理功能
            </p>
            <div className="divider-gold w-24 mx-auto mt-4" />
          </div>

          {subscription && (
            <div className="text-center mb-8">
              <span className="inline-flex items-center gap-2 bg-cosmos-800/60 border border-gold-700/30 rounded-full px-4 py-2 text-sm">
                <span className="text-gold-400">✦</span>
                <span className="text-parchment-dim">
                  目前方案：<span className="text-gold-300 font-medium">{subscription.plan_display_name}</span>
                  {subscription.monthly_tokens !== -1 && (
                    <> · 剩餘 <span className="text-gold-300">{subscription.token_balance}</span> 星辰代幣</>
                  )}
                  {subscription.monthly_tokens === -1 && (
                    <> · <span className="text-gold-300">無限代幣</span></>
                  )}
                </span>
              </span>
            </div>
          )}

          {loading ? (
            <div className="flex justify-center py-16">
              <span className="w-5 h-5 border-2 border-gold-500 border-t-transparent rounded-full animate-spin" />
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12">
              {plans.map((plan, i) => {
                const isCurrent = plan.name === currentPlan;
                const isPopular = plan.name === "basic";
                return (
                  <motion.div
                    key={plan.id}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: i * 0.1 }}
                    className={`relative card-gold rounded-3xl p-6 flex flex-col
                      ${isCurrent ? "ring-2 ring-gold-400/60" : ""}
                      ${isPopular ? "md:-translate-y-2" : ""}`}
                  >
                    {isPopular && (
                      <div className="absolute -top-3 left-1/2 -translate-x-1/2 bg-gold-500 text-cosmos-950 text-xs font-bold px-3 py-1 rounded-full">
                        最受歡迎
                      </div>
                    )}

                    <div className="text-center mb-4">
                      <span className="text-3xl">{PLAN_ICONS[plan.name] || "✦"}</span>
                      <h3 className="font-serif text-lg font-bold text-parchment mt-2">
                        {plan.display_name}
                      </h3>
                      <div className="mt-2">
                        <span className="text-2xl font-bold text-gold-300">
                          {plan.price_twd === 0 ? "免費" : `NT$${plan.price_twd}`}
                        </span>
                        {plan.price_twd > 0 && (
                          <span className="text-xs text-parchment-muted"> / 月</span>
                        )}
                      </div>
                    </div>

                    <div className="divider-gold w-full mb-4" />

                    <div className="flex-1 space-y-3 mb-6">
                      <div className="flex items-center gap-2 text-sm">
                        <span className="text-gold-400">✦</span>
                        <span className="text-parchment-dim">
                          每月{" "}
                          {plan.monthly_tokens === -1
                            ? "無限"
                            : `${plan.monthly_tokens} 枚`}
                          {" "}星辰代幣
                        </span>
                      </div>
                      <div className="flex items-center gap-2 text-sm">
                        <span className="text-gold-400">❖</span>
                        <span className="text-parchment-dim">
                          最多{" "}
                          {plan.max_profiles === -1
                            ? "無限"
                            : `${plan.max_profiles} 個`}
                          {" "}命盤
                        </span>
                      </div>
                      {Object.entries(plan.features).map(([key, enabled]) => (
                        <div key={key} className="flex items-center gap-2 text-sm">
                          <span className={enabled ? "text-green-400" : "text-parchment-muted/40"}>
                            {enabled ? "✓" : "✗"}
                          </span>
                          <span className={enabled ? "text-parchment-dim" : "text-parchment-muted/50 line-through"}>
                            {FEATURE_LABELS[key] || key}
                          </span>
                        </div>
                      ))}
                    </div>

                    {isCurrent ? (
                      <div className="text-center text-xs text-gold-400 font-medium py-3 border border-gold-600/40 rounded-2xl">
                        目前方案
                      </div>
                    ) : plan.name === "free" ? null : (
                      <Button
                        variant="gold"
                        size="md"
                        onClick={() => handleSubscribe(plan.name)}
                        className="w-full font-serif"
                      >
                        升級至{plan.display_name}
                      </Button>
                    )}
                  </motion.div>
                );
              })}
            </div>
          )}

          <div className="card-gold rounded-3xl p-6">
            <h3 className="font-serif text-lg font-bold text-parchment mb-4 text-center">
              星辰代幣消耗表
            </h3>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              {TOKEN_COSTS.map(({ action, cost }) => (
                <div
                  key={action}
                  className="flex items-center justify-between bg-cosmos-900/50 rounded-xl px-4 py-3"
                >
                  <span className="text-sm text-parchment-dim">{action}</span>
                  <span className="text-sm text-gold-400 font-medium">{cost}</span>
                </div>
              ))}
            </div>
          </div>
        </motion.div>
      </div>
    </div>
  );
}
