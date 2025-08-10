import React, { useState } from 'react';

export default function RagChat() {
  const [input, setInput] = useState('');
  const [history, setHistory] = useState<{ role: 'user' | 'assistant'; content: string }[]>([]);
  const [loading, setLoading] = useState(false);

  async function send() {
    const q = input.trim();
    if (!q) return;
    setInput('');
    setHistory(h => [...h, { role: 'user', content: q }]);
    setLoading(true);

    try {
      const r = await fetch('/api/rag', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question: q }),
      });
      const data = await r.json();
      if (!r.ok) throw new Error(data?.error || '请求失败');
      setHistory(h => [...h, { role: 'assistant', content: data?.answer ?? '(空响应)' }]);
    } catch (err: any) {
      setHistory(h => [...h, { role: 'assistant', content: `错误：${err?.message || err}` }]);
    } finally {
      setLoading(false);
    }
  }

  function onKeyDown(e: React.KeyboardEvent<HTMLTextAreaElement>) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      send();
    }
  }

  return (
    <div className="max-w-3xl mx-auto p-4 space-y-4">
      <h1 className="text-2xl font-semibold">RAG Chat</h1>

      <div className="border rounded-2xl p-3 h-[60vh] overflow-y-auto space-y-3 bg-white/70">
        {history.map((m, i) => (
          <div key={i} className={`rounded-xl p-3 ${m.role === 'user' ? 'bg-gray-100' : 'bg-gray-50'}`}>
            <div className="text-xs mb-1 text-gray-500">{m.role === 'user' ? '你' : '助手'}</div>
            <div className="whitespace-pre-wrap leading-relaxed">{m.content}</div>
          </div>
        ))}
        {loading && <div className="text-sm text-gray-500">思考中…</div>}
      </div>

      <div className="space-y-2">
        <textarea
          className="w-full border rounded-xl p-3 focus:outline-none"
          rows={3}
          placeholder="输入问题，Enter 发送（Shift+Enter 换行）"
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={onKeyDown}
        />
        <div className="flex gap-2">
          <button
            onClick={send}
            disabled={loading || !input.trim()}
            className="px-4 py-2 rounded-xl border shadow-sm disabled:opacity-50"
          >
            发送
          </button>
          <button onClick={() => setHistory([])} className="px-4 py-2 rounded-xl border">清空</button>
        </div>
      </div>
    </div>
  );
}
