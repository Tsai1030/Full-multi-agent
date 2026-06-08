"use client";
import { useCallback, useEffect, useRef, useState } from "react";
import { useParams } from "next/navigation";
import Image from "next/image";
import Link from "next/link";
import { motion } from "framer-motion";
import { chatApi, profileApi, ApiError } from "@/lib/api";
import { mdToHtml } from "@/lib/markdown";
import UpgradePrompt from "@/components/UpgradePrompt";
import { useAuth } from "@/contexts/AuthContext";
import type { ApiErrorDetail, ChartProfile, ChatMessage } from "@/types";

export default function MasterChatPage() {
  const params = useParams();
  const profileId = String(params.profileId);

  const [profile, setProfile] = useState<ChartProfile | null>(null);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(true);
  const [sending, setSending] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [upgradeError, setUpgradeError] = useState<ApiErrorDetail | null>(null);
  const { refreshSubscription } = useAuth();

  const scrollRef = useRef<HTMLDivElement>(null);
  const stickRef = useRef(true);

  const handleScroll = useCallback(() => {
    const el = scrollRef.current;
    if (!el) return;
    stickRef.current = el.scrollHeight - el.scrollTop - el.clientHeight < 80;
  }, []);

  // 直接設定 scrollTop（不可用 scrollIntoView，會造成整頁抖動）；只在貼底時跟隨
  useEffect(() => {
    const el = scrollRef.current;
    if (el && stickRef.current) el.scrollTop = el.scrollHeight;
  }, [messages]);

  useEffect(() => {
    let active = true;
    (async () => {
      setLoading(true);
      setError(null);
      setMessages([]);
      try {
        const p = await profileApi.get(profileId);
        if (!active) return;
        setProfile(p);

        const sessions = await chatApi.listSessions(profileId);
        const session = sessions[0] ?? (await chatApi.createSession(profileId));
        if (!active) return;
        setSessionId(session.id);

        const msgs = await chatApi.messages(session.id);
        if (active) setMessages(msgs);
      } catch (e) {
        if (active) setError(e instanceof ApiError ? e.message : "載入失敗，請稍後再試");
      } finally {
        if (active) setLoading(false);
      }
    })();
    return () => {
      active = false;
    };
  }, [profileId]);

  const handleSend = useCallback(async () => {
    const content = input.trim();
    if (!content || !sessionId || sending) return;

    setInput("");
    setError(null);
    setSending(true);
    stickRef.current = true;

    const now = Date.now();
    const userId = `tmp-u-${now}`;
    const masterId = `tmp-m-${now}`;
    setMessages((m) => [
      ...m,
      { id: userId, role: "user", content, created_at: new Date().toISOString() },
      { id: masterId, role: "master", content: "", created_at: new Date().toISOString() },
    ]);

    try {
      const done = await chatApi.stream(sessionId, content, (delta) => {
        setMessages((m) =>
          m.map((msg) => (msg.id === masterId ? { ...msg, content: msg.content + delta } : msg)),
        );
      });
      setMessages((m) =>
        m.map((msg) =>
          msg.id === masterId ? { ...msg, id: done.id, created_at: done.created_at } : msg,
        ),
      );
    } catch (e) {
      if (e instanceof ApiError && e.isInsufficientTokens) {
        setUpgradeError(e.detail);
      } else {
        setError(e instanceof ApiError ? e.message : "大師暫時無法回應，請稍後再試");
      }
      setMessages((m) => m.filter((msg) => msg.id !== masterId));
    } finally {
      setSending(false);
    }
  }, [input, sessionId, sending]);

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="h-full flex flex-col">
      <UpgradePrompt
        open={!!upgradeError}
        onClose={() => setUpgradeError(null)}
        error={upgradeError}
      />
      {/* 頂部 bar（滿版） */}
      <header className="shrink-0 border-b border-gold-800/30 bg-cosmos-950/40 backdrop-blur-sm px-4 md:px-6 pt-16 md:pt-4 pb-3">
        <div className="max-w-3xl mx-auto flex items-center justify-between gap-3">
          <div className="min-w-0">
            <h1 className="font-serif text-lg sm:text-xl font-bold text-parchment leading-tight">
              <span className="text-mystic-300">玄機子</span> · 與大師對談
            </h1>
            {profile && (
              <p className="text-xs text-parchment-muted truncate mt-0.5">
                正在解讀：<span className="text-gold-300">{profile.label}</span>
                <span className="text-parchment-muted/70">
                  {" "}· {profile.gender} {profile.birth_year}/{profile.birth_month}/
                  {profile.birth_day} {profile.birth_hour}時
                </span>
              </p>
            )}
          </div>
          <Link
            href="/master"
            className="shrink-0 text-xs text-gold-400 hover:text-gold-300 border border-gold-700/40 hover:border-gold-500/60 rounded-full px-3 py-1.5 transition-colors"
          >
            換命盤
          </Link>
        </div>
      </header>

      {/* 訊息區（滿版捲動，內容置中可讀） */}
      <div ref={scrollRef} onScroll={handleScroll} className="flex-1 min-h-0 overflow-y-auto">
        <div className="max-w-3xl mx-auto px-4 md:px-6 py-6 min-h-full flex flex-col">
          {loading ? (
            <div className="flex-1 flex items-center justify-center text-parchment-muted text-sm">
              <span className="w-5 h-5 border-2 border-gold-500 border-t-transparent rounded-full animate-spin mr-2" />
              正在請大師入座…
            </div>
          ) : error && messages.length === 0 ? (
            <div className="flex-1 flex flex-col items-center justify-center gap-3 text-center">
              <p className="text-red-400 text-sm">{error}</p>
              <Link href="/profiles" className="text-gold-400 text-sm hover:text-gold-300">
                返回我的命盤
              </Link>
            </div>
          ) : messages.length === 0 ? (
            <div className="flex-1 flex flex-col items-center justify-center gap-3 text-center px-4">
              <div className="relative w-16 h-16 opacity-90">
                <Image src="/wizard_icon/crystal-ball.png" alt="" fill className="object-contain" />
              </div>
              <p className="text-parchment font-serif text-lg">大師已備好你的命盤</p>
              <p className="text-parchment-muted text-sm max-w-sm">
                問問感情、事業、財運，或任何想請教的人生課題吧。
              </p>
            </div>
          ) : (
            <div className="flex flex-col gap-4">
              {messages.map((m) => (
                <MessageBubble key={m.id} message={m} />
              ))}
            </div>
          )}
        </div>
      </div>

      {error && messages.length > 0 && (
        <p className="text-red-400 text-xs sm:text-sm text-center py-1 shrink-0">{error}</p>
      )}

      {/* 輸入列（滿版 bar） */}
      <div className="shrink-0 border-t border-gold-800/30 bg-cosmos-950/40 backdrop-blur-sm px-4 md:px-6 py-3">
        <div className="max-w-3xl mx-auto flex items-end gap-2">
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="向大師提問…（Enter 送出，Shift+Enter 換行）"
            rows={1}
            disabled={loading || !sessionId}
            className="input-mystic flex-1 rounded-2xl px-4 py-3 text-sm resize-none max-h-40"
          />
          <button
            onClick={handleSend}
            disabled={sending || loading || !input.trim() || !sessionId}
            className="btn-gold text-cosmos-950 rounded-2xl px-5 py-3 text-sm font-semibold disabled:opacity-40 disabled:cursor-not-allowed h-[48px] flex items-center justify-center min-w-[64px]"
          >
            {sending ? (
              <span className="w-4 h-4 border-2 border-cosmos-950 border-t-transparent rounded-full animate-spin" />
            ) : (
              "送出"
            )}
          </button>
        </div>
      </div>
    </div>
  );
}

function MessageBubble({ message }: { message: ChatMessage }) {
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
        {!isUser && <span className="block text-xs text-mystic-300 mb-1">玄機子</span>}
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
