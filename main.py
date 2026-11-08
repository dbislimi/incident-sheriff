import sys
from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path
from time import perf_counter
from uuid import uuid4

import typer
from openai import OpenAI
from pydantic import BaseModel

from sheriff.config import load_env
from sheriff.llm import MODEL_TEMPERATURE
from sheriff.metadata import (
    LogsMetadata,
    Model,
    RunMetadata,
    StepMetadata,
    write_metadata,
)
from sheriff.test_generation import TestGenerationResult, test_generation
from sheriff.ticket import find_corr_logs, load_ticket, print_logs
from sheriff.triage import triage_ticket
from sheriff.utils import Result

CURRENT_PATH = Path(__file__).parent
OUTPUT_DIR = CURRENT_PATH / "output"


def create_run_dir(ticket_path: Path) -> Path | None:
    timestamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    run_id = f"{timestamp}-{uuid4().hex[:6]}"
    run_dir = OUTPUT_DIR / ticket_path.stem / run_id

    try:
        run_dir.mkdir(parents=True, exist_ok=False)
    except FileExistsError:
        print(f"Error : Folder {run_dir} already exists.")
        return None
    return run_dir


def write_json(path: Path, model: BaseModel):
    path.write_text(model.model_dump_json(indent=2), encoding="utf-8")


def process_step(
    step: str, run_dir: Path, metadata: RunMetadata, action: Callable[[], Result | None]
) -> Result:
    print(f"Current step: {step}...")
    metadata.steps[step].status = "running"
    write_metadata(run_dir, metadata)

    started = perf_counter()
    error = None
    result = None

    try:
        result = action()
        if result is None:
            raise RuntimeError(f"{step} failed.")

        filename = f"{step}.json"
        write_json(run_dir / filename, result)
        metadata.artifacts.append(filename)
        if isinstance(result, TestGenerationResult) and result._compilation_error:
            raise RuntimeError(result._compilation_error)
        metadata.steps[step].status = "completed"
    except (Exception, KeyboardInterrupt) as e:
        error = e
        metadata.steps[step].status = "failed"
        metadata.steps[step].error = "Interrupted by user." if isinstance(e, KeyboardInterrupt) else str(e)
        metadata.steps[step].error_type = type(e).__name__
        metadata.failed_step = step

    metadata.steps[step].duration_seconds = perf_counter() - started
    write_metadata(run_dir, metadata)

    if error is not None:
        raise error
    if result is None:
        raise RuntimeError(f"{step} returned no result.")

    return result


def main(ticket_path: Path, limit: int = 10, offset: int = 0, verbose: bool = False):
    print(f"Handling ticket: {ticket_path} ...\n")

    ticket = load_ticket(ticket_path)

    if not ticket:
        print("Could not load ticket.")
        sys.exit(1)
    print(f"{ticket.title}\n")

    truncated = False
    try:
        truncated = find_corr_logs(ticket, limit, offset)
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)

    if not ticket.corr_logs:
        print("Could not find correlate logs.")
        sys.exit(1)
    if truncated:
        print("Warn: some logs were omitted.")

    if verbose:
        print_logs(ticket)

    env = load_env()

    run_dir = create_run_dir(ticket_path)
    if not run_dir:
        sys.exit(1)

    metadata = RunMetadata(
        run_id=run_dir.name,
        ticket_id=ticket.id,
        ticket_file=str(ticket_path),
        started_at=datetime.now(UTC),
        model=Model(name=env.chat_model, temperature=MODEL_TEMPERATURE),
        logs=LogsMetadata(
            limit=limit,
            offset=offset,
            selected_count=len(ticket.corr_logs),
            truncated=truncated,
        ),
        steps={
            "triage": StepMetadata(),
            "test_generation": StepMetadata(),
        },
    )
    write_metadata(run_dir, metadata)

    error = None
    try:
        client = OpenAI(
            api_key=env.api_key,
            base_url=env.base_url,
            max_retries=0,
        )
        process_step(
            "triage",
            run_dir,
            metadata,
            lambda: triage_ticket(
                env.chat_model,
                client,
                ticket,
                verbose,
                metadata.steps["triage"].audit_warnings,
            ),
        )
        process_step(
            "test_generation",
            run_dir,
            metadata,
            lambda: test_generation(
                env.chat_model,
                client,
                ticket,
                verbose,
                run_dir,
                metadata.artifacts,
            ),
        )
        metadata.status = "completed"
    except (Exception, KeyboardInterrupt) as e:
        error = e
        metadata.status = "failed"
        metadata.error = "Interrupted by user." if isinstance(e, KeyboardInterrupt) else str(e)
        metadata.error_type = type(e).__name__

    metadata.finished_at = datetime.now(UTC)
    write_metadata(run_dir, metadata)

    if error is not None:
        if isinstance(error, KeyboardInterrupt):
            raise error
        print(f"Error: {error}")
        sys.exit(1)


if __name__ == "__main__":
    typer.run(main)
