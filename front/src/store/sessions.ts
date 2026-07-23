export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
}

export interface ChatSession {
  id: string;
  title: string;
  messages: ChatMessage[];
  model: string;
  createdAt: number;
  updatedAt: number;
}

const KEY = "chat_sessions";
const MAX = 100;

export function getSessions(): ChatSession[] {
  try {
    return JSON.parse(localStorage.getItem(KEY) ?? "[]");
  } catch {
    return [];
  }
}

export function saveSession(session: ChatSession): void {
  const all = getSessions();
  const idx = all.findIndex((s) => s.id === session.id);
  if (idx >= 0) {
    all[idx] = session;
  } else {
    all.unshift(session);
  }
  localStorage.setItem(KEY, JSON.stringify(all.slice(0, MAX)));
}

export function deleteSession(id: string): void {
  localStorage.setItem(KEY, JSON.stringify(getSessions().filter((s) => s.id !== id)));
}

export function newSessionId(): string {
  return Date.now().toString(36) + Math.random().toString(36).slice(2, 7);
}

export function makeTitle(firstUserMessage: string): string {
  return firstUserMessage.trim().slice(0, 40) || "새 대화";
}
