"use client";
import { useCallback, useEffect, useRef, useState } from "react";
import { motion } from "framer-motion";
import { fortuneApi, ApiError } from "@/lib/api";
import { mdToHtml } from "@/lib/markdown";
import UpgradePrompt from "@/components/UpgradePrompt";
import { useAuth } from "@/contexts/AuthContext";
import type { ApiErrorDetail } from "@/types";

interface FortuneChatProps {
  domain: string;
  analysisContext: string;
  chartText: string;
  personaLabel: string;
  placeholder?: string;
}

interface Message {
  id: string;
  role: "user" | "advisor";
  content: string;
}

export default function FortuneChat({
  domain,
  analysisContext,
  chartText,
  personaLabel,
  placeholder = "針對分析結果追問…",
}: FortuneChatProps) {
  const { refreshSubscription } = useAuth();
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [sending, setSending] = useState(false);
  const [upgradeError, setUpgradeError] = useState<ApiErrorDetail | null>(null);
  const scrollRef = useRef<HTMLDivElement>(null);
  const stickRef = useRef(true);

  const handleScroll = useCallback(() => {
    const el = scrollRef.current;
    if (!el) return;
    stickRef.current = el.scrollHeight - el.scrollTop - el.clientHeight < 80;
  }, []);

  useEffect(() => {
    const el = scrollRef.current;
    if (el && stickRef.current) el.scrollTop = el.scrollHeight;
  }, [messages]);

  const handleSend = useCallback(async () => {
    const content = input.trim();
    if (!content || sending) return;

    setInput("");
    setSending(true);
    stickRef.current = true;

    const userId = `u-${Date.now()}`;
    const advisorId = `a-${Date.now()}`;
    setMessages((m) => [
      ...m,
      { id: userId, role: "user", content },
      { id: advisorId, role: "advisor", content: "" },
    ]);

    const history = messages.map((m) => ({
      role: m.role === "user" ? "user" : "assistant",
      content: m.content,
    }));

    try {
      await fortuneApi.stream(
        {
          domain,
          analysis_context: analysisContext,
          chart_text: chartText,
          messages: history,
          user_message: content,
        },
        (delta) => {
          setMessages((m) =>
            m.map((msg) =>
              msg.id === advisorId ? { ...msg, content: msg.content + delta } : msg,
            ),
          );
        },
      );
      await refreshSubscription();
    } catch (e) {
      if (e instanceof ApiError && e.isInsufficientTokens) {
        setUpgradeError(e.detail);
        setMessages((m) => m.filter((msg) => msg.id !== advisorId));
      } else {
        setMessages((m) =>
          m.map((msg) =>
            msg.id === advisorId
              ? { ...msg, content: msg.content || "（暫時無法回應，請稍後再試）" }
              : msg,
          ),
        );
      }
    } finally {
      setSending(false);
    }
  }, [input, sending, messages, domain, analysisContext, chartText, refreshSubscription]);

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="flex flex-col h-full">
      <UpgradePrompt
        open={!!upgradeError}
        onClose={() => setUpgradeError(null)}
        error={upgradeError}
      />

      <div
        ref={scrollRef}
        onScroll={handleScroll}
        className="flex-1 min-h-0 overflow-y-auto px-4 py-4"
      >
        {messages.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full gap-3 text-center px-4">
            <span className="text-3xl text-gold-500">✦</span>
            <p className="text-parchment font-serif">有任何想追問的嗎？</p>
            <p className="text-parchment-muted text-sm max-w-sm">
              針對上方的分析結果，你可以進一步追問細節或詢問建議。
            </p>
          </div>
        ) : (
          <div className="flex flex-col gap-3">
            {messages.map((m) => (
              <MessageBubble key={m.id} message={m} personaLabel={personaLabel} />
            ))}
          </div>
        )}
      </div>

      <div className="shrink-0 border-t border-gold-800/30 bg-cosmos-950/40 backdrop-blur-sm px-4 py-3">
        <div className="flex items-end gap-2">
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder={placeholder}
            rows={1}
            disabled={sending}
            className="input-mystic flex-1 rounded-2xl px-4 py-3 text-sm resize-none max-h-40"
          />
          <button
            onClick={handleSend}
            disabled={sending || !input.trim()}
            className="btn-gold text-cosmos-950 rounded-2xl px-5 py-3 text-sm font-semibold disabled:opacity-40 disabled:cursor-not-allowed h-[48px] flex items-center justify-center min-w-[64px]"
          >
            {sending ? (
              <span className="w-4 h-4 border-2 border-cosmos-950 border-t-transparent rounded-full animate-spin" />
            ) : (
              "追問"
            )}
          </button>
        </div>
        <p className="text-[10px] text-parchment-muted mt-1.5 text-center">
          每則追問消耗 1 星辰代幣 · 離開頁面後對話不會保存
        </p>
      </div>
    </div>
  );
}

function MessageBubble({ message, personaLabel }: { message: Message; personaLabel: string }) {
  const isUser = message.role === "user";
  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.25 }}
      className={`flex ${isUser ? "justify-end" : "justify-start"}`}
    >
      <div
        className={`max-w-[90%] sm:max-w-[80%] rounded-2xl px-4 py-3 text-sm leading-relaxed break-words ${
          isUser
            ? "bg-gold-500/15 border border-gold-600/40 text-parchment"
            : "bg-cosmos-800/70 border border-mystic-500/30 text-parchment-dim"
        }`}
      >
        {!isUser && <span className="block text-xs text-mystic-300 mb-1">{personaLabel}</span>}
        {!isUser && message.content === "" ? (
          <span className="flex gap-1 py-1">
            {[0, 1, 2].map((i) => (
              <span
                key={i}
                className="w-2 h-2 rounded-full bg-mystic-400/70 animate-bounce"
                style={{ animationDelay: `${i * 0.15}s` }}
              />
            ))}
          </span>
        ) : isUser ? (
          <span className="whitespace-pre-wrap">{message.content}</span>
        ) : (
          <div className="chat-md" dangerouslySetInnerHTML={{ __html: mdToHtml(message.content) }} />
        )}
      </div>
    </motion.div>
  );
}
