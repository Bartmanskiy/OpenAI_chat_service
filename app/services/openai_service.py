from openai import OpenAI

from app.core.config import OPENAI_API_KEY


client = OpenAI(api_key=OPENAI_API_KEY)


def generate_response(model: str, messages: list):
    return client.responses.create(
        model=model,
        input=messages
    )


def get_usage(response):
    usage = response.usage

    return {
        "input_tokens": usage.input_tokens,
        "output_tokens": usage.output_tokens,
        "total_tokens": usage.total_tokens,
    }