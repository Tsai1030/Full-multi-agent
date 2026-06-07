"use client";
import { Suspense, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";
import CosmicBackground from "@/components/CosmicBackground";
import Navbar from "@/components/Navbar";
import BirthFields from "@/components/BirthFields";
import Button from "@/components/ui/Button";
import { useAuth } from "@/contexts/AuthContext";
import { ApiError, profileApi } from "@/lib/api";
import { computeChart } from "@/lib/ziwei";
import type { BirthData } from "@/types";

function OnboardingInner() {
  const router = useRouter();
  const { user, loading: authLoading } = useAuth();

  const [birth, setBirth] = useState<BirthData>({
    gender: "男",
    birth_year: 1990,
    birth_month: 1,
    birth_day: 1,
    birth_hour: "子",
  });
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!authLoading && !user) router.replace("/login");
  }, [authLoading, user, router]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setSubmitting(true);
    try {
      const chart = computeChart(birth);
      const profile = await profileApi.create({
        label: "我的命盤",
        relation: "self",
        birth_data: birth,
        chart,
      });
      router.push(`/profiles/${profile.id}`);
    } catch (err) {
      if (err instanceof ApiError) setError(err.message);
      else setError("命盤生成失敗，請確認生辰是否正確");
      setSubmitting(false);
    }
  };

  if (authLoading || !user) {
    return (
      <main className="relative min-h-screen">
        <CosmicBackground dimOverlay />
        <Navbar />
      </main>
    );
  }

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
            <p className="text-xs tracking-[0.4em] text-gold-500 uppercase mb-2">最後一步</p>
            <h1 className="font-serif text-2xl font-bold text-parchment">填入你的生辰</h1>
            <p className="mt-2 text-xs text-parchment-muted">
              我們將為你生成專屬命盤，之後即可與大師對談
            </p>
            <div className="divider-gold w-24 mx-auto mt-4" />
          </div>

          <form onSubmit={handleSubmit} className="flex flex-col gap-5">
            <BirthFields value={birth} onChange={setBirth} />

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
              loading={submitting}
              disabled={submitting}
              className="mt-1 w-full font-serif tracking-widest"
            >
              ✦ 生成我的命盤
            </Button>
          </form>
        </motion.div>
      </div>
    </main>
  );
}

export default function OnboardingPage() {
  return (
    <Suspense>
      <OnboardingInner />
    </Suspense>
  );
}
