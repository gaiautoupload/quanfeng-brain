"""
FastAPI service for QuanFeng Smart Brain RAG system.
Provides REST API endpoints for document retrieval and Q&A.
"""
import io
import sys
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import ollama
import chromadb
from chromadb.config import Settings

# Fix Windows console encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

# Configuration
VECTOR_STORE_DIR = r"C:\Users\III-AIPC-02\.nanobot_2\workspace\quanfeng_brain\vector_store"
COLLECTION_NAME = "quanfeng_docs"
LLM_MODEL = "qwen3.6:27b"
EMBEDDING_MODEL = "nomic-embed-text"
TOP_K = 10
SIMILARITY_THRESHOLD = 0.30

app = FastAPI(
    title="QuanFeng Smart Brain RAG API",
    description="RAG API for QuanFeng Smart Brain knowledge base",
    version="1.0.0"
)


class QueryRequest(BaseModel):
    query: str
    top_k: int = TOP_K


class QueryResponse(BaseModel):
    query: str
    answer: str
    sources: list = []


def get_embedding(text: str) -> list:
    """Get embedding for a query using Ollama."""
    response = ollama.embed(model=EMBEDDING_MODEL, input=text)
    return response["embeddings"][0]


def retrieve_relevant_chunks(query: str, top_k: int = TOP_K) -> list:
    """Retrieve relevant document chunks from ChromaDB."""
    client = chromadb.PersistentClient(path=VECTOR_STORE_DIR)
    collection = client.get_collection(name=COLLECTION_NAME)
    
    query_embedding = get_embedding(query)
    
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        include=["documents", "metadatas", "distances"]
    )
    
    return results


def generate_answer(query: str, context: str) -> str:
    """Generate an answer using Ollama LLM with retrieved context."""
    system_prompt = """你是全鋒智慧大腦的客服助手。請根據提供的參考資料回答用戶問題。
如果參考資料中沒有相關資訊，請誠實說明「目前資料中未找到相關資訊」。
回答要簡潔、專業、有禮貌。
"""
    
    user_prompt = f"""
參考資料：
{context}

用戶問題：{query}

請根據參考資料回答：
"""
    
    response = ollama.chat(
        model=LLM_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
    )
    
    return response["message"]["content"]


# Root endpoint moved to FileResponse below for Web UI


@app.post("/query", response_model=QueryResponse)
def query_endpoint(request: QueryRequest):
    """Query the RAG system with a question."""
    try:
        # Retrieve relevant chunks
        results = retrieve_relevant_chunks(request.query, request.top_k)
        
        # Build context and sources with similarity threshold
        context_parts = []
        sources = []

        for i, (doc, meta, dist) in enumerate(zip(results["documents"][0], results["metadatas"][0], results["distances"][0])):
            similarity = 1 - dist
            if similarity < SIMILARITY_THRESHOLD:
                continue
            context_parts.append(f"[來源: {meta['source']}, 相似度: {similarity:.3f}]\n{doc}")
            sources.append({
                "source": meta["source"],
                "similarity": round(similarity, 3),
                "content_preview": doc[:200] + "..." if len(doc) > 200 else doc
            })

        if not context_parts:
            return QueryResponse(
                query=request.query,
                answer="目前資料中未找到相關資訊（相似度低於門檻）。",
                sources=[]
            )
        
        context = "\n\n---\n\n".join(context_parts)
        
        # Generate answer
        answer = generate_answer(request.query, context)
        
        return QueryResponse(
            query=request.query,
            answer=answer,
            sources=sources
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


# Serve static files (Web UI)
STATIC_DIR = r"C:\Users\III-AIPC-02\.nanobot_2\workspace\quanfeng_brain\static"

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/")
def root():
    return FileResponse(r"C:\Users\III-AIPC-02\.nanobot_2\workspace\quanfeng_brain\static\index.html")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
