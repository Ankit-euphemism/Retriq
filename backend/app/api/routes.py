import json
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from app.models.schemas import QueryRequest, QueryResponse
from app.core.pipeline import run_pipeline

router = APIRouter()

# Helper function to parse questions from JSON string and validate them
def _parse_questions(raw_questions: str) -> list[str]:
    raw_questions = raw_questions.strip()
    if not raw_questions:
        raise HTTPException(
            status_code=400,
            detail="questions is required",
        )

    try:
        parsed_questions = json.loads(raw_questions)
    except json.JSONDecodeError:
        return [raw_questions]

    if isinstance(parsed_questions, str):
        parsed_questions = [parsed_questions]

    if not isinstance(parsed_questions, list) or not all(isinstance(item, str) for item in parsed_questions):
        raise HTTPException(
            status_code=400,
            detail="questions must be a JSON array of strings",
        )

    cleaned_questions = [item.strip() for item in parsed_questions if item.strip()]
    if not cleaned_questions:
        raise HTTPException(
            status_code=400,
            detail="questions must contain at least one non-empty string",
        )

    return cleaned_questions

# Original URL-based endpoint (keep working)
@router.post("/query/run", response_model=QueryResponse)
async def query_run(payload: QueryRequest):
    try:
        answers = run_pipeline(
            questions=payload.questions,
            document_url=payload.documents
        )
        return QueryResponse(answers=answers)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# NEW — file upload endpoint for frontend
@router.post("/query/upload", response_model=QueryResponse)
async def query_upload(
    file: UploadFile = File(...),           # PDF file
    questions: str = Form(...)              # JSON string of questions list
):
    try:
        file_bytes = await file.read()
        questions_list = _parse_questions(questions)

        answers = run_pipeline(
            questions=questions_list,
            file_bytes=file_bytes
        )
        return QueryResponse(answers=answers)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))