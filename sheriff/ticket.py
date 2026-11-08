import json
from dataclasses import dataclass
from pathlib import Path
from typing import Annotated

from pydantic import AwareDatetime, BaseModel, Field, StringConstraints, ValidationError

from sheriff.utils import DATA_DIR


@dataclass
class Log:
    source_file: Path
    line: int
    msg: str


NonEmptyText = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]


class Ticket(BaseModel):
    id: str = Field(pattern=r"^DISRUPT-[0-9]{3}$")
    title: NonEmptyText
    correlation_id: str = Field(pattern=r"^corr-[a-zA-Z0-9-]+$")
    observed_result: NonEmptyText
    expected_result: NonEmptyText
    description: NonEmptyText
    date: AwareDatetime

    corr_logs: list[Log] = Field(default_factory=list)


def load_ticket(file_path: Path):
    ticket: Ticket | None = None

    try:
        data = json.loads(file_path.read_text(encoding="utf-8"))
        ticket = Ticket(**data)
    except (json.JSONDecodeError, OSError) as e:
        print(f"Error: {e}")
    except ValidationError as e:
        print(f"Error: {file_path.name}: {e}")
    return ticket


def find_corr_logs(ticket: Ticket, limit: int, offset: int):
    if limit <= 0 or offset < 0:
        raise ValueError("Limit must be positive and offset must be non-negative.")

    logs_dir = DATA_DIR / "logs"
    target = "correlation_id="
    logs: list[Log] = []
    matched = 0

    for logs_file in sorted(logs_dir.glob("*.log")):
        with open(logs_file, "r", encoding="utf-8") as f:
            for line_nb, line in enumerate(f, start=1):
                if target + ticket.correlation_id not in line.split():
                    continue
                if matched >= offset:
                    if len(logs) == limit:
                        ticket.corr_logs = logs
                        return True
                    logs.append(
                        Log(
                            logs_file.relative_to(DATA_DIR.parent),
                            line_nb,
                            line.rstrip("\r\n"),
                        )
                    )
                matched += 1

    ticket.corr_logs = logs
    return False


def print_logs(ticket: Ticket):
    print(f"Ticket {ticket.id} logs:")
    for log in ticket.corr_logs:
        print(f"Line {log.line}: {log.msg} ({log.source_file})")
    print()
