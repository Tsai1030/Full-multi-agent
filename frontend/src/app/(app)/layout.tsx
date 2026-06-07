"use client";
import { useEffect } from "react";
import { usePathname, useRouter } from "next/navigation";
import CosmicBackground from "@/components/CosmicBackground";
import Sidebar from "@/components/app/Sidebar";
import { useAuth } from "@/contexts/AuthContext";

export default function AppLayout({ children }: { children: React.ReactNode }) {
  const { user, loading } = useAuth();
  const router = useRouter();
  const pathname = usePathname();

  // 登入檢查：未登入 → 導去登入並記住來源
  useEffect(() => {
    if (!loading && !user) {
      router.replace(`/login?redirect=${encodeURIComponent(pathname)}`);
    }
  }, [loading, user, pathname, router]);

  return (
    <div className="relative h-[100dvh] overflow-hidden">
      <CosmicBackground dimOverlay />
      <div className="relative z-10 flex h-full">
        {user && <Sidebar />}
        <main className="flex-1 min-w-0 h-full overflow-hidden">
          {loading || !user ? (
            <div className="h-full flex items-center justify-center text-parchment-muted text-sm">
              <span className="w-5 h-5 border-2 border-gold-500 border-t-transparent rounded-full animate-spin mr-2" />
              載入中…
            </div>
          ) : (
            children
          )}
        </main>
      </div>
    </div>
  );
}
