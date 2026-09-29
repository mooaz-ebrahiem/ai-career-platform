import os
from pathlib import Path

import chromadb
from chromadb.utils import embedding_functions

from app.config import PROJECT_ROOT


STORAGE_PATH = Path(os.getenv("CHROMA_PERSIST_DIR", str(PROJECT_ROOT / "chroma_db")))
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
CHUNK_SIZE = 800
CHUNK_OVERLAP = 120

_client = chromadb.PersistentClient(path=str(STORAGE_PATH))
_collection = None


def _get_collection():
    global _collection
    if _collection is None:
        embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name=EMBEDDING_MODEL,
        )
        _collection = _client.get_or_create_collection(
            name="resumes_collection",
            embedding_function=embedding_function,
        )
    return _collection


def chunk_text(text: str) -> list[str]:
    chunks = []
    start = 0
    while start < len(text):
        end = min(start + CHUNK_SIZE, len(text))
        chunks.append(text[start:end])
        if end == len(text):
            break
        start = end - CHUNK_OVERLAP
    return chunks


def index_resume(resume_id: int | str, resume_text: str) -> dict:
    chunks = chunk_text(resume_text)
    identifier = str(resume_id)
    _get_collection().upsert(
        ids=[f"{identifier}_chunk_{index}" for index in range(len(chunks))],
        documents=chunks,
        metadatas=[
            {"resume_id": identifier, "chunk_index": index}
            for index in range(len(chunks))
        ],
    )
    return {"status": "indexed", "chunks_indexed": len(chunks)}


def retrieve_resume_chunks(resume_id: int | str, query: str, limit: int = 4) -> list[dict]:
    result = _get_collection().query(
        query_texts=[query],
        n_results=limit,
        where={"resume_id": str(resume_id)},
        include=["documents", "distances", "metadatas"],
    )
    documents = result.get("documents", [[]])[0] or []
    distances = result.get("distances", [[]])[0] or []
    metadatas = result.get("metadatas", [[]])[0] or []
    return [
        {
            "text": document,
            "distance": distances[index] if index < len(distances) else None,
            "chunk_index": metadatas[index].get("chunk_index") if index < len(metadatas) else None,
        }
        for index, document in enumerate(documents)
    ]
