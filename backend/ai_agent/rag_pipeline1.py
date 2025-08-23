# backend/ai_agent/rag_pipeline1.py
import os
from pathlib import Path
from typing import List
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_openai import ChatOpenAI
from langchain.chains import RetrievalQA

EMBED_MODEL = os.getenv("EMBED_MODEL", "BAAI/bge-small-zh-v1.5")  # ← 统一！
EMBED_KW = {"device": "cpu"}

def _emb():
    return HuggingFaceEmbeddings(model_name=EMBED_MODEL, model_kwargs=EMBED_KW)

def load_docs(doc_folder: str):
    doc_dir = Path(doc_folder)
    docs = []
    if not doc_dir.exists():
        print(f"[load_docs] 文档目录不存在：{doc_dir}")
        return docs
    for p in doc_dir.iterdir():
        if p.suffix.lower() == ".pdf":
            docs.extend(PyPDFLoader(str(p)).load())
        elif p.suffix.lower() == ".txt":
            docs.extend(TextLoader(str(p), encoding="utf-8").load())
    print(f"✅ 加载文档完成，共 {len(docs)} 条 chunk")
    return docs

def create_index(docs, save_path: str):
    save_path = str(Path(save_path).resolve())
    vs = FAISS.from_documents(docs, _emb())
    Path(save_path).mkdir(parents=True, exist_ok=True)
    vs.save_local(save_path)
    print(f"✅ 向量索引已保存至：{save_path}")
    return vs

def load_index(save_path: str):
    save_path = str(Path(save_path).resolve())
    return FAISS.load_local(save_path, _emb(), allow_dangerous_deserialization=True)

def get_qa_chain(vectorstore):
    llm = ChatOpenAI(
        model_name=os.getenv("OPENAI_MODEL", "deepseek-chat"),
        temperature=float(os.getenv("TEMPERATURE", "0")),
        openai_api_key=os.getenv("OPENAI_API_KEY"),
        openai_api_base=os.getenv("OPENAI_API_BASE"),
    )
    if vectorstore is None:
        from langchain.chains import LLMChain
        from langchain.prompts import PromptTemplate
        return LLMChain(llm=llm, prompt=PromptTemplate.from_template("直接回答：{q}"))
    return RetrievalQA.from_chain_type(
        llm=llm,
        retriever=vectorstore.as_retriever(search_kwargs={"k": 4}),
        return_source_documents=False,
        chain_type="stuff",
    )

def get_answer(chain, question: str):
    # 统一用 invoke，兼容 RetrievalQA / LLMChain
    if hasattr(chain, "invoke"):
        # RetrievalQA 期望 {"query": "..."}；LLMChain 期望 {"q": "..."}
        try:
            return chain.invoke({"query": question})["result"]
        except Exception:
            return chain.invoke({"q": question})["text"]
    # 兜底
    return chain.run(question)
