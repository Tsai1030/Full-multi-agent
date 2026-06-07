"use client";
import { useCallback, useEffect, useRef, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import { motion, AnimatePresence } from "framer-motion";
import CosmicBackground from "@/components/CosmicBackground";
import Navbar from "@/components/Navbar";
import { useAuth } from "@/contexts/AuthContext";
import { chatApi, profileApi, ApiError } from "@/lib/api";
import type { ChartProfile, ChatMessage } from "@/types";

export default function MasterChatPage() {
  const params = useParams();
  const router = useRouter();
  const profileId = String(params.profileId);
  const { user, loading: authLoading } = useAuth();

  const [profile, setProfile] = useState<ChartProfile | null>(null);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(true);
  const [sending, setSending] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const bottomRef = useRef<HTMLDivElement>(null);

  // 未登入 → 導去登入
  useEffect(() => {
    if (!authLoading && !user) {
      router.replace(`/login?redirect=/master/${profileId}`);
    }
  }, [authLoading, user, profileId, router]);

  // 載入 profile + session + 訊息
  useEffect(() => {
    if (!user) return;
    let active = true;
    (async () => {
      setLoading(true);
      setError(null);
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
  }, [user, profileId]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, sending]);

  const handleSend = useCallback(async () => {
    const content = input.trim();
    if (!content || !sessionId || sending) return;

    setInput("");
    setError(null);
    setSending(true);
    const optimistic: ChatMessage = {
      id: `tmp-${Date.now()}`,
      role: "user",
      content,
      created_at: new Date().toISOString(),
    };
    setMessages((m) => [...m, optimistic]);

    try {
      const reply = await chatApi.send(sessionId, content);
      setMessages((m) => [...m, reply]);
    } catch (e) {
      setError(e instanceof ApiError ? e.message : "大師暫時無法回應，請稍後再試");
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

      <div className="relative z-10 min-h-screen flex flex-col items-center pt-24 pb-6 px-4">
        <div className="w-full max-w-2xl flex flex-col flex-1" style={{ minHeight: 0 }}>
          {/* Header */}
          <div className="text-center mb-4">
            <p className="text-xs tracking-[0.4em] text-gold-500 uppercase mb-1">玄機子 · 命理大師</p>
            <h1 className="font-serif text-2xl font-bold text-parchment">
              與大師對談
            </h1>
            {profile && (
              <p className="mt-1 text-xs text-parchment-muted">
                命盤：{profile.label} · {profile.gender} · {profile.birth_year}/{profile.birth_month}/{profile.birth_day} {profile.birth_hour}時
              </p>
            )}
            <div className="divider-gold w-24 mx-auto mt-3" />
          </div>

          {/* Messages */}
          <div className="flex-1 overflow-y-auto card-gold rounded-3xl p-5 mb-4" style={{ minHeight: "50vh" }}>
            {loading ? (
              <div className="h-full flex items-center justify-center text-parchment-muted text-sm">
                <span className="w-5 h-5 border-2 border-gold-500 border-t-transparent rounded-full animate-spin mr-2" />
                正在請大師入座…
              </div>
            ) : error && messages.length === 0 ? (
              <div className="h-full flex flex-col items-center justify-center gap-3 text-center">
                <p className="text-red-400 text-sm">{error}</p>
                <Link href="/profiles" className="text-gold-400 text-sm hover:text-gold-300">
                  返回我的命盤
                </Link>
              </div>
            ) : messages.length === 0 ? (
              <div className="h-full flex flex-col items-center justify-center gap-2 text-center px-6">
                <span className="text-4xl mb-1">🔮</span>
                <p className="text-parchment font-serif">大師已備好你的命盤</p>
                <p className="text-parchment-muted text-sm">
                  問問感情、事業、財運，或任何想請教的人生課題吧。
                </p>
              </div>
            ) : (
              <div className="flex flex-col gap-4">
                {messages.map((m) => (
                  <MessageBubble key={m.id} message={m} />
                ))}
                {sending && <TypingBubble />}
                <div ref={bottomRef} />
              </div>
            )}
          </div>

          {/* Inline error (when messages exist) */}
          {error && messages.length > 0 && (
            <p className="text-red-400 text-sm text-center mb-2">{error}</p>
          )}

          {/* Composer */}
          <div className="flex items-end gap-2">
            <textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="向大師提問…（Enter 送出，Shift+Enter 換行）"
              rows={2}
              disabled={loading || !sessionId}
              className="input-mystic flex-1 rounded-2xl px-4 py-3 text-sm resize-none"
            />
            <button
              onClick={handleSend}
              disabled={sending || loading || !input.trim() || !sessionId}
              className="btn-gold text-cosmos-950 rounded-2xl px-5 py-3 text-sm font-semibold disabled:opacity-40 disabled:cursor-not-allowed h-[52px] flex items-center gap-2"
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
    </main>
  );
}

function MessageBubble({ message }: { message: ChatMessage }) {
  const isUser = message.role === "user";
  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      className={`flex ${isUser ? "justify-end" : "justify-start"}`}
    >
      <div
        className={`max-w-[80%] rounded-2xl px-4 py-3 text-sm leading-relaxed whitespace-pre-wrap ${
          isUser
            ? "bg-gold-500/15 border border-gold-600/40 text-parchment"
            : "bg-cosmos-800/70 border border-mystic-500/30 text-parchment-dim"
        }`}
      >
        {!isUser && <span className="block text-xs text-mystic-300 mb-1">玄機子</span>}
        {message.content}
      </div>
    </motion.div>
  );
}

function TypingBubble() {
  return (
    <div className="flex justify-start">
      <div className="bg-cosmos-800/70 border border-mystic-500/30 rounded-2xl px-4 py-3">
        <span className="block text-xs text-mystic-300 mb-1">玄機子</span>
        <span className="flex gap-1">
          {[0, 1, 2].map((i) => (
            <span
              key={i}
              className="w-2 h-2 rounded-full bg-mystic-400/70 animate-bounce"
              style={{ animationDelay: `${i * 0.15}s` }}
            />
          ))}
        </span>
      </div>
    </div>
  );
}
