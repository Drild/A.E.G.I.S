import chromadb
from sentence_transformers import SentenceTransformer
from datetime import datetime
import uuid

client = chromadb.PersistentClient(path="./memory/db")
collection = client.get_or_create_collection(name="aegis_memory")
embedder = SentenceTransformer("all-MiniLM-L6-v2")

def save_memory(user_message: str, aegis_reply: str):
    text = f"User: {user_message}\nAegis: {aegis_reply}"
    embedding = embedder.encode(text).tolist()
    collection.add(
        documents=[text],
        embeddings=[embedding],
        metadatas=[{"timestamp": datetime.now().isoformat()}],
        ids=[str(uuid.uuid4())]
    )

def search_memory(query: str, n=3) -> str:
    count = collection.count()
    if count == 0:
        return ""

    embedding = embedder.encode(query).tolist()
    results = collection.query(
        query_embeddings=[embedding],
        n_results=min(n, count)
    )

    memories = results["documents"][0]
    if not memories:
        return ""

    return "\n---\n".join(memories)