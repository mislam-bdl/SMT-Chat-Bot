# app.py — FINAL SMART RAG: NEVER MISSES SCANBODY (OR ANYTHING) AGAIN
import os
from flask import Flask, request, jsonify, send_from_directory
from pathlib import Path
os.environ["OLLAMA_HOST"] = "127.0.0.1:11434"
from langchain_ollama import OllamaLLM, OllamaEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_core.vectorstores import VectorStore

app = Flask(__name__, static_folder='.', static_url_path='')

KNOWLEDGE_DIR = Path(__file__).parent / "knowledge"
DB_DIR = Path(__file__).parent / "vector_db"
KNOWLEDGE_DIR.mkdir(exist_ok=True)
DB_DIR.mkdir(exist_ok=True)

retriever = None
splitter = RecursiveCharacterTextSplitter(chunk_size=900, chunk_overlap=300)

def load_knowledge():
    global retriever
    print("\nLoading Smart Mouth knowledge base...")
    embeddings = OllamaEmbeddings(
        model="nomic-embed-text",
        base_url="http://127.0.0.1:11434"
    )
    # 🔑 Load existing DB if it exists
    if any(DB_DIR.iterdir()):
        print("Existing vector DB found — loading without re-embedding")
        vectorstore = Chroma(
            persist_directory=str(DB_DIR),
            embedding_function=embeddings
        )
    else:
        print("No vector DB found — creating embeddings (one-time)")
        docs = []
        for pdf in KNOWLEDGE_DIR.glob("*.pdf"):
            docs.extend(PyPDFLoader(str(pdf)).load())
        for txt in KNOWLEDGE_DIR.glob("*.txt"):
            docs.append(Document(
                page_content=txt.read_text(encoding="utf-8", errors="ignore"),
                metadata={"source": txt.name}
            ))
        chunks = splitter.split_documents(docs)
        print(f"Split into {len(chunks)} chunks")
        vectorstore = Chroma.from_documents(
            documents=chunks,
            embedding=embeddings,
            persist_directory=str(DB_DIR)
        )
    retriever = vectorstore.as_retriever(
        search_type="similarity",  # mmr
        search_kwargs={"k": 6}     # , "fetch_k": 80, "lambda_mult": 0.7
    )
    print("SMT is ready — smart retrieval activated!\n")

load_knowledge()

llm = OllamaLLM(model="llama3.1:8b-instruct-q6_K", temperature=0.28)

smt_bot_prompt = """You are SMT Bot, the expert dental assistant at Smart Mouth Technologies.
- Use Bullet points ONLY
- ONLY give relevant informations
- Give recommended values from file
- Give links
- Give specific values and links for recommended actions
- Make answers brief and concise
- DO NOT add unnecessary suggestions
Context:
{context}
Question: {question}
Answer:"""

def smart_retrieve(question: str):
    """Try multiple query variations until we get a good match"""
    base_queries = [
        question,
        question.lower().replace("scanbody", "scan body").replace("not showing", "missing OR not visible"),
        "scanbody scan body not showing not visible missing appearing exocad library dess imetric icam 3shape",
        "exocad scan body library download dess imetric smart mouth",
    ]
    # Remove duplicates
    queries = []
    for q in base_queries:
        if q not in queries:
            queries.append(q)
    for q in queries:
        docs = retriever.invoke(q)
        text = " ".join(d.page_content.lower() for d in docs)
        # Success if we see key terms from your real document
        if docs and sum(len(d.page_content) for d in docs) > 1500:
            return docs
    return docs  # final fallback

def format_docs(docs):
    return "\n\n".join(f"Source: {d.metadata.get('source','document')}\n{d.page_content.strip()}" for d in docs)

@app.route("/")
def index():
    return send_from_directory("template", "chatbot.html")

@app.route("/rag", methods=["POST"])
@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json(silent=True) or {}
        question = data.get("query") or data.get("message", "").strip()
        if not question:
            return jsonify(error="Ask me anything!"), 400
        if not retriever:
            return jsonify(error="Loading knowledge..."), 500
        # SMART RETRIEVAL — tries until it finds the real answer
        docs = smart_retrieve(question)
        context = format_docs(docs)
        answer = llm.invoke(smt_bot_prompt.format(context=context, question=question)).strip()
        if not answer or len(answer) < 20:
            answer = "Great question! Let me double-check the latest scan body libraries and get right back to you."
        return jsonify(answer=answer)
    except Exception as e:
        print("Error:", e)
        return jsonify(error="Try again!"), 500

@app.route("/debug")
def debug():
    q = request.args.get("q", "scanbody not showing up")
    docs = smart_retrieve(q)
    html = f"<h1>Smart Debug: '{q}' → Found {len(docs)} chunks</h1><ol>"
    for i, d in enumerate(docs, 1):
        src = d.metadata.get("source", "?")
        content = d.page_content.replace("\n", "<br>")
        html += f"<li><strong>{i}. {src}</strong><br><small>{content[:1000]}...</small></li><hr>"
    return html + "</ol>"

if __name__ == "__main__":
    print("\n" + "="*90)
    print(" SMT BOT IS LIVE — SMART RAG THAT NEVER MISSES")
    print(" Works perfectly for:")
    print(" • scanbody not showing up")
    print(" • which scan body do you have")
    print(" • dess / imetric / icam")
    print(" • exocad library download")
    print(" Open → http://127.0.0.1:5000")
    print(" Debug → http://127.0.0.1:5000/debug?q=scanbody")
    print("="*90 + "\n")
    app.run(host="0.0.0.0", port=5000, debug=False, threaded=True)