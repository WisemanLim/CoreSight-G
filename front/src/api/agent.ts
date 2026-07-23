export interface SseEvent {
  event: string;
  data: string;
}

export async function* streamChat(
  message: string,
  history: { role: string; content: string }[],
  model?: string,
): AsyncGenerator<SseEvent> {
  const token = localStorage.getItem("token");
  const resp = await fetch("/api/agent/chat/stream", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
    body: JSON.stringify({ message, history, model }),
  });

  if (!resp.ok) {
    throw new Error(`HTTP ${resp.status}`);
  }

  const reader = resp.body!.getReader();
  const decoder = new TextDecoder();
  let buf = "";

  while (true) {
    const { value, done } = await reader.read();
    if (done) break;
    buf += decoder.decode(value, { stream: true });

    // SSE blocks separated by double newline
    const blocks = buf.split("\n\n");
    buf = blocks.pop() ?? "";

    for (const block of blocks) {
      if (!block.trim()) continue;
      let eventType = "message";
      let dataStr = "";

      for (const line of block.split("\n")) {
        if (line.startsWith("event: ")) {
          eventType = line.slice(7).trim();
        } else if (line.startsWith("data: ")) {
          dataStr = line.slice(6);
        }
      }

      if (!dataStr) continue;

      try {
        const parsed = JSON.parse(dataStr);
        // backend sends {"text": "..."} for delta, extract the text
        const data = parsed.text ?? parsed.message ?? parsed.data ?? JSON.stringify(parsed);
        yield { event: eventType, data: String(data) };
      } catch {
        yield { event: eventType, data: dataStr };
      }
    }
  }
}
