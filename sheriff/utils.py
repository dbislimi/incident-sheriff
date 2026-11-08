from pathlib import Path
from typing import TypeVar

from pydantic import BaseModel

Result = TypeVar("Result", bound=BaseModel)


CURRENT_PATH = Path(__file__).resolve().parent
DATA_DIR = CURRENT_PATH.parent / "data"
PROMPTS_DIR = CURRENT_PATH.parent / "prompts"
CPP_DIR = CURRENT_PATH.parent / "cpp"

def get_content(path: Path):
    content = ""
    try:
        content = path.read_text(encoding="utf-8")
    except OSError as e:
        print(f"Error: {e}")
        return ""
    return content
