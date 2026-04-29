import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "紫微星盤 · AI 命理解析",
  description: "以 AI Multi-Agent 技術推算紫微斗數，探索命盤星象的深層意涵",
  icons: { icon: "/icon-removebg-preview.png" },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="zh-TW" suppressHydrationWarning>
      <body className="font-sans antialiased">{children}</body>
    </html>
  );
}
