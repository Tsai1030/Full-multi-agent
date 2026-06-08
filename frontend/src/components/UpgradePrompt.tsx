"use client";
import { useRouter } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";
import Button from "@/components/ui/Button";
import type { ApiErrorDetail } from "@/types";

interface UpgradePromptProps {
  open: boolean;
  onClose: () => void;
  error: ApiErrorDetail | null;
}

const PLAN_DISPLAY: Record<string, string> = {
  basic: "基本方案（NT$100/月）",
  premium: "高級方案（NT$300/月）",
};

export default function UpgradePrompt({ open, onClose, error }: UpgradePromptProps) {
  const router = useRouter();
  if (!error) return null;

  const isFeatureLocked = error.error === "feature_locked";
  const isInsufficientTokens = error.error === "insufficient_tokens";
  const isProfileLimit = error.error === "profile_limit";

  let title = "升級方案";
  let description = "";
  let icon = "✦";

  if (isFeatureLocked) {
    title = "功能尚未解鎖";
    description = `此功能需要升級至${PLAN_DISPLAY[error.required_plan || "basic"]}才能使用。`;
    icon = "🔒";
  } else if (isInsufficientTokens) {
    title = "星辰代幣不足";
    description = `此操作需要 ${error.required} 星辰代幣，您目前剩餘 ${error.balance} 枚。升級方案可獲得更多代幣。`;
    icon = "✦";
  } else if (isProfileLimit) {
    title = "命盤數量已達上限";
    description = error.message || "升級方案可儲存更多命盤。";
    icon = "❖";
  }

  return (
    <AnimatePresence>
      {open && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm px-4"
          onClick={onClose}
        >
          <motion.div
            initial={{ scale: 0.9, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            exit={{ scale: 0.9, opacity: 0 }}
            className="card-gold rounded-3xl p-8 max-w-md w-full text-center flex flex-col items-center gap-5"
            onClick={(e) => e.stopPropagation()}
          >
            <span className="text-4xl">{icon}</span>
            <h2 className="font-serif text-xl font-bold text-parchment">{title}</h2>
            <p className="text-sm text-parchment-muted leading-relaxed">{description}</p>
            <div className="flex gap-3 w-full">
              <Button
                variant="ghost"
                size="md"
                onClick={onClose}
                className="flex-1"
              >
                稍後再說
              </Button>
              <Button
                variant="gold"
                size="md"
                onClick={() => {
                  onClose();
                  router.push("/pricing");
                }}
                className="flex-1"
              >
                查看方案
              </Button>
            </div>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
