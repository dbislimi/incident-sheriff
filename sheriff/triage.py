from enum import StrEnum
from typing import Literal

from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel, Field

from sheriff.llm import get_completion
from sheriff.ticket import Ticket
from sheriff.utils import DATA_DIR, PROMPTS_DIR, get_content

load_dotenv()


class Category(StrEnum):
    UNKNOWN = "Unknown"
    BUSINESSLOGIC = "BusinessLogic"
    NETWORK = "Network"
    DATA = "Data"
    UI = "UI"
    OTHER = "Other"


class Source(BaseModel):
    kind: Literal["ticket", "log"]
    reference: str
    line: int | None = Field(ge=1)


class Fact(BaseModel):
    description: str
    sources: list[Source] = Field(min_length=1)


class TriageResult(BaseModel):
    category: Category
    severity: int | None = Field(ge=1, le=5)
    suspected_function: str | None
    facts: list[Fact]
    hypotheses: list[str]
    missing_information: list[str]


def get_system_prompt():
    role = get_content(PROMPTS_DIR / "triage.txt")
    rules = get_content(DATA_DIR / "business_rules.md")
    if not role or not rules:
        return ""

    return f"""
{role}

<business_rules>
{rules}
</business_rules>
""".strip()


def get_user_prompt(ticket: Ticket):
    ticket_json = ticket.model_dump_json(indent=2)
    if not ticket_json:
        return ""
    return f"""
<incident_ticket>
{ticket_json}
</incident_ticket>
""".strip()


def audit_facts(ticket: Ticket, result: TriageResult):
    errors = []
    log_sources = {(str(log.source_file), log.line) for log in ticket.corr_logs}

    for i, fact in enumerate(result.facts, start=1):
        for source in fact.sources:
            if source.kind == "ticket":
                if source.line is not None:
                    errors.append(f"Fact {i}: ticket source must not have a line.")
                if source.reference not in Ticket.model_fields:
                    errors.append(f"Fact {i}: unknown ticket field: {source.reference}")
            else:
                if (source.reference, source.line) not in log_sources:
                    errors.append(
                        f"Fact {i}: log source not provided:\n{source.reference}:{source.line}"
                    )
    return errors


def triage_ticket(
    model: str,
    client: OpenAI,
    ticket: Ticket,
    verbose: bool,
    audit_warnings: list[str] | None = None,
) -> TriageResult:
    result = get_completion(
        client,
        model,
        get_system_prompt(),
        get_user_prompt(ticket),
        TriageResult,
        verbose,
    )
    errors = audit_facts(ticket, result)
    if errors:
        for error in errors:
            print(f"Audit error: {error}")
        if audit_warnings is not None:
            audit_warnings.extend(errors)
        raise RuntimeError(
            "Triage source audit failed; see audit warnings in metadata."
        )
    if verbose:
        print("RESULT:\n", result.model_dump_json(indent=2))
    return result
