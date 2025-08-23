from flask import Flask, request, jsonify
from rag_pipeline1 import load_docs, create_index, load_index, get_qa_chain, get_answer
import os

app = Flask(__name__)

if not os.path.exists("index"):
    docs = load_docs(r"backend\ai-agent\docs")
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
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
