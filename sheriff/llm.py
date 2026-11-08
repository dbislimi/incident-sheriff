import time

from openai import OpenAI

from sheriff.utils import Result

MODEL_TEMPERATURE = 0.3


def print_token_usage(usage):
    if usage is None:
        print("Tokens : informations indisponibles.")
        return

    print("Tokens :")
    print(f"  Entrée : {usage.prompt_tokens}")
    print(f"  Sortie : {usage.completion_tokens}")
    print(f"  Total : {usage.total_tokens}")
    for label, details in (
        ("Entrée", usage.prompt_tokens_details),
        ("Sortie", usage.completion_tokens_details),
    ):
        if details is not None:
            for name, value in details.model_dump(exclude_none=True).items():
                print(f"  {label} / {name} : {value}")
    print()


def get_completion(
    client: OpenAI,
    model: str,
    system_prompt: str,
    user_prompt: str,
    format: type[Result],
    verbose: bool,
) -> Result:
    if not system_prompt or not user_prompt:
        raise ValueError("System or user prompt is empty.")

    if verbose:
        print("SYTEM_PROMPT:\n", system_prompt)
        print("USER_PROMPT:\n", user_prompt)

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]

    start_time = time.perf_counter()
    response = client.chat.completions.parse(
        messages=messages,
        model=model,
        temperature=MODEL_TEMPERATURE,
        response_format=format,
    )
    total_time = time.perf_counter() - start_time
    print(f"inference time: {total_time:.2f} s")

    if not response.choices or not response.choices[0].message.content:
        raise ValueError("Model returned an empty response.")

    result = response.choices[0].message.parsed
    if result is None:
        raise ValueError("Model response could not be parsed.")

    print_token_usage(response.usage)

    return result
