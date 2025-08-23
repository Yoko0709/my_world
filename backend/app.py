# backend/app.py
import os
from flask import Flask, request, jsonify

# NOTE: 现在从 backend/ai_agent/rag_pipeline1.py 导入
from ai_agent.rag_pipeline1 import (
    load_docs, create_index, load_index, get_qa_chain, get_answer
)

def create_app():
    app = Flask(__name__)

    # ---- 路径与配置（跨平台 + 可通过环境变量覆盖）----
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DOCS_DIR = os.environ.get("DOCS_DIR", os.path.join(BASE_DIR, "ai_agent", "docs"))
    INDEX_DIR = os.environ.get("INDEX_DIR", os.path.join(BASE_DIR, "ai_agent", "index"))

    # ---- 懒加载（避免启动阶段阻塞/失败）----
    app.qa_chain = None
    app.index_dir = INDEX_DIR
    app.docs_dir = DOCS_DIR

    def ensure_qa_chain():
        if app.qa_chain is not None:
            return app.qa_chain
        # 如果没有索引就创建，有就加载
        if not os.path.exists(app.index_dir):
            docs = load_docs(app.docs_dir)
            vectorstore = create_index(docs)  # create_index 内部请使用 app.index_dir
        else:
            vectorstore = load_index()
        app.qa_chain = get_qa_chain(vectorstore)
        return app.qa_chain

    @app.get("/health")
    def health():
        return {"ok": True}, 200

    @app.post("/ask")
    def ask():
        data = request.get_json(silent=True) or {}
        question = data.get("question", "")
        # 若还没建索引，第一次调用 /ask 时自动构建（可改成后台任务或预构建）
        qa_chain = ensure_qa_chain()
        if question:
            answer = get_answer(qa_chain, question)
            return jsonify({"answer": answer})
        # 没有 question 时，先把收到的原文回显
        return jsonify({"answer": f"你问了: {data}"}), 200

    # 可选：提供一个显式的索引重建端点（只在你自己内部用）
    @app.post("/rebuild-index")
    def rebuild_index():
        # 允许手动重建索引
        docs = load_docs(app.docs_dir)
        _ = create_index(docs)
        app.qa_chain = None  # 下次 ask 时会重新加载
        return {"ok": True, "message": "index rebuilt"}, 200

    return app

app = create_app()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
