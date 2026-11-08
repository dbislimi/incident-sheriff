# Incident Sheriff — project brief

## Purpose

Incident Sheriff is a proof of concept for AI-assisted software maintenance. It takes an incident ticket and local logs, proposes a structured triage, and attempts to generate a C++ regression test. An engineer reviews the results and decides what to do next.

The domain model covers passenger rebooking after a cancelled flight.

## Workflow

1. Validate a ticket and retrieve local log lines using its correlation ID.
2. Ask a local model for a category, severity, sourced facts, hypotheses and missing information.
3. Independently ask the model for a Google Test candidate, using the incident, logs, business rules and public C++ interface. It can abstain when a meaningful test cannot be expressed.
4. Save the results and metadata; compile generated C++ locally. A human reviews the candidate before separately executing it.

The pipeline uses Python, Pydantic, Ollama and C++20 with CMake and Google Test. The recorded runs use `qwen3.5:4b-16k` at temperature 0.3. The two model calls are independent; the test-generation call does not receive the triage. This is a workflow with two model calls, not a multi-agent system.

## Scenarios and observations

| Ticket | Scenario | What it evaluates | Observed result |
| --- | --- | --- | --- |
| 001 | An eligible replacement flight is rejected. | Can a generated test reproduce a defect? | A generated incident test failed against the intentionally defective engine when executed. An earlier generated suite contained contradictory assertions. |
| 002 | The search for alternatives times out. | Can the model avoid inventing a cause and recognize that a timeout cannot be tested through the supplied interface? | The examined runs classified the cause as `Unknown` and abstained from generating a test. |
| 003 | The requested original flight ID is unknown. | Can the model recognize that the interface cannot check a repository or report an unknown ID? | Earlier runs generated compilable but invalid tests. One run after a prompt revision correctly abstained, although its explanation still included an incorrect suggestion. |

Ticket 003 is a context and validation scenario: the ticket already says the unknown flight was reported. The evidence does not clearly establish whether an alternative search was attempted. It is not proof of a confirmed software defect.

The engine deliberately rejects flights with exactly two available seats. The logs show that a candidate was rejected but do not establish this exact cause. Human reference answers are kept in `data/references/` and are not supplied to the model.

## Key limitations

- The current C++ interface filters flights supplied by the caller. It cannot simulate a timeout or validate a flight ID against a repository.
- A valid JSON response or successful compilation does not prove that an analysis or test is correct. The source audit checks that references exist, not that they support a claim.
- Outputs vary between runs. Three tickets and a few runs demonstrate behavior; they do not measure reliability statistically.
- The prototype does not assign incidents to real teams, access production systems, automatically fix defects or deploy changes.

For setup, commands and artifact locations, see [README.md](README.md).
