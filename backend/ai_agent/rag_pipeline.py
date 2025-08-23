import os
from langchain.document_loaders import UnstructuredFileLoader
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.chat_models import ChatOpenAI
from langchain.chains import RetrievalQA
from dotenv import load_dotenv

load_dotenv()

# 加载文档并向量化
def load_docs(doc_folder="docs"):
    docs = []
    for fname in os.listdir(doc_folder):
        path = os.path.join(doc_folder, fname)
        if path.endswith(".pdf") or path.endswith(".txt"):
            loader = UnstructuredFileLoader(path)
            docs += loader.load()
    return docs

# 创建向量索引
def create_index(docs, save_path="index"):
    embeddings = OpenAIEmbeddings()
    vectorstore = FAISS.from_documents(docs, embeddings)
    vectorstore.save_local(save_path)
    return vectorstore

# 加载已有索引
def load_index(save_path="index"):
    embeddings = OpenAIEmbeddings()
    return FAISS.load_local(save_path, embeddings)

# 创建问答链
def get_qa_chain(vectorstore):
    llm = ChatOpenAI(model_name="gpt-4-1106-preview", temperature=0)
    return RetrievalQA.from_chain_type(llm=llm, retriever=vectorstore.as_retriever())

# 获取答案
def get_answer(chain, question):
    return chain.run(question)
