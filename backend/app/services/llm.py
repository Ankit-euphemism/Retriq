from openrouter import OpenRouter
from app.core.config import settings

# LLM service for sending questions and context to the LLM via OpenRouter.
def get_answer(question: str, context_chunks: list[str]) -> str:
    """Send question + retrieved context to LLM via OpenRouter."""
    context = "\n\n---\n\n".join(context_chunks)

    prompt = f"""You are a precise document QA assistant.
Answer ONLY from the context below. Be concise and specific.
If not found, say "Information not available in document."

CONTEXT:
{context}

QUESTION: {question}

ANSWER:"""
# Use OpenRouter to send the prompt to the LLM and get the answer
    with OpenRouter(api_key=settings.openrouter_api_key) as client:
        response = client.chat.send(
            model=settings.model_name,
            messages=[{"role": "user", "content": prompt}],
        )

    content = response.choices[0].message.content

    if not content:
        return ""

    if isinstance(content, str):
        return content.strip()

    return "".join(getattr(part, "text", "") for part in content).strip()