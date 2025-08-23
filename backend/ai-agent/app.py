from flask import Flask, request, jsonify
from rag_pipeline1 import load_docs, create_index, load_index, get_qa_chain, get_answer
import os

app = Flask(__name__)

if not os.path.exists("index"):
    docs = load_docs(r"E:\my_world\backend\ai-agent\docs")
    vectorstore = create_index(docs)
else:
    vectorstore = load_index()

qa_chain = get_qa_chain(vectorstore)

@app.route("/ask", methods=["POST"])
def ask():
    data = request.get_json()
    question = data.get("question", "")
    answer = get_answer(qa_chain, question)
    return jsonify({"answer": answer})

if __name__ == "__main__":
    app.run(port=5000)
