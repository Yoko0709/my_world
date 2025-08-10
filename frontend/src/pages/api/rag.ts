// src/pages/api/rag.ts
import type { APIRoute } from 'astro';

export const prerender = false; // 需要运行时

export const POST: APIRoute = async ({ request }) => {
  try {
    const { question } = await request.json();
    if (!question || typeof question !== 'string') {
      return new Response(JSON.stringify({ error: 'question 必须是字符串' }), { status: 400 });
    }

    const base = import.meta.env.RAG_API_BASE;
    if (!base) {
      return new Response(JSON.stringify({ error: '后端地址未配置（RAG_API_BASE）' }), { status: 500 });
    }

    // 转发到你的 Flask: POST /ask  {question: "..."}
    const resp = await fetch(`${base.replace(/\/$/, '')}/ask`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question }),
    });

    // 直接把 Flask 的 JSON 回给前端
    const data = await resp.json().catch(() => ({}));
    if (!resp.ok) {
      return new Response(JSON.stringify({ error: data?.error || 'RAG 服务错误' }), { status: 502 });
    }

    // 期望返回形如 { answer: "..." }
    return new Response(JSON.stringify(data), {
      status: 200,
      headers: { 'Content-Type': 'application/json' },
    });
  } catch (e: any) {
    return new Response(JSON.stringify({ error: e?.message || '未知错误' }), { status: 500 });
  }
};
