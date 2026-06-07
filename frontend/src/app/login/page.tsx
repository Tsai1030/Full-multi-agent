"use client";
import { Suspense, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";
import CosmicBackground from "@/components/CosmicBackground";
import Navbar from "@/components/Navbar";
import Button from "@/components/ui/Button";
import { GoldInput } from "@/components/ui/GoldSelect";
import { useAuth } from "@/contexts/AuthContext";
import { ApiError } from "@/lib/api";

type Mode = "login" | "register";

function LoginInner() {
  const router = useRouter();
  const params = useSearchParams();
  const redirect = params.get("redirect") || "/analyze";
  const { login, register } = useAuth();

  const [mode, setMode] = useState<Mode>("login");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [displayName, setDisplayName] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    if (!email || !password || (mode === "register" && !displayName)) {
      setError("請填寫完整資料");
      return;
    }
    if (password.length < 6) {
      setError("密碼至少需 6 個字元");
      return;
    }

    setLoading(true);
    try {
      if (mode === "login") await login(email, password);
      else await register(email, password, displayName);
      router.push(redirect);
    } catch (err) {
      if (err instanceof ApiError) setError(err.message);
      else setError("連線失敗，請確認後端服務是否正常");
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="relative min-h-screen">
      <CosmicBackground dimOverlay />
      <Navbar />

      <div className="relative z-10 min-h-screen flex flex-col items-center justify-center px-4 py-28">
        <motion.div
          initial={{ opacity: 0, y: 40, scale: 0.97 }}
          animate={{ opacity: 1, y: 0, scale: 1 }}
          transition={{ duration: 0.8, ease: [0.22, 1, 0.36, 1] }}
          className="card-gold p-8 md:p-10 rounded-3xl w-full max-w-md"
        >
          <div className="text-center mb-8">
            <p className="text-xs tracking-[0.4em] text-gold-500 uppercase mb-2">
              {mode === "login" ? "登入" : "註冊"}
            </p>
            <h1 className="font-serif text-2xl font-bold text-parchment">
              {mode === "login" ? "歡迎回來" : "建立帳號"}
            </h1>
            <p className="mt-2 text-xs text-parchment-muted">
              登入後即可儲存命盤、與大師對談
            </p>
            <div className="divider-gold w-24 mx-auto mt-4" />
          </div>

          <form onSubmit={handleSubmit} className="flex flex-col gap-5">
            <AnimatePresence mode="wait">
              {mode === "register" && (
                <motion.div
                  key="name"
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: "auto" }}
                  exit={{ opacity: 0, height: 0 }}
                >
                  <GoldInput
                    label="顯示名稱"
                    value={displayName}
                    onChange={(e) => setDisplayName(e.target.value)}
                    placeholder="你的稱呼"
                    autoComplete="name"
                  />
                </motion.div>
              )}
            </AnimatePresence>

            <GoldInput
              label="Email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="you@example.com"
              autoComplete="email"
            />
            <GoldInput
              label="密碼"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="至少 6 個字元"
              autoComplete={mode === "login" ? "current-password" : "new-password"}
            />

            <AnimatePresence>
              {error && (
                <motion.p
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: "auto" }}
                  exit={{ opacity: 0, height: 0 }}
                  className="text-sm text-red-400 text-center"
                >
                  {error}
                </motion.p>
              )}
            </AnimatePresence>

            <Button
              type="submit"
              variant="gold"
              size="lg"
              loading={loading}
              disabled={loading}
              className="mt-2 w-full font-serif tracking-widest"
            >
              {mode === "login" ? "✦ 登入" : "✦ 註冊"}
            </Button>
          </form>

          <p className="mt-6 text-center text-sm text-parchment-muted">
            {mode === "login" ? "還沒有帳號？" : "已經有帳號了？"}
            <button
              type="button"
              onClick={() => {
                setMode(mode === "login" ? "register" : "login");
                setError(null);
              }}
              className="ml-2 text-gold-400 hover:text-gold-300 transition-colors"
            >
              {mode === "login" ? "立即註冊" : "前往登入"}
            </button>
          </p>
        </motion.div>
      </div>
    </main>
  );
}

export default function LoginPage() {
  return (
    <Suspense>
      <LoginInner />
    </Suspense>
  );
}
