import os
from dotenv import load_dotenv
from langchain_community.document_loaders import UnstructuredFileLoader
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_openai import ChatOpenAI
from langchain.chains import RetrievalQA

load_dotenv()

# 文档加载
def load_docs(doc_folder="docs"):
    docs = []
    for fname in os.listdir(doc_folder):
        path = os.path.join(doc_folder, fname)
        if path.endswith(".pdf") or path.endswith(".txt"):
            loader = UnstructuredFileLoader(path)
            docs += loader.load()
    print(f"✅ 加载文档完成，共 {len(docs)} 条 chunk")
    return docs

# 创建嵌入（HuggingFace 本地中文模型）
def get_embedding_model():
    return HuggingFaceEmbeddings(
        model_name="BAAI/bge-small-zh-v1.5",
        model_kwargs={"device": "cpu"}  # 若使用 GPU 改为 "cuda"
    )

# 创建向量索引
def create_index(docs, save_path="index"):
    embedding = get_embedding_model()
    vectorstore = FAISS.from_documents(docs, embedding)
    vectorstore.save_local(save_path)
    print(f"✅ 向量索引已保存至：{save_path}")
    return vectorstore

# 加载已有索引
def load_index(save_path="index"):
    embedding = get_embedding_model()
    return FAISS.load_local(save_path, embedding)

# 创建 DeepSeek 模型问答链
def get_qa_chain(vectorstore):
    llm = ChatOpenAI(
        model_name="deepseek-chat",
        temperature=0,
        openai_api_key=os.getenv("OPENAI_API_KEY"),
        openai_api_base=os.getenv("OPENAI_API_BASE")
    )
    return RetrievalQA.from_chain_type(
        llm=llm,
        retriever=vectorstore.as_retriever(),
        return_source_documents=False  # 如果需要返回引用可改为 True
    )

# 获取答案
def get_answer(chain, question):
    return chain.run(question)
