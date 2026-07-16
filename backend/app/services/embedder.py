import faiss
import numpy as np
from app.core.config import settings
from app.services.embedding_model import get_embedding_model

"""
Embedding service for converting text into vector representations and store in FAISS index.
"""
model = get_embedding_model()
# chunk_text and build_index are used in the pipeline to prepare documents for retrieval.
def chunk_text(text: str) -> list[str]:
    """Split text into overlapping chunks."""
    words = text.split()
    chunks = []
    size = settings.chunk_size
    overlap = settings.chunk_overlap

    for i in range(0, len(words), size - overlap):
        chunk = " ".join(words[i:i + size])
        if chunk.strip():
            chunks.append(chunk)
    return chunks
# Build a FAISS index from the text chunks.
def build_index(chunks: list[str]):
    """Embed all chunks → FAISS index."""
    embeddings = model.encode(chunks, show_progress_bar=False)
    embeddings = np.array(embeddings).astype("float32")

    dim = embeddings.shape[1]
    index = faiss.IndexFlatL2(dim)
    index.add(embeddings)

    return index, embeddings, chunks
