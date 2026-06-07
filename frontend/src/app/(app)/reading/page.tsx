"use client";
import ChartAnalyzer from "@/components/ChartAnalyzer";

export default function ReadingPage() {
  return (
    <div className="h-full overflow-y-auto">
      <div className="w-full flex flex-col items-center px-4 pt-16 md:pt-12 pb-16">
        <ChartAnalyzer />
      </div>
    </div>
  );
}
