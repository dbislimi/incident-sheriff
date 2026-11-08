from datetime import datetime
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field

StepStatus = Literal["pending", "running", "completed", "failed"]
RunStatus = Literal["running", "completed", "failed"]

class LogsMetadata(BaseModel):
    limit: int
    offset: int
    selected_count: int
    truncated: bool

class StepMetadata(BaseModel):
    status: StepStatus = "pending"
    duration_seconds: float | None = None
    audit_warnings: list[str] = Field(default_factory=list)
    error: str | None = None
    error_type: str | None = None

class Model(BaseModel):
    name: str
    temperature: float

class RunMetadata(BaseModel):
    schema_version: int = 1
    run_id: str
    ticket_id: str
    ticket_file: str

    started_at: datetime
    finished_at: datetime | None = None
    status: RunStatus = "running"

    model: Model
    logs: LogsMetadata
    steps: dict[str, StepMetadata] = Field(default_factory=dict)
    artifacts: list[str] = Field(default_factory=list)

    failed_step: str | None = None
    error: str | None = None
    error_type: str | None = None


def write_metadata(run_dir: Path, metadata: RunMetadata):
    path = run_dir / "metadata.json"

    path.write_text(
        metadata.model_dump_json(indent=2),
        encoding="utf-8"
    )

