"use client";
import { Suspense } from "react";
import { useSearchParams } from "next/navigation";
import CosmicBackground from "@/components/CosmicBackground";
import Navbar from "@/components/Navbar";
import ChartAnalyzer from "@/components/ChartAnalyzer";
import type { DomainType } from "@/types";

function AnalyzePage() {
  const params = useSearchParams();
  const initialDomain = (params.get("domain") as DomainType) || "comprehensive";

  return (
    <main className="relative min-h-screen">
      <CosmicBackground dimOverlay />
      <Navbar />
      <div className="relative z-10 min-h-screen flex flex-col items-center justify-start pt-28 pb-16 px-4">
        <ChartAnalyzer initialDomain={initialDomain} />
      </div>
    </main>
  );
}

export default function AnalyzePageWrapper() {
  return (
    <Suspense>
      <AnalyzePage />
    </Suspense>
  );
}
