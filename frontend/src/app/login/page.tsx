"use client";
import { Suspense, useCallback, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";
import CosmicBackground from "@/components/CosmicBackground";
import Navbar from "@/components/Navbar";
import BirthFields from "@/components/BirthFields";
import GoogleSignInButton from "@/components/GoogleSignInButton";
import Button from "@/components/ui/Button";
import { GoldInput } from "@/components/ui/GoldSelect";
import { useAuth } from "@/contexts/AuthContext";
import { ApiError, profileApi } from "@/lib/api";
import { computeChart } from "@/lib/ziwei";
import type { BirthData } from "@/types";

type Mode = "login" | "register";

function LoginInner() {
  const router = useRouter();
  const params = useSearchParams();
  const redirect = params.get("redirect") || "/analyze";
  const { login, register, googleLogin } = useAuth();

  const [mode, setMode] = useState<Mode>("login");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [displayName, setDisplayName] = useState("");
  const [birth, setBirth] = useState<BirthData>({
    gender: "男",
    birth_year: 1990,
    birth_month: 1,
    birth_day: 1,
    birth_hour: "子",
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // 登入後依是否已有命盤決定去向
  const routeAfterAuth = useCallback(
    (hasProfile: boolean) => {
      if (!hasProfile) router.push(`/onboarding?redirect=${encodeURIComponent(redirect)}`);
      else router.push(redirect);
    },
    [router, redirect],
  );

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
      if (mode === "login") {
        const res = await login(email, password);
        routeAfterAuth(res.has_profile);
      } else {
        // 註冊：前端用 iztro 排盤，連同帳號主人的生辰一起建立主命盤
        const chart = computeChart(birth);
        await register(email, password, displayName, birth, chart);
        const profiles = await profileApi.list();
        router.push(profiles[0] ? `/profiles/${profiles[0].id}` : redirect);
      }
    } catch (err) {
      if (err instanceof ApiError) setError(err.message);
      else if (err instanceof Error && err.message.includes("Invalid"))
        setError("命盤計算失敗，請確認生辰是否正確");
      else setError("連線失敗，請確認後端服務是否正常");
    } finally {
      setLoading(false);
    }
  };

  const handleGoogle = useCallback(
    async (credential: string) => {
      setError(null);
      setLoading(true);
      try {
        const res = await googleLogin(credential);
        routeAfterAuth(res.has_profile);
      } catch (err) {
        setError(err instanceof ApiError ? err.message : "Google 登入失敗");
      } finally {
        setLoading(false);
      }
    },
    [googleLogin, routeAfterAuth],
  );

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
          <div className="text-center mb-7">
            <p className="text-xs tracking-[0.4em] text-gold-500 uppercase mb-2">
              {mode === "login" ? "登入" : "註冊"}
            </p>
            <h1 className="font-serif text-2xl font-bold text-parchment">
              {mode === "login" ? "歡迎回來" : "建立帳號"}
            </h1>
            <p className="mt-2 text-xs text-parchment-muted">
              {mode === "login"
                ? "登入後即可儲存命盤、與大師對談"
                : "填入你的生辰，註冊後立即生成你的專屬命盤"}
            </p>
            <div className="divider-gold w-24 mx-auto mt-4" />
          </div>

          <form onSubmit={handleSubmit} className="flex flex-col gap-5">
            {mode === "register" && (
              <GoldInput
                label="顯示名稱"
                value={displayName}
                onChange={(e) => setDisplayName(e.target.value)}
                placeholder="你的稱呼"
                autoComplete="name"
              />
            )}

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

            {mode === "register" && (
              <div className="pt-2 border-t border-gold-800/30">
                <p className="text-xs tracking-[0.3em] text-gold-500 uppercase mb-4 text-center">
                  你的生辰
                </p>
                <BirthFields value={birth} onChange={setBirth} />
              </div>
            )}

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
              className="mt-1 w-full font-serif tracking-widest"
            >
              {mode === "login" ? "✦ 登入" : "✦ 註冊並生成命盤"}
            </Button>
          </form>

          {/* Google 登入（未設定 client id 時自動隱藏） */}
          <div className="mt-6 flex flex-col items-center gap-4">
            <div className="flex items-center gap-3 w-full text-parchment-muted/60 text-xs">
              <div className="flex-1 h-px bg-gold-800/30" />
              或
              <div className="flex-1 h-px bg-gold-800/30" />
            </div>
            <GoogleSignInButton onCredential={handleGoogle} />
          </div>

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
