"use client";
import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import Link from "next/link";
import Button from "@/components/ui/Button";
import { subscriptionApi, tokenApi, ApiError } from "@/lib/api";
import { useAuth } from "@/contexts/AuthContext";
import type { TokenTransaction } from "@/types";

const ACTION_LABELS: Record<string, string> = {
  monthly_allocation: "每月代幣發放",
  chat_message: "大師對話",
  fortune_followup: "算命追問",
  profile_create: "建立命盤",
  career_analysis: "事業分析",
  love_analysis: "感情分析",
  comprehensive_analysis: "綜合分析",
  compatibility_analysis: "合盤分析",
  admin_grant: "系統贈送",
};

export default function AccountPage() {
  const { user, subscription, refreshSubscription } = useAuth();
  const [transactions, setTransactions] = useState<TokenTransaction[]>([]);
  const [loadingTx, setLoadingTx] = useState(true);

  useEffect(() => {
    (async () => {
      try {
        const txs = await tokenApi.history(1);
        setTransactions(txs);
      } catch {
        /* ignore */
      } finally {
        setLoadingTx(false);
      }
    })();
  }, []);

  const handleCancel = async () => {
    if (!confirm("確定要取消訂閱嗎？取消後將在當期結束時生效。")) return;
    try {
      await subscriptionApi.cancel();
      await refreshSubscription();
      alert("訂閱將在當期結束後取消");
    } catch (e) {
      alert(e instanceof ApiError ? e.message : "操作失敗");
    }
  };

  return (
    <div className="h-full overflow-y-auto">
      <div className="max-w-2xl mx-auto px-4 pt-16 md:pt-12 pb-16">
        <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }}>
          <div className="text-center mb-8">
            <p className="text-xs tracking-[0.4em] text-gold-500 uppercase mb-2">帳號管理</p>
            <h1 className="font-serif text-3xl font-bold text-parchment">我的帳號</h1>
            <div className="divider-gold w-24 mx-auto mt-4" />
          </div>

          {/* User info */}
          <div className="card-gold rounded-3xl p-6 mb-6">
            <h3 className="font-serif text-base font-bold text-parchment mb-4">個人資料</h3>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-parchment-muted">姓名</span>
                <span className="text-parchment">{user?.display_name}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-parchment-muted">Email</span>
                <span className="text-parchment">{user?.email}</span>
              </div>
            </div>
          </div>

          {/* Subscription */}
          {subscription && (
            <div className="card-gold rounded-3xl p-6 mb-6">
              <h3 className="font-serif text-base font-bold text-parchment mb-4">訂閱方案</h3>
              <div className="space-y-2 text-sm mb-4">
                <div className="flex justify-between">
                  <span className="text-parchment-muted">目前方案</span>
                  <span className="text-gold-300 font-medium">{subscription.plan_display_name}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-parchment-muted">星辰代幣</span>
                  <span className="text-gold-300 font-medium">
                    {subscription.monthly_tokens === -1 ? "無限" : subscription.token_balance}
                  </span>
                </div>
                {subscription.period_end && (
                  <div className="flex justify-between">
                    <span className="text-parchment-muted">當期結束</span>
                    <span className="text-parchment">{new Date(subscription.period_end).toLocaleDateString("zh-TW")}</span>
                  </div>
                )}
                <div className="flex justify-between">
                  <span className="text-parchment-muted">狀態</span>
                  <span className={`font-medium ${
                    subscription.cancel_at_period_end ? "text-yellow-400" : "text-green-400"
                  }`}>
                    {subscription.cancel_at_period_end ? "將於當期結束取消" : "生效中"}
                  </span>
                </div>
              </div>

              <div className="flex gap-3">
                <Link href="/pricing" className="flex-1">
                  <Button variant="gold" size="sm" className="w-full">
                    {subscription.plan_name === "free" ? "升級方案" : "變更方案"}
                  </Button>
                </Link>
                {subscription.plan_name !== "free" && !subscription.cancel_at_period_end && (
                  <Button variant="ghost" size="sm" onClick={handleCancel}>
                    取消訂閱
                  </Button>
                )}
              </div>
            </div>
          )}

          {/* Token history */}
          <div className="card-gold rounded-3xl p-6">
            <h3 className="font-serif text-base font-bold text-parchment mb-4">代幣紀錄</h3>
            {loadingTx ? (
              <div className="flex justify-center py-8">
                <span className="w-5 h-5 border-2 border-gold-500 border-t-transparent rounded-full animate-spin" />
              </div>
            ) : transactions.length === 0 ? (
              <p className="text-sm text-parchment-muted text-center py-4">尚無代幣紀錄</p>
            ) : (
              <div className="space-y-2">
                {transactions.map((tx) => (
                  <div
                    key={tx.id}
                    className="flex items-center justify-between bg-cosmos-900/50 rounded-xl px-4 py-3"
                  >
                    <div>
                      <span className="text-sm text-parchment-dim">
                        {ACTION_LABELS[tx.action] || tx.action}
                      </span>
                      <span className="text-xs text-parchment-muted ml-2">
                        {new Date(tx.created_at).toLocaleString("zh-TW")}
                      </span>
                    </div>
                    <span className={`text-sm font-medium ${tx.amount > 0 ? "text-green-400" : "text-red-400"}`}>
                      {tx.amount > 0 ? `+${tx.amount}` : tx.amount}
                    </span>
                  </div>
                ))}
              </div>
            )}
          </div>
        </motion.div>
      </div>
    </div>
  );
}
