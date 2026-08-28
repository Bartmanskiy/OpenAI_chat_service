PRICING = {
    "gpt-5.6": {
        "input": 4.0,
        "output": 20.0,
    }
}


def calculate_cost(
    model: str,
    input_tokens: int,
    output_tokens: int
) -> float:
    pricing = PRICING.get(model)

    if pricing is None:
        return 0.0

    input_cost = (input_tokens / 1_000_000) * pricing["input"]
    output_cost = (output_tokens / 1_000_000) * pricing["output"]

    return input_cost + output_cost