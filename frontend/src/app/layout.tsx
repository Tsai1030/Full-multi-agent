import type { Metadata } from "next";
import "./globals.css";
import { AuthProvider } from "@/contexts/AuthContext";

export const metadata: Metadata = {
  metadataBase: new URL("https://ziwei-frontend.onrender.com"),
  title: "紫微星盤 · AI 命理解析",
  description: "以 AI Multi-Agent 技術推算紫微斗數，探索命盤星象的深層意涵",
  icons: { icon: "/icon-removebg-preview.png" },
  alternates: { canonical: "/" },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="zh-TW" suppressHydrationWarning>
      <body className="font-sans antialiased">
        <AuthProvider>{children}</AuthProvider>
      </body>
    </html>
  );
}
