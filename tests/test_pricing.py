from app.services.pricing_service import calculate_cost, is_supported_model


def test_calculate_cost():
    cost = calculate_cost(
        model="gpt-5.6",
        input_tokens=1_000_000,
        output_tokens=1_000_000,
    )

    assert cost == 24.0


def test_calculate_cost_with_zero_tokens():
    cost = calculate_cost(
        model="gpt-5.6",
        input_tokens=0,
        output_tokens=0,
    )

    assert cost == 0.0


def test_unsupported_model_cost():
    cost = calculate_cost(
        model="unknown-model",
        input_tokens=1_000_000,
        output_tokens=1_000_000,
    )

    assert cost == 0.0


def test_supported_model():
    assert is_supported_model("gpt-5.6") is True


def test_unsupported_model():
    assert is_supported_model("unknown-model") is False