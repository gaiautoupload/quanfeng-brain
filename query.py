"""
Query script for QuanFeng Smart Brain RAG system.
Retrieves relevant documents from ChromaDB and generates answers using Ollama.
"""
import sys
import io
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
TOP_K = 5


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


def query_rag(query: str):
    """Main RAG query function."""
    print(f"Query: {query}\n")
    
    # Retrieve relevant chunks
    results = retrieve_relevant_chunks(query)
    
    if not results["documents"] or len(results["documents"][0]) == 0:
        print("No relevant documents found.")
        return
    
    # Build context from retrieved chunks
    context_parts = []
    for i, (doc, meta, dist) in enumerate(zip(results["documents"][0], results["metadatas"][0], results["distances"][0])):
        context_parts.append(f"[來源: {meta['source']}, 相似度: {1-dist:.3f}]\n{doc}")
    
    context = "\n\n---\n\n".join(context_parts)
    
    print(f"Found {len(results['documents'][0])} relevant chunks.\n")
    
    # Generate answer
    print("Generating answer...")
    answer = generate_answer(query, context)
    
    print(f"\nAnswer:\n{answer}")


def main():
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
    else:
        query = input("Enter your question: ")
    
    query_rag(query)


if __name__ == "__main__":
    main()
