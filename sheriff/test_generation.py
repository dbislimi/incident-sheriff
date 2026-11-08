import subprocess
from pathlib import Path
from typing import Literal

from openai import OpenAI
from pydantic import BaseModel

from sheriff.llm import get_completion
from sheriff.ticket import Ticket
from sheriff.utils import CPP_DIR, DATA_DIR, PROMPTS_DIR, get_content


class TestGenerationResult(BaseModel):
    status: Literal["generated", "insufficient_context"]
    test_code: str | None
    explanation: str
    missing_information: list[str]
    _compilation_error: str | None = None


def audit_result(result: TestGenerationResult):
    errors = []
    if result.status == "generated" and (
        not result.test_code or not result.test_code.strip()
    ):
        errors.append(
            "Error: TestGenerationResult.test_code should not be empty because status is 'generated'"
        )
    elif result.status == "insufficient_context" and result.test_code is not None:
        errors.append(
            "Error: TestGenerationResult.test_code should be empty because status is 'insufficient_context'"
        )
    elif (
        result.status == "insufficient_context" and len(result.missing_information) == 0
    ):
        errors.append(
            "Error: TestGenerationResult.missing_information should not be empty because status is 'insufficient_context'"
        )
    return errors


def get_system_prompt():
    cpp_interface_path = CPP_DIR / "rebooking.hpp"
    cpp_interface = get_content(cpp_interface_path)
    if not cpp_interface:
        return ""

    rules_path = DATA_DIR / "business_rules.md"
    rules = get_content(rules_path)
    if not rules:
        return ""

    role_path = PROMPTS_DIR / "test_generation.txt"
    role = get_content(role_path)
    if not role:
        return ""

    return f"""
{role}

<business_rules>
{rules}
</business_rules>

<interface>
{cpp_interface}
</interface>
""".strip()


def get_user_prompt(ticket: Ticket):
    return f"<incident_ticket>\n{ticket.model_dump_json()}\n</incident_ticket>"


def test_generation(
    model: str,
    client: OpenAI,
    ticket: Ticket,
    verbose: bool,
    run_dir: Path,
    artifacts: list[str],
) -> TestGenerationResult:
    result = get_completion(
        client,
        model,
        get_system_prompt(),
        get_user_prompt(ticket),
        TestGenerationResult,
        verbose,
    )

    errors = audit_result(result)
    if errors:
        raise ValueError("Invalid test generation result: " + "; ".join(errors))

    if verbose:
        print("RESULT:\n", result.model_dump_json(indent=2))

    if result.status == "generated" and result.test_code:
        source = run_dir / "rebooking_test.cpp"
        source.write_text(result.test_code, encoding="utf-8")
        artifacts.append(source.name)

        log = run_dir / "compilation.log"
        artifacts.append(log.name)
        print("Compiling generated test locally...")
        try:
            compile_candidate(source, log)
        except (OSError, RuntimeError) as e:
            result._compilation_error = str(e)
    return result


def compile_candidate(source: Path, log: Path) -> None:
    build_dir = CPP_DIR / "build"
    commands = [
        [
            "cmake",
            "-S",
            str(CPP_DIR),
            "-B",
            str(build_dir),
            f"-DTEST_SOURCE_FILE={source.resolve()}",
            "-DDISCOVER_TESTS=OFF",
        ],
        ["cmake", "--build", str(build_dir)],
    ]
    with log.open("w", encoding="utf-8") as output:
        for command in commands:
            output.write("$ " + " ".join(command) + "\n")
            output.flush()
            try:
                completed = subprocess.run(
                    command, stdout=output, stderr=subprocess.STDOUT, timeout=60
                )
            except (OSError, subprocess.TimeoutExpired) as e:
                output.write(f"Compilation error: {e}\n")
                raise RuntimeError(f"Compilation failed; see {log}") from e
            if completed.returncode != 0:
                output.write(f"Exit code: {completed.returncode}\n")
                raise RuntimeError(f"Compilation failed; see {log}")
