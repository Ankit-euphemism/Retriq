from typing import Optional
from app.services.document_loader import load_document_from_url, load_document_from_bytes
from app.services.embedder import chunk_text, build_index
from app.services.retriever import retrieve_chunks
from app.services.llm import get_answer
# Pipeline service that orchestrates the document loading, embedding, retrieval, and LLM answering process.
def run_pipeline(
    questions: list[str],
    document_url: Optional[str] = None,
    file_bytes: Optional[bytes] = None,
) -> list[str]:
    # Load doc — either from URL or raw bytes
    if file_bytes:
        raw_text = load_document_from_bytes(file_bytes)
    elif document_url:
        raw_text = load_document_from_url(document_url)
    else:
        raise ValueError("Need url or file_bytes")

    chunks = chunk_text(raw_text)
    index, _, chunks = build_index(chunks)

    answers = []
    for question in questions:
        relevant = retrieve_chunks(question, index, chunks)
        answer = get_answer(question, relevant)
        answers.append(answer)

    return answers