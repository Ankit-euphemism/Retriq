import os
from functools import lru_cache

from sentence_transformers import SentenceTransformer

from app.core.config import settings

"""
Get the embedding model and securely set the Hugging Face token in the environment if provided in settings. 
The model is cached to avoid reloading it multiple times.
"""
@lru_cache(maxsize=1)
def get_embedding_model() -> SentenceTransformer:
    if settings.hf_token and not os.environ.get("HF_TOKEN"):
        os.environ["HF_TOKEN"] = settings.hf_token

    return SentenceTransformer(settings.embedding_model_name)
