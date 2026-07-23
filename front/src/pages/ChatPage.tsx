import { useCallback, useEffect, useRef, useState } from "react";
import { useNavigate } from "react-router";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { streamChat } from "../api/agent";
import { clearAuth } from "../store/auth";
import { useLocale } from "../hooks/useLocale";
import {
  type ChatMessage,
  type ChatSession,
  deleteSession,
  getSessions,
  makeTitle,
  newSessionId,
  saveSession,
} from "../store/sessions";

interface Message extends ChatMessage {
  streaming?: boolean;
}

const MODEL_OPTIONS = [
  { value: "ollama", label: "🏠 Ollama (Local)" },
  { value: "claude-sonnet-4-6", label: "Claude Sonnet 4.6" },
  { value: "claude-haiku-4-5-20251001", label: "Claude Haiku 4.5" },
  { value: "gpt-4o", label: "GPT-4o" },
  { value: "gemini-1.5-flash", label: "Gemini 1.5 Flash" },
];

function formatDate(ts: number, locale: string): string {
  const d = new Date(ts);
  const now = new Date();
  const diffDays = Math.floor((now.getTime() - d.getTime()) / 86400000);
  if (diffDays === 0) return d.toLocaleTimeString(locale, { hour: "2-digit", minute: "2-digit" });
  if (diffDays === 1) return locale.startsWith("ko") ? "어제" : "Yesterday";
  if (diffDays < 7) return locale.startsWith("ko") ? `${diffDays}일 전` : `${diffDays}d ago`;
  return d.toLocaleDateString(locale, { month: "short", day: "numeric" });
}

