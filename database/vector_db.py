# database/vector_db.py
import os
import chromadb
from dotenv import load_dotenv

load_dotenv()

CHROMA_PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", "./chroma_store")

_client = None

def get_chroma_client() -> chromadb.PersistentClient:
    global _client
    if _client is None:
        _client = chromadb.PersistentClient(path=CHROMA_PERSIST_DIR)
    return _client

def get_coaching_memory_collection():
    """
    Returns the single ChromaDB collection used for all semantic memory.
    Creates it if it doesn't exist.
    """
    client = get_chroma_client()
    collection = client.get_or_create_collection(
        name="coaching_memory",
        metadata={"hnsw:space": "cosine"}
    )
    return collection
