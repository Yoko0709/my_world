# backend/ai_agent/rag_pipeline1.py
import os
from pathlib import Path
from typing import List, Optional, Tuple, Iterable
from dataclasses import dataclass

from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_community.vectorstores import FAISS
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from langchain.chains import RetrievalQA

# ----------------------------
# 配置项（也可转到 .env / settings.py）
# ----------------------------
CHUNK_SIZE = int(os.getenv("RAG_CHUNK_SIZE", "800"))
CHUNK_OVERLAP = int(os.getenv("RAG_CHUNK_OVERLAP", "120"))
TOP_K = int(os.getenv("RAG_TOP_K", "6"))
SEARCH_TYPE = os.getenv("RAG_SEARCH_TYPE", "similarity")  # or "mmr"

ALLOWED_SUFFIX = {".pdf", ".txt", ".md"}  # 需要可再扩展 .docx 等


@dataclass
class EmbConf:
    api_key: Optional[str]
    base_url: Optional[str]
    model: str


def _emb_conf() -> EmbConf:
    """
    嵌入与对话模型分离配置：
      OPENAI_EMBEDDINGS_KEY / BASE / MODEL
      未设置时回退到 OPENAI_API_KEY
    """
    api_key = os.getenv("OPENAI_EMBEDDINGS_KEY") or os.getenv("OPENAI_API_KEY")
    base = os.getenv("OPENAI_EMBEDDINGS_BASE") or os.getenv("OPENAI_API_BASE")
    model = os.getenv("OPENAI_EMBEDDINGS_MODEL", "text-embedding-3-small")
    return EmbConf(api_key=api_key, base_url=base, model=model)


def _emb():
    c = _emb_conf()
    # 统一新版参数名；若你项目 pin 在旧版，可将 api_key→openai_api_key, base_url→openai_api_base
    return OpenAIEmbeddings(model=c.model, api_key=c.api_key, base_url=c.base_url)


def _split_docs(docs: List[Document]) -> List[Document]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP, separators=[
            "\n\n", "\n", "。", "！", "？", "；", "，", " ", ""
        ]
    )
    return splitter.split_documents(docs)


def _load_one(path: Path) -> List[Document]:
    if path.suffix.lower() == ".pdf":
        return PyPDFLoader(str(path)).load()
    # 其它纯文本类
    return TextLoader(str(path), encoding="utf-8", errors="ignore").load()


def load_docs(doc_folder: str, recursive: bool = True) -> List[Document]:
    doc_dir = Path(doc_folder)
    if not doc_dir.exists():
        print(f"[load_docs] 文档目录不存在：{doc_dir}")
        return []
    paths: Iterable[Path] = doc_dir.rglob("*") if recursive else doc_dir.iterdir()
    raw_docs: List[Document] = []
    for p in paths:
        if p.is_file() and p.suffix.lower() in ALLOWED_SUFFIX:
            try:
                raw_docs.extend(_load_one(p))
            except Exception as e:
                print(f"[load_docs] 跳过 {p.name}：{e}")
    print(f"✅ 原始文档共 {len(raw_docs)} 条（文件粒度/页粒度）")
    docs = _split_docs(raw_docs)
    print(f"✅ 切块完成，共 {len(docs)} 条 chunk（chunk_size={CHUNK_SIZE}, overlap={CHUNK_OVERLAP}）")
    return docs


def _write_fingerprint(save_dir: Path, vs: FAISS):
    """
    写一个简易指纹，避免 embeddings 变更后误读。
    """
    fp = save_dir / "fingerprint.txt"
    dim = getattr(vs.index, "d", None)
    meta = {
        "emb_model": _emb_conf().model,
        "dim": dim,
        "chunks": len(getattr(vs, "index_to_docstore_id", {})),
    }
    fp.write_text("\n".join(f"{k}={v}" for k, v in meta.items()), encoding="utf-8")


def _check_fingerprint(save_dir: Path):
    fp = save_dir / "fingerprint.txt"
    if not fp.exists():
        print("[load_index] 未发现 fingerprint.txt，继续但请注意 Embedding 兼容性。")
        return
    data = dict(line.split("=", 1) for line in fp.read_text(encoding="utf-8").splitlines() if "=" in line)
    emb_model = data.get("emb_model")
    if emb_model and emb_model != _emb_conf().model:
        print(f"[load_index] 警告：索引使用模型 {emb_model}，当前配置为 {_emb_conf().model}，可能造成维度/语义不一致。")


def create_index(docs: List[Document], save_path: str) -> FAISS:
    save_dir = Path(save_path).resolve()
    save_dir.mkdir(parents=True, exist_ok=True)
    vs = FAISS.from_documents(docs, _emb())
    vs.save_local(str(save_dir))
    _write_fingerprint(save_dir, vs)
    print(f"✅ 向量索引已保存至：{save_dir}")
    return vs

def load_index(save_path: str) -> FAISS:
    save_dir = Path(save_path).resolve()
    _check_fingerprint(save_dir)
    # 避免危险反序列化：尽量只加载自己创建的目录；保持最小权限运行
    return FAISS.load_local(
        str(save_dir),
        _emb(),
        allow_dangerous_deserialization=False,  # 更安全；如历史索引必须加载，再权衡开启
    )


def get_llm():
    return ChatOpenAI(
        model=os.getenv("DEEPSEEK_MODEL", "deepseek-chat"),
        api_key=os.getenv("DEEPSEEK_API_KEY"),
        base_url=os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com"),
        temperature=float(os.getenv("RAG_TEMPERATURE", "0.2")),
        timeout=60,
    )


def get_qa_chain(vectorstore: Optional[FAISS]):
    llm = get_llm()
    if vectorstore is None:
        # 纯 LLM 回答（不检索），保留你的兜底逻辑
        from langchain.chains import LLMChain
        from langchain.prompts import PromptTemplate
        return LLMChain(llm=llm, prompt=PromptTemplate.from_template("直接回答：{q}"))

    retriever = vectorstore.as_retriever(
        search_type=SEARCH_TYPE,  # "similarity" 或 "mmr"
        search_kwargs={"k": TOP_K, "fetch_k": max(TOP_K * 2, 8)} if SEARCH_TYPE == "mmr" else {"k": TOP_K},
    )

    return RetrievalQA.from_chain_type(
        llm=llm,
        retriever=retriever,
        return_source_documents=True,  # 打开以便调试/可观测
        chain_type=os.getenv("RAG_CHAIN_TYPE", "stuff"),
        # 可选：自定义 prompt / combine_docs_chain_kwargs
    )


def get_answer(chain, question: str):
    """
    统一入口：兼容 RetrievalQA / LLMChain
    返回：(answer, sources)
    """
    if hasattr(chain, "invoke"):
        try:
            out = chain.invoke({"query": question})
            if isinstance(out, dict) and "result" in out:
                ans = out["result"]
                srcs = out.get("source_documents", None)
                return ans, srcs
            # LLMChain 情况
            if isinstance(out, dict) and "text" in out:
                return out["text"], None
            # 兜底
            return str(out), None
        except Exception:
            out = chain.invoke({"q": question})
            if isinstance(out, dict) and "text" in out:
                return out["text"], None
            return str(out), None
    # 旧式接口兜底
    return chain.run(question), None
