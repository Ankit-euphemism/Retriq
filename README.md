# Retriq

Retriq is a personal document question-answering application. Upload a PDF or DOCX file, ask one or more questions in plain language, and receive concise answers based on the most relevant parts of that document.

It uses a retrieval-augmented generation (RAG) workflow: the document is converted to text, split into overlapping sections, indexed as embeddings, and searched for context before an LLM prepares each answer. This keeps responses focused on the supplied document rather than general model knowledge.

## What it does

- Accepts PDF and DOCX documents through a browser upload or a document URL.
- Extracts text and splits it into overlapping, word-based chunks.
- Creates local embeddings with `sentence-transformers/all-MiniLM-L6-v2`.
- Uses FAISS similarity search to find the chunks most relevant to every question.
- Sends only the retrieved context and question to an OpenRouter model for answering.
- Returns answers in the same order as the submitted questions.
- Provides a small static web interface and an HTTP API.

## How it works

```text
PDF/DOCX -> text extraction -> overlapping chunks -> embeddings + FAISS index
                                                        |
Question --------------------------------------> relevant chunks -> OpenRouter -> answer
```

The index is created in memory for each request. Documents and indexes are not persisted by the application.

## Tech stack

| Area | Technology |
| --- | --- |
| API | FastAPI, Uvicorn, Pydantic |
| Document parsing | pdfplumber, python-docx |
| Embeddings | Sentence Transformers (`all-MiniLM-L6-v2`) |
| Retrieval | FAISS |
| Answer generation | OpenRouter |
| Interface | HTML, Tailwind CSS (CDN), vanilla JavaScript |

## Project layout

```text
Retriq/
|-- backend/
|   |-- app/
|   |   |-- api/routes.py              # Upload and URL-query endpoints
|   |   |-- core/config.py             # Environment-backed settings
|   |   |-- core/pipeline.py           # End-to-end RAG orchestration
|   |   |-- models/schemas.py          # API request/response models
|   |   `-- services/
|   |       |-- document_loader.py     # PDF/DOCX detection and text extraction
|   |       |-- embedder.py            # Chunking and FAISS index creation
|   |       |-- embedding_model.py     # Cached Sentence Transformer loader
|   |       |-- retriever.py           # Similarity search
|   |       `-- llm.py                 # OpenRouter answer generation
|   |-- main.py                        # FastAPI entry point
|   |-- requirements.txt               # Runtime dependencies
|   |-- .env.example                   # Configuration template
|   `-- render.yml                     # Render deployment configuration
|-- frontend/
|   `-- index.html                     # Static upload and question interface
`-- README.md
```

## Getting started

### Prerequisites

- Python 3.11, 3.12, or 3.13
- An OpenRouter API key

The embedding model is downloaded by Sentence Transformers the first time the backend starts. A Hugging Face token is optional, but can be useful in environments that require authenticated model downloads.

### 1. Configure and start the backend

From the repository root:

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

On macOS or Linux, activate the environment with `source .venv/bin/activate` and copy the template with `cp .env.example .env`.

Update `backend/.env`:

```env
OPENROUTER_API_KEY="your_openrouter_api_key_here"
OPENROUTER_MODEL="openrouter/auto"
# HF_TOKEN is optional
# EMBEDDING_MODEL_NAME="sentence-transformers/all-MiniLM-L6-v2"
```

Start the API:

```powershell
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

The service is then available at `http://127.0.0.1:8000`, with interactive API documentation at `http://127.0.0.1:8000/docs`.

### 2. Open the frontend

Open `frontend/index.html` in a browser while the API is running. The page sends uploads to `http://127.0.0.1:8000/api/v1/query/upload`.

Select a PDF or DOCX, enter a single question or a JSON list of questions, and choose **Ask Retriq**.

## API reference

### `GET /`

Returns a short service welcome message.

### `GET /health`

Returns the service status for health checks.

```json
{
  "status": "ok",
  "app": "Retriq Query System"
}
```

### `POST /api/v1/query/upload`

Accepts a multipart document upload. The backend verifies the uploaded bytes and supports PDF and DOCX documents.

| Form field | Type | Description |
| --- | --- | --- |
| `file` | file | PDF or DOCX document |
| `questions` | string | One question, a JSON string, or a JSON array of strings |

Example:

```bash
curl -X POST http://127.0.0.1:8000/api/v1/query/upload \
  -F "file=@./document.pdf" \
  -F 'questions=["What is the effective date?", "How can the agreement be terminated?"]'
```

### `POST /api/v1/query/run`

Fetches a PDF or DOCX from a URL and answers the provided questions.

```json
{
  "documents": "https://example.com/document.pdf",
  "questions": [
    "What is the termination clause?"
  ]
}
```

Both query endpoints return:

```json
{
  "answers": [
    "The answer to the first question.",
    "The answer to the second question."
  ]
}
```

## Configuration

Settings are defined in `backend/app/core/config.py` and can be supplied through `backend/.env` or environment variables.

| Environment variable | Default | Purpose |
| --- | --- | --- |
| `OPENROUTER_API_KEY` | empty | Required API key for answer generation |
| `OPENROUTER_MODEL` | `openrouter/auto` | OpenRouter model identifier |
| `HF_TOKEN` | empty | Optional Hugging Face access token |
| `HUGGINGFACE_HUB_TOKEN` | empty | Alternative name for the Hugging Face token |
| `EMBEDDING_MODEL_NAME` | `sentence-transformers/all-MiniLM-L6-v2` | Sentence Transformer used for embeddings |

The chunk size (`500` words), chunk overlap (`50` words), and retrieval count (`5` chunks) are code defaults in `config.py` rather than environment variables.

## Deployment

`backend/render.yml` contains a Render web-service configuration. It installs dependencies from `requirements.txt`, starts Uvicorn, and uses `/health` as the health-check path.

Set `OPENROUTER_API_KEY` (and optionally `OPENROUTER_MODEL`, `HF_TOKEN`, and `EMBEDDING_MODEL_NAME`) in the deployment environment. If the frontend is hosted separately, update its API URL in `frontend/index.html`. The backend currently permits cross-origin requests from any origin, so restrict CORS in `backend/main.py` before a public production deployment.

## Current limitations

- Scanned PDFs without selectable text are not OCR processed.
- Tables, images, headers, and complex document formatting may not be fully represented in the extracted text.
- Very large documents take longer because embeddings and the FAISS index are rebuilt for each request.
- Answer quality depends on text extraction, retrieved context, and the selected OpenRouter model.
- The URL-query endpoint fetches a user-provided document URL server-side; protect or restrict it appropriately before exposing it publicly.
