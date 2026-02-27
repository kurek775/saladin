"""Token usage telemetry and cost estimation."""

from dataclasses import dataclass, field

# Pricing per 1M tokens (input/output) as of 2025
MODEL_PRICING: dict[str, tuple[float, float]] = {
    # Anthropic
    "claude-sonnet-4-20250514": (3.0, 15.0),
    "claude-haiku-3-5-20241022": (0.80, 4.0),
    # OpenAI
    "gpt-4o": (2.50, 10.0),
    "gpt-4o-mini": (0.15, 0.60),
    # Google
    "gemini-2.0-flash": (0.10, 0.40),
    "gemini-1.5-pro": (1.25, 5.0),
}


@dataclass
class TokenUsage:
    model: str = ""
    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0
    estimated_cost_usd: float = 0.0


def estimate_cost(model: str, input_tokens: int, output_tokens: int) -> float:
    """Estimate cost in USD for given token usage."""
    pricing = MODEL_PRICING.get(model)
    if not pricing:
        # Try partial match
        for key, val in MODEL_PRICING.items():
            if key in model or model in key:
                pricing = val
                break

    if not pricing:
        return 0.0

    input_cost_per_m, output_cost_per_m = pricing
    cost = (input_tokens / 1_000_000) * input_cost_per_m + (output_tokens / 1_000_000) * output_cost_per_m
    return round(cost, 6)


def create_token_usage(model: str, input_tokens: int, output_tokens: int) -> TokenUsage:
    total = input_tokens + output_tokens
    cost = estimate_cost(model, input_tokens, output_tokens)
    return TokenUsage(
        model=model,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        total_tokens=total,
        estimated_cost_usd=cost,
    )
