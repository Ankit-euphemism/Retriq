import numpy as np
from app.core.config import settings
from app.services.embedding_model import get_embedding_model
"""
Retriever service for finding similar chunks based on a question.
"""
model = get_embedding_model()

def retrieve_chunks(question: str, index, chunks: list[str]) -> list[str]:
    """Embed question → find top-k closest chunks from FAISS."""
    q_embedding = np.asarray(model.encode([question]), dtype="float32")
    distances, indices = index.search(q_embedding, settings.top_k)

    results = []
    for i in indices[0]:
        if i < len(chunks):
            results.append(chunks[i])
    return results
