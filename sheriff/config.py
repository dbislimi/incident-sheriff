import os
from dataclasses import dataclass

from dotenv import load_dotenv


@dataclass(frozen=True)
class Env:
    api_key: str
    base_url: str
    chat_model: str


def load_env():
    load_dotenv()

    return Env(
        api_key=os.getenv("LLM_API_KEY", "ollama"),
        base_url=os.getenv("LLM_BASE_URL", "http://localhost:11434/v1"),
        chat_model=os.getenv("CHAT_MODEL", "qwen3.5:4b-16k"),
    )
