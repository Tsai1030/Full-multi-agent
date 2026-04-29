"use client";
import { useEffect, useRef } from "react";
import Image from "next/image";
import { motion } from "framer-motion";
import Button from "@/components/ui/Button";
import type { AnalysisResponse } from "@/types";

interface ResultDisplayProps {
  result: AnalysisResponse;
  onReset: () => void;
}

function formatResult(text: string): string {
  return text
    .replace(/^## (.+)$/gm, '<h2>$1</h2>')
    .replace(/^### (.+)$/gm, '<h3>$1</h3>')
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    .replace(/^- (.+)$/gm, '<li>$1</li>')
    .replace(/(<li>.*<\/li>\n?)+/g, (m) => `<ul>${m}</ul>`)
    .replace(/\n{2,}/g, '</p><p>')
    .replace(/^(?!<[hup])(.+)$/gm, (m) => m.trim() ? `<p>${m}</p>` : '')
    .replace(/<p><\/p>/g, '');
}

const container = {
  hidden: {},
  show: { transition: { staggerChildren: 0.12 } },
};
const item = {
  hidden: { opacity: 0, y: 20 },
  show:   { opacity: 1, y: 0, transition: { duration: 0.6, ease: [0.22, 1, 0.36, 1] } },
};

export default function ResultDisplay({ result, onReset }: ResultDisplayProps) {
  const contentRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    contentRef.current?.scrollIntoView({ block: "start", behavior: "smooth" });
  }, []);

  const html = formatResult(result.result || "（無結果）");
  const elapsed = result.metadata?.elapsed_ms
    ? `${(result.metadata.elapsed_ms / 1000).toFixed(1)}s`
    : null;

  return (
    <motion.div
      variants={container}
      initial="hidden"
      animate="show"
      ref={contentRef}
      className="w-full max-w-2xl mx-auto"
    >
      {/* Header card */}
      <motion.div variants={item} className="card-gold rounded-3xl p-8 mb-6 text-center">
        <div className="flex justify-center mb-4">
          <div
            className="relative w-16 h-16"
            style={{ filter: "drop-shadow(0 0 16px rgba(201,168,76,0.6))" }}
          >
            <Image src="/icon-removebg-preview.png" alt="" fill className="object-contain" />
          </div>
        </div>
        <p className="text-xs tracking-[0.4em] text-gold-500 uppercase mb-2">命盤解析完成</p>
        <h2 className="font-serif text-2xl font-bold text-parchment">
          星象已顯
        </h2>
        {elapsed && (
          <p className="mt-2 text-xs text-parchment-muted">
            推算耗時 {elapsed} · AI Multi-Agent
          </p>
        )}
        <div className="divider-gold w-24 mx-auto mt-4" />
      </motion.div>

      {/* Result content card */}
      <motion.div variants={item} className="card-gold rounded-3xl p-8 mb-6">
        <div
          ref={contentRef}
          className="result-content"
          dangerouslySetInnerHTML={{ __html: html }}
        />
      </motion.div>

      {/* Metadata badge */}
      {result.metadata && (
        <motion.div variants={item} className="flex gap-3 justify-center mb-8">
          {[
            { label: "分析領域", value: result.metadata.domain_type },
            { label: "推理迭代", value: `${result.metadata.iterations} 次` },
          ].map((m) => (
            <div
              key={m.label}
              className="px-4 py-2 rounded-full border border-gold-800/40 bg-cosmos-800/50
                text-xs text-parchment-muted flex items-center gap-2"
            >
              <span className="text-gold-600">{m.label}</span>
              <span className="text-parchment">{m.value}</span>
            </div>
          ))}
        </motion.div>
      )}

      {/* Actions */}
      <motion.div variants={item} className="flex flex-col sm:flex-row gap-4 justify-center pb-16">
        <Button variant="gold" size="md" onClick={onReset}>
          ✦ 再次推算
        </Button>
        <Button
          variant="ghost"
          size="md"
          onClick={() => {
            const text = result.result || "";
            navigator.clipboard.writeText(text).catch(() => {});
          }}
        >
          複製結果
        </Button>
      </motion.div>
    </motion.div>
  );
}