export default function ChatPage() {
  const navigate = useNavigate();
  const { t, locale } = useLocale();
  const [sessions, setSessions] = useState<ChatSession[]>(() => getSessions());
  const [activeId, setActiveId] = useState<string>(() => {
    const all = getSessions();
    return all[0]?.id ?? newSessionId();
  });
  const [messages, setMessages] = useState<Message[]>(() => {
    const all = getSessions();
    return (all[0]?.messages ?? []) as Message[];
  });
  const [model, setModel] = useState<string>(() => {
    const all = getSessions();
    return all[0]?.model ?? "ollama";
  });
  const [input, setInput] = useState("");
  const [busy, setBusy] = useState(false);
  const [showSessions, setShowSessions] = useState(true);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const loadSession = useCallback((id: string) => {
    const all = getSessions();
    const s = all.find((s) => s.id === id);
    if (s) {
      setActiveId(s.id);
      setMessages(s.messages as Message[]);
      setModel(s.model);
    } else {
      setActiveId(id);
      setMessages([]);
    }
    setInput("");
  }, []);

  function createNewSession() {
    const id = newSessionId();
    setActiveId(id);
    setMessages([]);
    setModel("ollama");
    setInput("");
  }

  function handleDeleteSession(id: string, e: React.MouseEvent) {
    e.stopPropagation();
    deleteSession(id);
    const remaining = getSessions();
    setSessions(remaining);
    if (id === activeId) {
      if (remaining.length > 0) {
        loadSession(remaining[0].id);
      } else {
        createNewSession();
      }
    }
  }

  async function handleSend(e: React.FormEvent) {
    e.preventDefault();
    const text = input.trim();
    if (!text || busy) return;

    const history = messages.map((m) => ({ role: m.role, content: m.content }));
    const userMsg: Message = { role: "user", content: text };
    const assistantMsg: Message = { role: "assistant", content: "", streaming: true };

    setMessages((prev) => [...prev, userMsg, assistantMsg]);
    setInput("");
    setBusy(true);

    const assistantIdx = messages.length + 1;

    try {
      for await (const evt of streamChat(text, history, model)) {
        if (evt.event === "delta") {
          setMessages((prev) =>
            prev.map((m, i) =>
              i === assistantIdx ? { ...m, content: m.content + evt.data } : m
            )
          );
        } else if (evt.event === "error") {
          setMessages((prev) =>
            prev.map((m, i) =>
              i === assistantIdx
                ? { ...m, content: `⚠️ ${t("chat.error")}: ${evt.data}`, streaming: false }
                : m
            )
          );
        }
      }
    } catch (err: unknown) {
      const status = (err as { message?: string }).message;
      if (status?.includes("401")) {
        clearAuth();
        navigate("/login", { replace: true });
        return;
      }
      setMessages((prev) =>
        prev.map((m, i) =>
          i === assistantIdx
            ? { ...m, content: t("chat.errorGeneral"), streaming: false }
            : m
        )
      );
    } finally {
      setMessages((prev) => {
        const updated = prev.map((m, i) =>
          i === assistantIdx ? { ...m, streaming: false } : m
        );
        const cleanMsgs: ChatMessage[] = updated.map(({ role, content }) => ({ role, content }));
        const isNew = !getSessions().find((s) => s.id === activeId);
        const title = isNew ? makeTitle(text) : (getSessions().find((s) => s.id === activeId)?.title ?? makeTitle(text));
        const session: ChatSession = {
          id: activeId,
          title,
          messages: cleanMsgs,
          model,
          createdAt: getSessions().find((s) => s.id === activeId)?.createdAt ?? Date.now(),
          updatedAt: Date.now(),
        };
        saveSession(session);
        setSessions(getSessions());
        return updated;
      });
      setBusy(false);
    }
  }

  return (
    <div className="flex h-full bg-white dark:bg-gray-950">
      {/* Session sidebar */}
      {showSessions && (
        <div className="w-56 shrink-0 flex flex-col border-r border-gray-200 dark:border-gray-800 bg-gray-50 dark:bg-gray-900">
          <div className="p-3 border-b border-gray-200 dark:border-gray-800 flex items-center gap-2">
            <button
              onClick={createNewSession}
              className="flex-1 flex items-center gap-1.5 text-xs font-medium text-gray-600 dark:text-gray-300 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg px-3 py-1.5 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
            >
              <span className="text-base leading-none">+</span> {t("chat.newSession")}
            </button>
            <button
              onClick={() => setShowSessions(false)}
              className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 transition-colors p-1"
              title={t("chat.hideSidebar")}
            >
              ‹
            </button>
          </div>

          <div className="flex-1 overflow-y-auto py-2">
            {sessions.length === 0 && (
              <p className="text-xs text-gray-400 dark:text-gray-600 text-center mt-4">
                {t("chat.noSessions")}
              </p>
            )}
            {sessions.map((s) => (
              <div
                key={s.id}
                onClick={() => loadSession(s.id)}
                className={`group mx-2 mb-0.5 px-3 py-2 rounded-lg cursor-pointer flex items-start justify-between gap-1 transition-colors ${
                  s.id === activeId
                    ? "bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800"
                    : "hover:bg-gray-100 dark:hover:bg-gray-800"
                }`}
              >
                <div className="min-w-0 flex-1">
                  <p className="text-[12px] font-medium text-gray-700 dark:text-gray-300 truncate">
                    {s.title}
                  </p>
                  <p className="text-[10px] text-gray-400 dark:text-gray-600 mt-0.5">
                    {formatDate(s.updatedAt, locale)}
                  </p>
                </div>
                <button
                  onClick={(e) => handleDeleteSession(s.id, e)}
                  className="opacity-0 group-hover:opacity-100 text-gray-400 hover:text-red-400 transition-all text-xs shrink-0 mt-0.5"
                  title={t("chat.deleteSession")}
                >
                  ×
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Chat area */}
      <div className="flex flex-col flex-1 min-w-0">
        <div className="flex items-center justify-between px-4 py-2 border-b border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900 shrink-0">
          <div className="flex items-center gap-2">
            {!showSessions && (
              <button
                onClick={() => setShowSessions(true)}
                className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 transition-colors text-sm mr-1"
                title={t("chat.showSidebar")}
              >
                ›
              </button>
            )}
            <h1 className="text-sm font-semibold text-gray-700 dark:text-gray-300">AI Assistant</h1>
          </div>
          <div className="flex items-center gap-2">
            <select
              value={model}
              onChange={(e) => setModel(e.target.value)}
              className="text-xs border border-gray-200 dark:border-gray-700 rounded-lg px-2 py-1 bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              {MODEL_OPTIONS.map((opt) => (
                <option key={opt.value} value={opt.value}>
                  {opt.label}
                </option>
              ))}
            </select>
            <button
              onClick={createNewSession}
              className="text-xs text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 disabled:opacity-40 transition-colors"
            >
              {t("chat.addSession")}
            </button>
          </div>
        </div>

        <div className="flex-1 overflow-y-auto px-4 py-6 space-y-4 bg-white dark:bg-gray-950">
          {messages.length === 0 && (
            <div className="text-center mt-16 space-y-2">
              <p className="text-3xl">🤖</p>
              <p className="text-gray-400 dark:text-gray-500 text-sm">
                {t("chat.noMessages")}
              </p>
              <p className="text-gray-300 dark:text-gray-600 text-xs">
                {t("chat.currentModel")}: {MODEL_OPTIONS.find((o) => o.value === model)?.label}
              </p>
            </div>
          )}
          {messages.map((msg, i) => (
            <div
              key={i}
              className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}
            >
              {msg.role === "assistant" && (
                <div className="w-6 h-6 rounded-full bg-blue-600 flex items-center justify-center text-white text-[10px] font-bold shrink-0 mr-2 mt-1">
                  AI
                </div>
              )}
              <div
                className={`max-w-[75%] rounded-2xl px-4 py-3 text-sm ${
                  msg.role === "user"
                    ? "bg-blue-600 text-white"
                    : "bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 text-gray-800 dark:text-gray-200 shadow-sm"
                }`}
              >
                {msg.role === "assistant" ? (
                  <div className="prose prose-sm dark:prose-invert max-w-none">
                    <ReactMarkdown remarkPlugins={[remarkGfm]}>
                      {msg.content || (msg.streaming ? "" : t("chat.noResponse"))}
                    </ReactMarkdown>
                  </div>
                ) : (
                  <p className="whitespace-pre-wrap">{msg.content}</p>
                )}
                {msg.streaming && (
                  <span className="inline-block w-1.5 h-4 bg-current opacity-60 animate-pulse ml-0.5" />
                )}
              </div>
            </div>
          ))}
          <div ref={bottomRef} />
        </div>

        <form
          onSubmit={handleSend}
          className="bg-white dark:bg-gray-900 border-t border-gray-200 dark:border-gray-800 px-4 py-3 flex gap-2 shrink-0"
        >
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            disabled={busy}
            placeholder={t("chat.placeholder")}
            className="flex-1 border border-gray-200 dark:border-gray-700 rounded-xl px-4 py-2 text-sm bg-white dark:bg-gray-800 text-gray-800 dark:text-gray-200 placeholder-gray-400 dark:placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-50 dark:disabled:bg-gray-900"
            onKeyDown={(e) => {
              if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                handleSend(e as unknown as React.FormEvent);
              }
            }}
          />
          <button
            type="submit"
            disabled={busy || !input.trim()}
            className="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-200 dark:disabled:bg-gray-700 disabled:text-gray-400 text-white rounded-xl px-4 py-2 text-sm font-medium transition-colors"
          >
            {busy ? "…" : t("chat.send")}
          </button>
        </form>
      </div>
    </div>
  );
}
