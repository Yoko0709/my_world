import React, { useEffect, useRef, useState } from "react";
import "./RagInlineLite.css";

type Source = { title: string; url?: string };
type Msg = {
  id: string;
  role: "user" | "assistant";
  content: string;
  sources?: Source[];
};

export default function RagInlineLite() {
  const [msgs, setMsgs] = useState<Msg[]>([]);
  const [text, setText] = useState("");
  const [loading, setLoading] = useState(false);
  const endRef = useRef<HTMLDivElement>(null);

  // 新消息出现时滚动到底部
  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [msgs.length, loading]);

  async function send() {
    const q = text.trim();
    if (!q) return;
    setText("");
    setMsgs(m => [...m, { id: crypto.randomUUID(), role: "user", content: q }]);
    setLoading(true);

    try {
      const r = await fetch("/api/rag", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: q }),
      });
      const data = await r.json().catch(() => ({}));
      const answer = r.ok ? (data?.answer ?? "(空响应)") : `错误：${data?.error || r.status}`;

      setMsgs(m => [
        ...m,
        {
          id: crypto.randomUUID(),
          role: "assistant",
          content: answer,
          sources: Array.isArray(data?.sources) ? data.sources : undefined,
        },
      ]);
    } catch (e: any) {
      setMsgs(m => [
        ...m,
        { id: crypto.randomUUID(), role: "assistant", content: `网络错误：${e?.message || e}` },
      ]);
    } finally {
      setLoading(false);
    }
  }

  function onKeyDown(e: React.KeyboardEvent<HTMLTextAreaElement>) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      send();
    }
  }

  return (
    <div className="rag-wrap">
      <div className="rag-header">Ask my notes</div>

      <div className="rag-box" aria-live="polite">
        {msgs.map(m => <MessageItem key={m.id} msg={m} />)}
        {loading && <div className="rag-typing">…thinking</div>}
        <div ref={endRef} />
      </div>

      <div className="rag-input">
        <textarea
          rows={2}
          placeholder="问我：此站/文档里有什么？（Enter 发送，Shift+Enter 换行）"
          value={text}
          onChange={e => setText(e.target.value)}
          onKeyDown={onKeyDown}
        />
        <button className="rag-send-btn" onClick={send} disabled={loading || !text.trim()}>
          发送
        </button>
      </div>
    </div>
  );
}

function MessageItem({ msg }: { msg: Msg }) {
  const isUser = msg.role === "user";
  const [showAll, setShowAll] = useState(false);
  const sources = msg.sources || [];
  const displayed = showAll ? sources : sources.slice(0, 3);

  return (
    <div className={`rag-row ${isUser ? "rag-user" : "rag-assistant"}`}>
      <div className="rag-bubble">
        <div className="rag-text">{msg.content}</div>

        {sources.length > 0 && (
          <div className="rag-sources">
            <div className="rag-sources-title">参考来源</div>
            <div className="rag-chips">
              {displayed.map((s, i) => (
                <a
                  key={i}
                  className="rag-chip"
                  href={s.url || "#"}
                  target={s.url ? "_blank" : undefined}
                  rel="noreferrer"
                  title={s.title}
                >
                  {s.title}
                </a>
              ))}
              {sources.length > 3 && !showAll && (
                <button className="rag-chip rag-more" onClick={() => setShowAll(true)}>
                  +{sources.length - 3}
                </button>
              )}
              {sources.length > 3 && showAll && (
                <button className="rag-chip rag-more" onClick={() => setShowAll(false)}>
                  收起
                </button>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
