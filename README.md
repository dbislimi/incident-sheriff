# Incident Sheriff

A local proof of concept for investigating software incidents and proposing C++ regression tests with a language model. The domain model covers passenger rebooking after a cancelled flight.

## What it does

Given a JSON incident ticket, the Python CLI:

1. Validates the ticket and selects local log lines with the same correlation ID, preserving their file and line number.
2. Asks a local model for a structured triage: category, severity, sourced facts, hypotheses and missing information.
3. Independently asks it for a Google Test candidate, using the ticket, logs, business rules and public C++ interface. It can instead report insufficient context.
4. Saves the responses and run metadata under `output/<ticket>/<run_id>/`. If a test is generated, it also saves the source and a compilation log.

The generated test is **compiled, not automatically executed**. Both the triage and test require human review. The triage is not passed to the test-generation step; the two model calls use the same incident evidence independently.

```text
ticket + local logs ──> correlated evidence ──┬──> triage JSON
                                              └──> test candidate ──> compile
```

## Example scenarios

| Ticket | Scenario | What to look for |
| --- | --- | --- |
| `DISRUPT-001` | An eligible flight with two seats is rejected. | A candidate test can expose the deliberately introduced defect in the C++ engine. |
| `DISRUPT-002` | An alternative search times out. | A timeout does not establish a network cause. The C++ interface cannot simulate a timeout, so a meaningful test requires more context or another interface. |
| `DISRUPT-003` | The original flight ID is unknown. | The C++ interface accepts a constructed flight and has no repository lookup; it cannot verify the unknown-ID behavior. |

Human reference answers are in `data/references/` and are not included in model prompts. On a reviewed run for 001, the generated incident test failed against the intentionally defective engine as expected. Another generated test had contradictory assertions. Earlier runs for 003 produced compilable but invalid tests; after a prompt change, one run correctly abstained, though its explanation still contained an incorrect suggestion. These few examples demonstrate the workflow, not a statistical measure of model reliability.

## Requirements

- Python 3.11 or later and [uv](https://docs.astral.sh/uv/).
- [Ollama](https://ollama.com/) running locally, with enough memory for the model.
- A C++20 compiler, CMake and Google Test available to CMake (`find_package(GTest REQUIRED)`).

From the project root, install the Python dependencies and prepare the model used in the recorded runs:

```bash
uv sync
ollama pull qwen3.5:4b
ollama create qwen3.5:4b-16k -f Modelfile
```

The default endpoint is `http://localhost:11434/v1` and the default model is `qwen3.5:4b-16k`. Configuration can be overridden using `LLM_BASE_URL`, `LLM_API_KEY` and `CHAT_MODEL`; see `.env.example`. A non-local endpoint may have its own privacy and pricing implications.

## Run a ticket

```bash
uv run python main.py data/tickets/DISRUPT-001.json
uv run python main.py data/tickets/DISRUPT-002.json
uv run python main.py data/tickets/DISRUPT-003.json
```

Use `--verbose` to display the selected logs, prompts and responses. `--limit` and `--offset` control log selection. Each run records its model, selected log count, step status, duration and artifacts in `metadata.json`. A completed step means the pipeline completed; it does not certify the correctness of the model's response. The CLI stops if no correlated logs are found.

To execute a generated candidate **after reviewing it**, run:

```bash
uv run python test_runner.py
```

Select a listed test by its displayed index. This rebuilds the selected candidate and runs it with CTest. An assertion failure on the buggy engine can be the expected result of reproducing a defect; inspect the failure and the test inputs before drawing that conclusion.

## Scope and limitations

- `cpp/rebooking.cpp` contains a deliberate bug: it rejects flights with exactly two available seats. The ticket and logs show a rejection, but do not establish that exact cause. The model does not receive the implementation.
- The simplified interface filters supplied flights; it does not implement remote search, timeout handling or repository lookup. It cannot distinguish a failed search or unknown flight from other application-level outcomes.
- Pydantic validates the response structure and the source audit checks that cited references exist in the supplied ticket or logs. Neither proves that a cited source supports a claim or that a generated assertion is correct.
- A test that compiles can still test the wrong behavior. Outputs vary between runs, especially with a small local model; there is no measured production reliability or automatic correction of generated tests.
- This is a single Python workflow with two model calls, not a multi-agent system, a real incident assignment service or an end-to-end production maintenance pipeline.

Business rules are in `data/business_rules.md`; versioned prompts are in `prompts/`. `FICHE_POC.md` is a concise project brief.
