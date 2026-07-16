from pathlib import Path

from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parents[2]


# Settings for the application, including OpenRouter API key, model name, chunk size, overlap, and top-k retrieval settings.
class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=BASE_DIR / ".env", env_file_encoding="utf-8")

    openrouter_api_key: str = Field(default="", validation_alias="OPENROUTER_API_KEY")
    openrouter_base_url: str = "https://openrouter.ai/api/v1"
    model_name: str = Field(default="openrouter/auto", validation_alias="OPENROUTER_MODEL")
    hf_token: str = Field(default="", validation_alias=AliasChoices("HF_TOKEN", "HUGGINGFACE_HUB_TOKEN"))
    embedding_model_name: str = Field(
        default="sentence-transformers/all-MiniLM-L6-v2",
        validation_alias="EMBEDDING_MODEL_NAME",
    )
    chunk_size: int = 500
    chunk_overlap: int = 50
    top_k: int = 5

settings = Settings()
